import logging
from time import perf_counter, sleep
from kivy.utils import platform
is_android = platform == 'android'

from kivy.graphics import Color, Rectangle

logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

from functools import partial
from typing import List

import numpy as np
from kivy.core.window import Window

from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.properties import ObjectProperty, ListProperty, BooleanProperty, OptionProperty
from kivy.uix.stencilview import StencilView

if is_android:
    from camera2.camera2 import PyCameraInterface, PyCameraDevice

from permission_manager import PermissionsManager

class CameraControl(StencilView):
    best_resolution = "hd"
    standard_resolutions = {"hd": (1280, 720),
                            "fhd":(1920, 1080),
                            "4k": (3840, 2160)}
    preview = BooleanProperty(False)
    texture : Texture = ObjectProperty(None, allownone=True)
    resolution = ListProperty([1920, 1080])


    _display_rect : Rectangle = ObjectProperty(None, allownone=True)
    _rect_pos = ListProperty([0, 0])
    _rect_size = ListProperty([1, 1])
    _tex_coords = ListProperty([0.0, 0.0,   #u      v  (u, v) - position, (w, h) - size
                                1.0, 0.0,   #u + w  v
                                1.0, 1.0,   #u + w  v + h
                                0.0, 1.0])  #u      v + h
    mirrored = BooleanProperty(False)

    current_camera = ObjectProperty(None, allownone=True)
    camera_texture : Texture = ObjectProperty(None, allownone=True)
    if is_android:
        available_cameras : List[PyCameraDevice] = ListProperty()

    permission_state = OptionProperty(
        PermissionsManager.RequestStates.UNKNOWN,
        options=[PermissionsManager.RequestStates.UNKNOWN,
                 PermissionsManager.RequestStates.HAVE_PERMISSION,
                 PermissionsManager.RequestStates.DO_NOT_HAVE_PERMISSION,
                 PermissionsManager.RequestStates.AWAITING_REQUEST_RESPONSE])

    def __init__(self, **kwargs):
        super(CameraControl, self).__init__(**kwargs)
        self.start_time = perf_counter()
        self.fps_list = []
        self.FPS_FREQUENCY = 15 # Update fps counter every FPS_FREQUENCY frames

        #self._update_rect will be called if any of these properties change
        self.bind(pos=self._update_rect,
                  size=self._update_rect,
                  resolution=self._update_rect,
                  texture=self._update_rect,
                  mirrored=self._update_rect)
        self.register_event_type('on_update')

        if is_android:
            self.camera_interface = PyCameraInterface()
            self._load_cameras()

        # Update the layout as frequently as possible
        Clock.schedule_interval(self.update, 0)
        self.restart_camera()

    def update(self, *args):
        self.parent.canvas.ask_update()
        if not is_android and self.camera_texture is not None:
            self.camera_texture.ask_update(self.on_frame)

    def on_frame(self, *args):
        """
        Called each time new texture is received from the camera
        :param sender: Camera object that invoked the method
        :param texture: The most recent texture from the camera
        """
        if len(args) == 2:
            texture = args[1]
        else:
            texture = self.camera_texture

        self.update_fps()
        self.dispatch('on_update', texture)

    def on_update(self, texture):
        pass

    def update_fps(self):
        now = perf_counter()
        fps = 1/(now - self.start_time)
        self.start_time = now

        self.fps_list.append(fps)
        if len(self.fps_list) >= self.FPS_FREQUENCY:
            fps = sum(self.fps_list) / len(self.fps_list)
            self.fps_list.clear()
            fps = f"FPS: {fps:.2f}"
            self.parent.ids.fps.text = fps

    def change_camera(self):
        if not is_android:
            logger.error("Unable to change the camera on a PC")
            return
        logger.info("Changing the camera")
        """
        Alternate cameras
        """
        self.available_cameras = self.available_cameras[1:] + [self.available_cameras[0]]
        self.restart_camera()

    def change_resolution(self, new_resolution: str):
        if not is_android:
            logger.error("Unable to change resolution on a PC")
            return
        logger.info("Restarting the camera with the new resolution")
        """
        Restart the camera with new resolution
        :param new_resolution: must be in ("hd", "fhd", "4k")
        """
        assert new_resolution is self.standard_resolutions
        self.best_resolution = new_resolution
        self.restart_camera()


    ### Camera initialization methods ###
    #####################################

    def _load_cameras(self):
        """
        Initialize the list of available cameras.
        Cameras facing FRONT go to the beginning of the list as they have more priority
        """
        logger.info("Available cameras:")
        for camera in self.camera_interface.cameras:
            logger.info(f"Camera ID {camera.camera_id}, facing {camera.facing}, resolutions {camera.supported_resolutions}")
            if camera.facing == "BACK":
                self.available_cameras.append(camera)
            else:
                self.available_cameras.insert(0, camera)

    def restart_camera(self, *args):
        self.ensure_closed()
        Clock.schedule_once(self._restart_camera, 0)

    def _restart_camera(self, dt):
        logger.info(f"Restarting the camera. State {self.permission_state}")
        permitted_states = [PermissionsManager.RequestStates.UNKNOWN,
                            PermissionsManager.RequestStates.HAVE_PERMISSION]
        if self.permission_state in permitted_states:
            self.start_camera()
        else:
            logger.warning(f"Restarting failed due to camera state {self.permission_state}")

    def start_camera(self, camera_index=0):
        camera = self.available_cameras[camera_index] if is_android else None
        if PermissionsManager.check_request_permissions(partial(self._permissions_callback, camera)):
            self._start_camera(camera)

    def _permissions_callback(self, camera, requested_permissions, allowed_permissions):
        if np.all(allowed_permissions):
            self.permission_state = PermissionsManager.RequestStates.HAVE_PERMISSION
            self._start_camera(camera)
        else:
            self.permission_state = PermissionsManager.RequestStates.DO_NOT_HAVE_PERMISSION
            logger.error("PERMISSION FORBIDDEN :(")

    def _start_camera(self, camera):
        supported_resolutions = camera.supported_resolutions if is_android else [(1920, 1080)]
        resolution = self.get_best_resolution(Window.size, supported_resolutions)
        if resolution is None:
            logger.error(f"No good resolution found in {supported_resolutions} for window size {Window.size}")
            return
        logger.info(f"Selected resolution {resolution} from options {supported_resolutions}")
        self.resolution = resolution
        if is_android:
            camera.open(self._camera_callback)
        else:
            from kivy.uix.camera import Camera
            camera = Camera(index=1, resolution=self.resolution)
            self._camera_callback(camera, "OPENED")

    def _camera_callback(self, camera, action):
        if action == "OPENED":
            logger.info(f"Camera opened. Starting preview")
            Clock.schedule_once(partial(self._camera_preview_callback, camera), 0)
        else:
            logger.info(f"Camera event {action} is ignored")

    def _camera_preview_callback(self, camera, *args):
        logger.info("Starting camera preview")

        if is_android:
            self.camera_texture = camera.start_preview(tuple(self.resolution))
            camera.bind(on_frame=self.on_frame)
            self.mirrored = camera.facing == "FRONT"
        else:
            while camera.texture is None:
                logger.error("Texture unavailable")
                sleep(0.1)
            self.camera_texture = camera.texture
            camera.bind(on_texture=self.on_frame)

        if self.preview:
            self.texture = self.camera_texture

        self.current_camera = camera
        self.current_camera.bind(on_texture=self.on_frame)

    def ensure_closed(self):
        if self.current_camera is not None:
            if is_android:
                self.current_camera.close()
            else:
                self.current_camera.on_play(self, False)
            self.current_camera = None


    #### Correct texture display methods####
    ########################################
    def _mirror(self):
        if is_android:
            if self.mirrored:
                logger.info("Using front camera. Therefore, mirroring the texture")
                p = (1., 0.) # Position. shifted all over to the right side
                s = (-1., 1.) # Size. full size, flipped along width (mirrored)
            else:
                p = (0., 0.) # Position.
                s = (1., 1.) # Size. full size
        else:
            p = (0, 1)
            s = (1, -1)

        self._tex_coords = [p[0],       p[1],
                            p[0] + s[0],p[1],
                            p[0] + s[0],p[1] + s[1],
                            p[0],       p[1] + s[1]]

        if self._display_rect is None or self._display_rect.tex_coords != self._tex_coords:
            self._display_rect = Rectangle(texture=self.texture, pos=self._rect_pos, size=self._rect_size, tex_coords=self._tex_coords)
            if self._display_rect in self.canvas.children:
                self.canvas.remove(self._display_rect)
            self.canvas.add(self._display_rect)


    def _update_rect(self, *args, fill=True):
        logger.info("Updating output rectangle")

        w, h = self.resolution
        aspect_width = self.width
        aspect_height = self.width * h / w

        if (aspect_height < self.height) if fill else (aspect_height > self.height):
            aspect_height = self.height
            aspect_width = aspect_height * w / h

        aspect_height = int(aspect_height)
        aspect_width = int(aspect_width)

        self._rect_pos = [self.center_x - aspect_width / 2,
                          self.center_y - aspect_height / 2]

        self._rect_size = [aspect_width, aspect_height]
        self._mirror()


    def get_best_resolution(self, window_size, resolutions, best=None):
        best = self.standard_resolutions[self.best_resolution] if best is None else best
        logger.info(f"Assuming the best resolution is {best}")
        if best in resolutions:
            return best

        if not resolutions:
            return None

        win_x, win_y = window_size
        larger_resolutions = [(x, y) for (x, y) in resolutions if (x > win_x and y > win_y)]

        if larger_resolutions:
            return min(larger_resolutions, key=lambda r: r[0] * r[1])

        smaller_resolutions = resolutions  # if we didn't find one yet, all are smaller than the requested Window size
        return max(smaller_resolutions, key=lambda r: r[0] * r[1])