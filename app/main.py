from time import perf_counter
import logging
logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.graphics.texture import Texture

from kivy.config import Config
Config.set('modules', 'monitor', '')
Config.set('modules', 'showborder', '')

from camera_control import CameraControl
from model_base import Model
from layout import AppLayout

# TODO: Correct mirroring

# TODO: Custom FPS tracker
# TODO: Replace background
# TODO: Async request processing to avoid freezing while waiting for response

class MattingApp(App):
    preview = BooleanProperty(True)
    camera_control : CameraControl = ObjectProperty(None)

    model: Model = ObjectProperty()

    start_time = perf_counter()

    def build(self):
        Builder.load_file('layout.kv')
        root = AppLayout()
        return root

    def update(self, sender, texture):
        if not self.model.initialized:
            return

        pixels = self.model.process(texture.pixels, texture.size)

        if self.camera_control.texture is None or self.camera_control.texture.size != texture.size or self.camera_control.texture.colorfmt != 'RGB':
            self.camera_control.texture = Texture.create(size=texture.size, bufferfmt=texture.bufferfmt, colorfmt='RGB')
            logger.info(f"Output texture of size {self.camera_control.texture.size} created")

        self.camera_control.texture.blit_buffer(pixels)

    def on_start(self):
        self.camera_control = self.root.ids.cdw
        self.camera_control.preview = self.preview
        if not self.preview:
            self.camera_control.bind(on_update=self.update)
            self.model = Model()

    def on_stop(self): #TODO Correct closing. Sometimes this method is not called
        self.camera_control.ensure_closed()
        logger.info("Application closed successfully!")
        return super().on_stop()

    def on_pause(self):
        logger.info("Closing camera because of pause")
        self.camera_control.ensure_closed()
        return super().on_pause()

    def on_resume(self): #TODO Wrong mirroring after resuming. Rectangle depends on root._tex_coords. Figure out what it is and why it doesn't change
        logger.info("Restarting camera owing to resume")
        self.camera_control.restart_camera()

if __name__ == '__main__':
    MattingApp().run()