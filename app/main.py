from logging_utils import get_logger, message_handler
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
        message_handler.setStream(root.ids.msg)
        return root

    def update(self, sender, texture):
        if self.model is None or not self.model.initialized:
            return

        pixels = self.model.process(texture.pixels, texture.size)

        self.display_control.display(pixels, texture.size)

    def toggle_preview(self):
        if self.model is not None:
            self.model.interrupt_initialization()

        if self.preview:
            self.model = Model()
            self.model.bind(on_initialized=self.on_model_initialized)
            self.model.initialize()
        else:
            self.model = None
            self.display_control.unbind(on_update=self.update)
            self.preview = True
            self.__restart_display()

    def on_model_initialized(self, *args):
        self.preview = False
        self.__restart_display()
        self.display_control.bind(on_update=self.update)

    def action(self, *args):
        from encoder import Encoding
        pixels = self.display_control._texture.pixels
        Encoding.json_from_bytes(pixels, self.display_control.resolution)

    def __restart_display(self):
        logger.debug("Restarting display")
        self.display_control.preview = self.preview
        self.display_control.initialize_camera()

    def on_start(self):
        self.display_control = self.root.ids.cdw
        self.__restart_display()

    def on_stop(self): #TODO Correct closing. Sometimes this method is not called
        if self.model:
            self.model.interrupt_initialization()
        self.display_control.close()
        logger.debug("Application closed successfully!")
        return super().on_stop()

    def on_pause(self):
        logger.debug("Closing camera because of pause")
        self.display_control.close()
        return super().on_pause()

    def on_resume(self):
        logger.debug("Restarting camera owing to resume")
        self.display_control.initialize_camera()

if __name__ == '__main__':
    MattingApp().run()