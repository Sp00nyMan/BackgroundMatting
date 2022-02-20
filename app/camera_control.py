from logging_utils import get_logger
logger = get_logger(__name__)

from camera import Camera, DeviceCamera

from kivy.clock import Clock
from kivy.graphics import Rectangle
from kivy.graphics.texture import Texture
from kivy.properties import ObjectProperty, ListProperty, BooleanProperty
from kivy.uix.stencilview import StencilView

class CameraControl(StencilView):
    best_resolution = "hd"
    standard_resolutions = {"hd": (1280, 720),
                            "fhd":(1920, 1080),
                            "4k": (3840, 2160)}

    preview = BooleanProperty(False)
    _texture : Texture = ObjectProperty(None, allownone=True)
    resolution = ListProperty([1920, 1080])


    _display_rect : Rectangle = ObjectProperty(None, allownone=True)
    _rect_pos = ListProperty([0, 0])
    _rect_size = ListProperty([1, 1])
    _tex_coords = ListProperty([0.0, 0.0,   #u      v  (u, v) - position, (w, h) - size
                                1.0, 0.0,   #u + w  v
                                1.0, 1.0,   #u + w  v + h
                                0.0, 1.0])  #u      v + h

    camera : Camera = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super(CameraControl, self).__init__(**kwargs)

        #self._update_rect will be called if any of these properties change
        self.bind(pos=self._update_rect,
                  size=self._update_rect,
                  resolution=self._update_rect,
                  _texture=self._update_rect)
        self.register_event_type('on_update')
        self.initialize_camera()

        self.update_event = Clock.schedule_interval(self.update, 0)

    def update(self, *args):
        self.parent.canvas.ask_update()

    def on_update(self, *args):
        pass

    def on_frame(self, sender, texture, *args):
        self.dispatch("on_update", texture)

    def update_fps(self, sender, new_value:float, *args):
        self.parent.ids.fps.text = f"FPS: {new_value:.2f}"

    ### Camera initialization methods ###
    #####################################

    def initialize_camera(self, *args):
        self.camera = DeviceCamera()

        self.camera.best_resolution = self.standard_resolutions[self.best_resolution]

        self.camera.bind(on_update=self.on_frame)
        self.camera.bind(on_fps=self.update_fps)
        self.camera.bind(on_started=self._start_camera)

        self.camera.restart()

    def _start_camera(self, *args):
        self._tex_coords = self.camera.suggested_tex_coords
        self._texture = self.camera.texture
        self.resolution = self.camera.resolution

    def close(self):
        if self.update_event is not None:
            self.update_event.cancel()
        if self.camera is not None:
            self.camera.close()
            self.camera = None


    #### Correct texture display methods####
    ########################################
    def display(self, pixels, shape, format="RGB"):
        if self._texture is None or self._texture.size != shape or self._texture.colorfmt != format:
            self._texture = Texture.create(size=shape, colorfmt=format)
            logger.info(f"Output texture of size {self._texture.size} created")

        self._texture.blit_buffer(pixels)

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

        if self._display_rect is None or self._display_rect.tex_coords != self._tex_coords:
            self._display_rect = Rectangle(texture=self._texture, pos=self._rect_pos, size=self._rect_size,
                                           tex_coords=self._tex_coords)
            if self._display_rect in self.canvas.children:
                self.canvas.remove(self._display_rect)
            self.canvas.add(self._display_rect)