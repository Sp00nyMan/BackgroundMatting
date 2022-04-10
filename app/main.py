import requests

from logging_utils import get_logger
logger = get_logger(__name__)

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty, BooleanProperty

from display_control import DisplayControl
from model import Model
from layout import AppLayout

# CODE:
# TODO: Texture output on Inference. The problem might be due to different values for resolution in camera and display_control
# TODO: Keep the resolution after switching to inference mode
# TODO: Optimize postprocessing time

# Functionality
# TODO: Replace background. Load an image from gallery
# TODO: Async request processing to avoid freezing while waiting for response

class MattingApp(App):
    preview = BooleanProperty(True)
    display_control : DisplayControl = ObjectProperty(None)

    model: Model = ObjectProperty(None, allownone=True)

    def build(self):
        Builder.load_file('layout.kv')
        root = AppLayout()
        return root

    def update(self, sender, texture):
        if self.model is None or not self.model.initialized:
            return

        pixels = self.model.process(texture.pixels, texture.size)

        self.display_control.display(pixels, texture.size)

    def toggle_preview(self, toggle=True):
        if toggle:
            preview = not self.preview
        else:
            preview = self.preview

        if not preview:
            try:
                self.model = Model()
            except requests.HTTPError as error:
                logger.exception("Server cannot be reached...")
                return
            self.display_control.bind(on_update=self.update)
        else:
            self.model = None
            self.display_control.unbind(on_update=self.update)

        self.preview = preview
        self.display_control.preview = self.preview
        if toggle:
            self.display_control.initialize_camera()

    def on_start(self):
        self.display_control = self.root.ids.cdw
        self.toggle_preview(False)

    def on_stop(self): #TODO Correct closing. Sometimes this method is not called
        self.display_control.close()
        logger.info("Application closed successfully!")
        return super().on_stop()

    def on_pause(self):
        logger.info("Closing camera because of pause")
        self.display_control.close()
        return super().on_pause()

    def on_resume(self):
        logger.info("Restarting camera owing to resume")
        self.display_control.initialize_camera()

if __name__ == '__main__':
    MattingApp().run()