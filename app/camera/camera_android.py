from logging_utils import get_logger
logger = get_logger(__name__)

from functools import partial
from typing import List, Tuple
import numpy as np

from kivy.properties import ListProperty, OptionProperty
from kivy.clock import mainthread

from camera import Camera, PyCameraDevice, PyCameraInterface, PermissionsManager

class CameraAndroid(Camera):
    _camera : PyCameraDevice
    _available_cameras : List[PyCameraDevice] = ListProperty()

    _permission_state = OptionProperty(
        PermissionsManager.RequestStates.UNKNOWN,
        options=[PermissionsManager.RequestStates.UNKNOWN,
                 PermissionsManager.RequestStates.HAVE_PERMISSION,
                 PermissionsManager.RequestStates.DO_NOT_HAVE_PERMISSION,
                 PermissionsManager.RequestStates.AWAITING_REQUEST_RESPONSE])

    def __init__(self, *args, **kwargs):
        super(CameraAndroid, self).__init__(*args, **kwargs)

        self.camera_interface = PyCameraInterface()
        self._load_cameras()

    def _load_cameras(self):
        """
        Initialize the list of available cameras.
        Cameras facing FRONT go to the beginning of the list as they have more priority
        """
        logger.debug("Available cameras:")
        for camera in self.camera_interface.cameras:
            logger.debug(f"Camera ID {camera.camera_id}, facing {camera.facing}, resolutions {camera.supported_resolutions}")
            if camera.facing == "BACK":
                self._available_cameras.append(camera)
            else:
                self._available_cameras.insert(0, camera)

    def close(self):
        if self._camera is not None:
            self._camera.unbind(on_frame=self.update)
            self._camera.close()
            self._camera = None
            logger.debug("Camera closed")

    def restart(self, *args):
        self.close()
        logger.debug(f"Restarting the camera. State {self._permission_state}")

        permitted_states = [PermissionsManager.RequestStates.UNKNOWN,
                            PermissionsManager.RequestStates.HAVE_PERMISSION]
        if self._permission_state not in permitted_states:
            logger.error(f"Restarting failed due to camera state {self._permission_state}")
            return

        self._camera = self._available_cameras[0]
        if PermissionsManager.check_request_permissions(partial(self._permissions_callback, self._camera)):
            self._start_camera()

    def _permissions_callback(self, camera, requested_permissions, allowed_permissions):
        if not np.all(allowed_permissions):
            self._permission_state = PermissionsManager.RequestStates.DO_NOT_HAVE_PERMISSION
            logger.error("PERMISSION FORBIDDEN :(")
            return

        self._permission_state = PermissionsManager.RequestStates.HAVE_PERMISSION
        self._start_camera()

    def _start_camera(self):
        self.supported_resolutions = self._camera.supported_resolutions
        self.set_best_available_resolution()
        self._camera.open(self._camera_opened)

    @mainthread
    def _camera_opened(self, camera, action:str):
        if action != "OPENED":
            logger.debug(f"Camera event {action} is ignored")
            return
        logger.debug("Camera opened")

        logger.debug("Starting camera preview")
        self.texture = self._camera.start_preview(self.resolution)
        if self._camera.facing == "FRONT":
            p = (1., 0.)
            s = (-1., 1.)
        else:
            p = (0., 0.)
            s = (1., 1.)

        self.set_suggested_tex_coords(p, s)

        self._camera.bind(on_frame=self.update)
        self.dispatch("on_started")

    def change_camera(self):
        logger.info("Changing the camera")
        self._available_cameras = self._available_cameras[1:] + [self._available_cameras[0]]
        self.restart()

    def change_resolution(self, new_resolution:Tuple[int, int]):
        logger.info(f"Restarting the camera with the new resolution {new_resolution}")
        assert new_resolution in self.supported_resolutions
        self.preferred_resolution = new_resolution
        self.restart()