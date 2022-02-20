from logging_utils import get_logger
logger = get_logger(__name__)

from time import perf_counter
from typing import Tuple

from kivy.core.window import Window
from kivy.graphics.texture import Texture
from kivy.properties import ObjectProperty, ListProperty, NumericProperty
from kivy.event import EventDispatcher


class Camera(EventDispatcher):
    texture : Texture = ObjectProperty(None, allownone=True)
    suggested_tex_coords = ListProperty([0., 1.,    #u      v       (u, v) - position, (w, h) - size
                                         1., 1.,    #u + w  v
                                         1., 0.,    #u + w  v + h
                                         0., 0.])   #u      v + h
    resolution = ListProperty([1920, 1080])
    supported_resolutions = ListProperty([(1920, 1080)])
    best_resolution = ListProperty([1920, 1080])

    _camera = ObjectProperty(None, allownone=True)

    FPS_FREQUENCY = NumericProperty(15) # Update FPS Counter every 15 frames
    __fps_list = ListProperty([])
    __start_time = perf_counter()

    def __init__(self, *args, **kwargs):
        super(Camera, self).__init__(*args, **kwargs)

        self.register_event_type('on_update')
        self.register_event_type('on_fps')
        self.register_event_type('on_started')

    def __del__(self):
        self.close()

    def update(self, *args):
        self.texture.ask_update(self.on_tex)

    def on_update(self, texture):
        """
        Invoked every new frame
        """
        pass

    def on_fps(self, fps:float):
        """
        Invoked when new FPS value is available
        :param fps: new FPS value
        """
        pass

    def on_started(self):
        """
        Invoked when camera initialization is completed
        """
        pass

    def close(self):
        pass

    def restart(self, *args):
        self.close()
        pass

    def on_tex(self, sender):
        """
        Called each time new _texture is received from the camera
        """
        self.update_fps()
        self.dispatch('on_update', self.texture)

    def update_fps(self):
        now = perf_counter()
        fps = 1 / (now - self.__start_time)
        self.__start_time = now

        self.__fps_list.append(fps)
        if len(self.__fps_list) >= self.FPS_FREQUENCY:
            fps = sum(self.__fps_list) / len(self.__fps_list)
            self.__fps_list.clear()
            self.dispatch("on_fps", fps)

    def change_resolution(self, new_resolution:Tuple[int, int]):
        """
        Restart the camera with new resolution
        """
        pass
    def change_camera(self):
        """
        Alternate cameras
        """
        pass

    def set_best_available_resolution(self, window_size=Window.size) -> None:
        logger.info(f"Assuming the best resolution is {self.best_resolution}")
        assert self.supported_resolutions, "List of supported resolutions is empty"

        if self.best_resolution in self.supported_resolutions:
            self.resolution = self.best_resolution
            return

        win_x, win_y = window_size
        larger_resolutions = [(x, y) for (x, y) in self.supported_resolutions if (x > win_x and y > win_y)]

        if larger_resolutions:
            self.resolution = min(larger_resolutions, key=lambda r: r[0] * r[1])
            return

        smaller_resolutions = self.supported_resolutions  # if we didn't find one yet, all are smaller than the requested Window size
        self.resolution = max(smaller_resolutions, key=lambda r: r[0] * r[1])

    def set_suggested_tex_coords(self, p, s):
        """
        Sets suggested_tex_coords based on p and s
        :param p: Texture position
        :param s: Texture size
        """

        self.suggested_tex_coords =[p[0],       p[1],
                                    p[0] + s[0],p[1],
                                    p[0] + s[0],p[1] + s[1],
                                    p[0],       p[1] + s[1]]