# main.py
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.dialog import MDDialog
from kivymd.uix.progressbar import MDProgressBar
from kivy.clock import Clock
from moviepy.editor import VideoFileClip
import os
import threading

Window.size = (400, 600)  # Set window size for desktop preview

class HomeScreen(Screen):
    pass

class ConverterApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_manager = MDFileManager(exit_manager=self.exit_manager, select_path=self.select_path, ext=[".mp4", ".avi", ".mov", ".mkv"])
        self.selected_file = ""
        self.output_directory = ""
        self.output_format = "mp3"
        self.dialog = None
        self.progress_bar = None
        self.progress_value = 0

    def build(self):
        self.title = "Video to Audio Converter"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        Builder.load_file('main.kv')
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        return sm

    def show_file_manager(self):
        self.file_manager.show(os.path.expanduser("~"))  # Open file manager at the home directory

    def exit_manager(self, *args):
        self.file_manager.close()

    def select_path(self, path):
        if self.selected_file:
            # If a file was already selected, set the output directory
            self.output_directory = path
            self.file_manager.close()
            self.start_conversion()
        else:
            # Select the video file
            self.selected_file = path
            self.file_manager.close()
            self.show_output_directory_dialog()

    def show_output_directory_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Select Output Directory",
                text="Choose the location where the audio file will be saved.",
                buttons=[
                    MDRaisedButton(text="Select", on_release=lambda x: self.close_dialog_and_show_file_manager())
                ]
            )
        self.dialog.open()

    def close_dialog_and_show_file_manager(self):
        if self.dialog:
            self.dialog.dismiss()  # Close the dialog
        self.show_file_manager()

    def start_conversion(self):
        self.root.get_screen('home').ids.progress_label.text = "Progress: Starting..."
        self.progress_bar = MDProgressBar(value=0, max=100, color=(0, 0.5, 1, 1))
        self.root.get_screen('home').ids.layout.add_widget(self.progress_bar)
        threading.Thread(target=self.convert_to_audio).start()
        Clock.schedule_interval(self.update_progress, 0.5)

    def convert_to_audio(self):
        try:
            video = VideoFileClip(self.selected_file)
            output_path = (self.output_directory or os.path.dirname(self.selected_file)) + \
                          f"/{os.path.splitext(os.path.basename(self.selected_file))[0]}.{self.output_format}"
            video.audio.write_audiofile(output_path, logger=None, verbose=False)
            Clock.schedule_once(lambda dt: self.show_success_dialog(output_path))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.show_error_dialog(str(e)))
        finally:
            Clock.schedule_once(lambda dt: self.remove_progress_bar())

    def update_progress(self, dt):
        if self.progress_bar:
            if self.progress_bar.value < 100:
                self.progress_bar.value += 10
                self.root.get_screen('home').ids.progress_label.text = f"Progress: {int(self.progress_bar.value)}%"
            else:
                self.root.get_screen('home').ids.progress_label.text = "Progress: Completed"
                Clock.unschedule(self.update_progress)

    def remove_progress_bar(self):
        if self.progress_bar:
            self.root.get_screen('home').ids.layout.remove_widget(self.progress_bar)
            self.progress_bar = None

    def show_success_dialog(self, output_path):
        success_dialog = MDDialog(
            title="Conversion Successful",
            text=f"Audio saved as: {output_path}",
            buttons=[MDRaisedButton(text="OK", on_release=lambda x: success_dialog.dismiss())]
        )
        success_dialog.open()

    def show_error_dialog(self, error_message):
        error_dialog = MDDialog(
            title="Error",
            text=f"An error occurred: {error_message}",
            buttons=[MDRaisedButton(text="OK", on_release=lambda x: error_dialog.dismiss())]
        )
        error_dialog.open()

if __name__ == "__main__":
    ConverterApp().run()

