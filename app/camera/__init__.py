from kivy.utils import platform

from .camera import Camera

if platform == 'android':
    from .camera_android import CameraAndroid as DeviceCamera
else:
    from .camera_cv import CameraCV as DeviceCamera
