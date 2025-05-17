# main.py
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp, ThemeManager
from kivymd.uix.button import MDButton, MDButtonText, MDButtonIcon
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogIcon,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogButtonContainer,
    MDDialogContentContainer,
)
from kivymd.uix.progressindicator import MDLinearProgressIndicator, MDCircularProgressIndicator
from kivy.clock import Clock
from moviepy.editor import VideoFileClip
import os
import threading

Window.size = (360, 600)  # Set window size for desktop preview

class HomeScreen(Screen):
    pass

class ConverterApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_manager = MDFileManager(exit_manager=self.exit_manager, select_path=self.select_file_path, ext=[".mp4", ".avi", ".mov", ".mkv"])
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

    def show_file_manager(self, for_output=False):
        if for_output:
            self.file_manager.select_path = self.select_output_path
        else:
            self.file_manager.select_path = self.select_file_path
        self.file_manager.show(os.path.expanduser("~"))  # Open file manager at the home directory

    def exit_manager(self, *args):
        self.file_manager.close()

    def select_file_path(self, path):
        # Reset any previous output selection and UI elements
        self.output_directory = ""
        self.root.get_screen('home').ids.file_name.text = ""
        self.root.get_screen('home').ids.progress_label.text = ""
        if self.progress_bar:
            self.remove_progress_bar()

        # Set the selected file and update the UI
        self.selected_file = path
        self.file_manager.close()
        self.root.get_screen('home').ids.file_name.text = f"Filename: {os.path.basename(self.selected_file)}"
        self.root.get_screen('home').ids.file_name_selection.text = "Change"
        self.check_ready_to_convert()

    def select_output_path(self, path):
        # Set the output directory
        self.output_directory = path
        self.file_manager.close()
        self.root.get_screen('home').ids.output_directory_label.text = f"Output Directory: {self.output_directory}"
        self.check_ready_to_convert()

    def check_ready_to_convert(self):
        # Enable the convert button only if both file and output directory are selected
        if self.selected_file and self.output_directory:
            self.root.get_screen('home').ids.convert_button.disabled = False
        else:
            self.root.get_screen('home').ids.convert_button.disabled = True

    def show_output_directory_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                MDDialogHeadlineText(
                    text="Select Output Directory",
                ),
                MDDialogSupportingText(
                    text="Choose the location where the audio file will be saved.",
                ),
                MDDialogButtonContainer(
                    Widget(),
                    MDButton(
                        MDButtonText(text="Cancel"),
                        style="text",
                        on_release=lambda x: self.close_dialog()
                    ),
                    MDButton(
                        MDButtonText(text="Select"),
                        style="text",
                        on_release=lambda x: self.close_dialog_and_show_file_manager()
                    ),
                    spacing="8dp",
                ),
            )
        self.dialog.open()

    def close_dialog(self):
        if self.dialog:
            self.dialog.dismiss()  # Close the dialog

    def close_dialog_and_show_file_manager(self):
        if self.dialog:
            self.dialog.dismiss()  # Close the dialog
        self.show_file_manager(for_output=True)

    def start_conversion(self):
        if self.selected_file and self.output_directory:
            self.root.get_screen('home').ids.progress_label.text = "Progress: Starting..."
            self.progress_bar = MDLinearProgressIndicator(id="progress", value=0, max=100, indicator_color="blue")
            self.root.get_screen('home').ids.layout.add_widget(self.progress_bar)
            threading.Thread(target=self.convert_to_audio).start()
            Clock.schedule_interval(self.update_progress, 0.5)
            
        else:
            print("Conversion cannot start without both file and output directory selected.")

    def convert_to_audio(self):
        try:
            video = VideoFileClip(self.selected_file)
            output_path = os.path.join(self.output_directory, f"{os.path.splitext(os.path.basename(self.selected_file))[0]}.{self.output_format}")
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
                self.progress_bar.indicator_color = "green"
                Clock.unschedule(self.update_progress)

    def remove_progress_bar(self):
        if self.progress_bar:
            self.root.get_screen('home').ids.layout.remove_widget(self.progress_bar)
            self.progress_bar = None

    def show_success_dialog(self, output_path):
        success_dialog = MDDialog(
            MDDialogHeadlineText(
                text="Conversion Successful",
            ),
            MDDialogSupportingText(
                text=f"Audio saved as: {output_path}",
            ),
            MDDialogButtonContainer(
                Widget(),
                MDButton(
                    MDButtonText(text="OK"),
                    style="text",
                    on_release=lambda x: success_dialog.dismiss()
                ),
                spacing="8dp",
            ),
        )
        success_dialog.open()

    def show_error_dialog(self, error_message):

        error_dialog = MDDialog(
            MDDialogHeadlineText(
                text="Error",
            ),
            MDDialogSupportingText(
                text=f"An error occurred: {output_path}",
            ),
            MDDialogButtonContainer(
                Widget(),
                MDButton(
                    MDButtonText(text="OK"),
                    style="text",
                    on_release=lambda x: error_dialog.dismiss()
                ),
                spacing="8dp",
            ),
        )
        error_dialog.open()


if __name__ == "__main__":
    ConverterApp().run()
