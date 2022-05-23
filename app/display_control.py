from logging_utils import get_logger
logger = get_logger(__name__)

from camera import Camera, DeviceCamera

from kivy.clock import Clock, mainthread
from kivy.graphics import Rectangle
from kivy.graphics.texture import Texture
from kivy.properties import ObjectProperty, ListProperty, BooleanProperty
from kivy.uix.stencilview import StencilView

class DisplayControl(StencilView):
    preview = BooleanProperty(False)
    _texture : Texture = ObjectProperty(None, allownone=True)
    resolution = ListProperty([1920, 1080])
    preferred_resolution = ListProperty([1280, 720])


    _display_rect : Rectangle = ObjectProperty(None, allownone=True)
    _rect_pos = ListProperty([0, 0])
    _rect_size = ListProperty([1, 1])
    _tex_coords = ListProperty([])

    camera : Camera = ObjectProperty(None, allownone=True)

    ### Camera initialization methods ###
    #####################################

    def __init__(self, **kwargs):
        super(DisplayControl, self).__init__(**kwargs)

        #self._update_rect will be called if any of these properties change
        self.pixels = None
        self.bind(pos=self._update_rect,
                  size=self._update_rect,
                  resolution=self._update_rect,
                  _texture=self._update_rect)
        self.register_event_type('on_update')
        self.update_event = None

    def initialize_camera(self, *args):
        self.close()
        self.camera = DeviceCamera()

        self.camera.preferred_resolution = self.preferred_resolution

        self.camera.bind(on_started=self._start_camera)
        self.camera.restart()

    def _start_camera(self, *args):
        self.camera.bind(on_update=self.on_frame)
        self.camera.bind(on_fps=self.update_fps)

        self._tex_coords = self.camera.suggested_tex_coords
        self._texture = self.camera.texture if self.preview else None
        self.resolution = self.camera.resolution
        self.update_event = Clock.schedule_interval(self.update, 0)
        logger.debug("Camera Update Event scheduled")

    def close(self):
        if self.update_event is not None:
            self.update_event.cancel()
        if self.camera is not None:
            self.camera.close()
            self.camera.unbind(on_update=self.on_frame)
            self.camera.unbind(on_fps=self.update_fps)
            self.camera.unbind(on_started=self._start_camera)
            self.camera = None

    #### Main functionality ####
    ############################

    def update(self, *args):
        self.parent.canvas.ask_update()

    def on_update(self, *args):
        pass

    def on_frame(self, sender, texture, *args):
        self.dispatch("on_update", texture)

    def update_fps(self, sender, new_value:float, *args):
        self.parent.ids.fps.text = f"FPS: {new_value:.2f}"

    def change_camera(self):
        self.camera.change_camera()

    def change_resolution(self, new_resolution):
        self.camera.change_resolution(new_resolution)


    #### Correct texture display methods####
    ########################################
    def display(self, pixels, shape, format="rgb"):
        if self._texture is None or self._texture.size != shape or self._texture.colorfmt != format:
            self._texture = Texture.create(size=shape, colorfmt=format)
            logger.debug(f"Output texture of size {self._texture.size} created")

        self.pixels = pixels
        self.__draw()

    @mainthread
    def __draw(self):
        if self.pixels:
            self._texture.blit_buffer(self.pixels, colorfmt='rgb')
            logger.debug("Image drawn")

    def _update_rect(self, *args, fill=True):
        logger.debug("Updating output rectangle")

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

        if self._display_rect is None \
                or self._display_rect.texture != self._texture \
                or self._display_rect.tex_coords != tuple(self._tex_coords) \
                or self._display_rect.pos != tuple(self._rect_pos) \
                or self._display_rect.size != tuple(self._rect_size):

            if self._display_rect in self.canvas.children:
                self.canvas.remove(self._display_rect)

            self._display_rect = Rectangle(texture=self._texture, pos=self._rect_pos, size=self._rect_size, tex_coords=self._tex_coords)

            self.canvas.add(self._display_rect)