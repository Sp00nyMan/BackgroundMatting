from kivy.utils import platform

from .camera import Camera

if platform == 'android':
    from .camera2 import PyCameraDevice, PyCameraInterface
    from .permission_manager import PermissionsManager
    from .camera_android import CameraAndroid as DeviceCamera
else:
    from .camera_cv import CameraCV as DeviceCamera
