from logging_utils import get_logger
logger = get_logger(__name__)

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.config import Config
Config.set('modules', 'monitor', '')
Config.set('modules', 'showborder', '')

from camera_control import CameraControl
from model_base import Model
from layout import AppLayout

# CODE:
# TODO: PC Texture output on Inference
# TODO: Optimize postprocessing time

# Functionality
# TODO: Replace background. Load an image from gallery
# TODO: Async request processing to avoid freezing while waiting for response

class MattingApp(App):
    preview = BooleanProperty(True)
    camera_control : CameraControl = ObjectProperty(None)

    model: Model = ObjectProperty(None, allownone=True)

    def build(self):
        Builder.load_file('layout.kv')
        root = AppLayout()
        return root

    def update(self, sender, texture):
        if self.model is None or not self.model.initialized:
            return

        pixels = self.model.process(texture.pixels, texture.size)

        self.camera_control.display(pixels, texture.size)

    def toggle_preview(self, toggle=True):
        if toggle:
            self.preview = not self.preview

        self.camera_control.preview = self.preview
        if toggle:
            self.camera_control.initialize_camera()

        if self.preview:
            self.model = None
            self.camera_control.unbind(on_update=self.update)
        else:
            self.camera_control.bind(on_update=self.update)
            self.model = Model()

    def on_start(self):
        self.camera_control = self.root.ids.cdw
        self.toggle_preview(False)

    def on_stop(self): #TODO Correct closing. Sometimes this method is not called
        self.camera_control.close()
        logger.info("Application closed successfully!")
        return super().on_stop()

    def on_pause(self):
        logger.info("Closing camera because of pause")
        self.camera_control.close()
        return super().on_pause()

    def on_resume(self):
        logger.info("Restarting camera owing to resume")
        self.camera_control.initialize_camera()

if __name__ == '__main__':
    MattingApp().run()