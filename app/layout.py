from typing import List

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
    _buttons_visible_fraction = NumericProperty(1.)
    supported_resolutions : List[str] = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def change_camera(self):
        self.ids.cdw.change_camera()

    def change_resolution(self):
        current_resolution = self.ids.button_resolution.text.lower()
        resolution_id = self.supported_resolutions.index(current_resolution)
        if resolution_id + 1 < len(self.supported_resolutions):
            resolution_id += 1
        else:
            resolution_id = 0

        new_resolution = self.supported_resolutions[resolution_id]
        if current_resolution != new_resolution:
            self.ids.button_resolution.text = new_resolution.upper()
            self.ids.cdw.change_resolution(new_resolution)