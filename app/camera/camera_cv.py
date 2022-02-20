from logging_utils import get_logger
logger = get_logger(__name__)

from typing import Tuple

from kivy.core.camera.camera_opencv import CameraOpenCV

from camera import Camera


class CameraCV(Camera):
    _camera : CameraOpenCV
    def __init__(self, *args, **kwargs):
        super(CameraCV, self).__init__(*args, **kwargs)

    def close(self):
        self._camera.stop()
        logger.info("Camera has been closed")

    def restart(self, *args):
        self.set_best_available_resolution()
        self._camera = CameraOpenCV(resolution=self.resolution, stopped=True)
        self._camera.bind(on_load=self._camera_opened)
        self._camera.start()

    def _camera_opened(self, *args):
        logger.info("Camera opened")
        self.texture = self._camera.texture

        p = (0., 1.)
        s = (1., -1.)
        self.set_suggested_tex_coords(p, s)

        self._camera.bind(on_texture=self.update)
        self.dispatch("on_started")

    def change_camera(self):
        raise NotImplementedError()

    def change_resolution(self, new_resolution:Tuple[int, int]):
        raise NotImplementedError()