from time import perf_counter

import numpy as np
from camera4kivy import Preview
from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.graphics.texture import Texture

from kivy.utils import platform
from kivy.clock import mainthread

from model_base import Model

class PermissionsManager:
    @staticmethod
    def is_android():
        return platform == 'android'

    @staticmethod
    def check_permissions():
        """
        Android runtime `CAMERA` permission check.
        """
        if not PermissionsManager.is_android():
            return True
        from android.permissions import Permission, check_permission
        return check_permission(Permission.CAMERA) and check_permission(Permission.INTERNET)

    @staticmethod
    def check_request_permissions(callback=None):
        """
        Android runtime `CAMERA` permission check & request.
        """
        had_permission = PermissionsManager.check_permissions()
        if not had_permission:
            from android.permissions import Permission, request_permissions
            permissions = [Permission.CAMERA, Permission.INTERNET]
            request_permissions(permissions, callback)
        return had_permission

#TODO: Migrate to kivy.core.camera.Camera
class CameraControl(Preview):
    def __init__(self, **kwargs):
        super().__init__(orientation='portrait')
        self._on_index()
        self.model = Model(mode='online')
        self.start_time = perf_counter()
        self.mask :Texture = None

    def _on_index(self):
        @mainthread
        def on_permissions_callback(permissions, grant_results):
            if all(grant_results):
                self._on_camera_ready()

        if PermissionsManager.check_request_permissions(callback=on_permissions_callback):
            self._on_camera_ready()

    def _on_camera_ready(self):
        self.connect_camera(camera_id='front')
        print('Camera connected')

    def canvas_instructions_callback(self, texture: Texture, tex_size, tex_pos):

        start = perf_counter()
        size = texture.size
        try:
            image = self.model.process(texture.pixels, (size[1], size[0]))
        except Exception as e:
            print(f'Error: {e}')
            App.get_running_app().stop()
            raise

        print(f"Inference: {perf_counter() - start:.4}\n\n\n")

        if not self.mask or self.mask.size[:2] != size:
            self.mask: Texture = Texture.create(size=size, colorfmt='rgb')
            self.mask.flip_vertical()
        self.mask.blit_buffer(image)

        with self.canvas:
            Color(1, 1, 1, 1)
            Rectangle(texture=self.mask, size=np.abs(tex_size))
