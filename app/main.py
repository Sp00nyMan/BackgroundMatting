from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.utils import platform
from kivy.core.window import Window

from kivy.config import Config

from camera_control import CameraControl

Config.set('modules', 'monitor', '')
Config.set('modules', 'showborder', '')

if platform == 'android':
    from jnius import autoclass
    from android.runnable import run_on_ui_thread
    from android import mActivity
    View = autoclass('android.view.View')

    @run_on_ui_thread
    def hide_landscape_status_bar(instance, width, height):
        # width,height gives false layout events, on pinch/spread
        # so use Window.width and Window.height
        if Window.width > Window.height:
            # Hide status bar
            option = View.SYSTEM_UI_FLAG_FULLSCREEN
        else:
            # Show status bar
            option = View.SYSTEM_UI_FLAG_VISIBLE
        mActivity.getWindow().getDecorView().setSystemUiVisibility(option)
else:
    # Dispose of that nasty red dot, required for gestures4kivy.
    from kivy.config import Config
    Config.set('input', 'mouse', 'mouse, disable_multitouch')

class MattingApp(App):

    def build(self):
        if platform == 'android':
            Window.bind(on_resize=hide_landscape_status_bar)
        return AppLayout()

    def on_start(self):
        pass

    def on_stop(self):
        self.root.ids.control.disconnect_camera()

class AppLayout(FloatLayout):
    camera_control = ObjectProperty()

Builder.load_string("""
<AppLayout>:
    camera_control: self.ids.control
    CameraControl:
        id: control
        aspect_ratio: '16:9'
""")

if __name__ == '__main__':
    MattingApp().run()
