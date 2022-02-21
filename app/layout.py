from logging_utils import get_logger
logger = get_logger(__name__)

from kivy.metrics import dp
from kivy.properties import NumericProperty, ListProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label

class ColouredButton(ButtonBehavior, Label):
    background_normal = ListProperty([1, 1, 1, 1])
    background_down = ListProperty([0.5, 0.5, 0.5, 1])
    padding = NumericProperty(dp(2))
    radius = NumericProperty(dp(5))

class AppLayout(FloatLayout):
    starting_resolution = "hd"
    standard_resolutions = {"hd": (1280, 720),
                            "fhd":(1920, 1080),
                            "4k": (3840, 2160)}
    _buttons_visible_fraction = NumericProperty(1.)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        from kivy.utils import platform
        if platform != 'android':
            logger.info("Hiding unused buttons")
            self.ids.buttons_dropdown.remove_widget(self.ids.button_resolution)
            self.ids.buttons_dropdown.remove_widget(self.ids.button_change)
        self.ids.cdw.preferred_resolution = self.standard_resolutions[self.starting_resolution]

    def change_camera(self):
        logger.info("Switching to different camera")
        self.ids.cdw.change_camera()

    def change_resolution(self):
        current_resolution = self.ids.button_resolution.text.lower()
        supported_resolutions = list(self.standard_resolutions.keys())
        resolution_id = supported_resolutions.index(current_resolution)
        if resolution_id + 1 < len(self.standard_resolutions):
            resolution_id += 1
        else:
            resolution_id = 0

        new_resolution = supported_resolutions[resolution_id]
        if current_resolution != new_resolution:
            logger.info(f"Switching to {new_resolution}")
            self.ids.button_resolution.text = new_resolution.upper()
            new_resolution = self.standard_resolutions[new_resolution]
            self.ids.cdw.change_resolution(new_resolution)