import flet as ft
from moviepy.editor import VideoFileClip
from proglog import TqdmProgressBarLogger
import os
from threading import Thread


def main(page: ft.Page):
    page.title = "Video Converter App"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Supported formats
    formats = ["MP4", "AVI", "GIF"]

    # Widgets
    file_picker = ft.FilePicker(on_result=lambda e: on_file_picked(e))
    save_picker = ft.FilePicker(on_result=lambda e: on_save_location_selected(e))  # For saving
    file_path_text = ft.Text("")
    output_format_dropdown = ft.Dropdown(options=[ft.dropdown.Option(f) for f in formats])
    convert_button = ft.ElevatedButton("Convert", on_click=lambda e: start_conversion_thread())
    download_button = ft.ElevatedButton("Download", on_click=lambda e: save_picker.save_file_dialog(), disabled=True)
    status_text = ft.Text("")
    progress_bar = ft.ProgressBar(width=300, visible=False)

    # Local storage for converted video path
    converted_video_path = None

    # Ensure the FilePickers are added to the page
    page.overlay.append(file_picker)
    page.overlay.append(save_picker)

    # File picker event handler
    def pick_file(e):
        file_picker.pick_files(allow_multiple=False)

    # Event handler for when a file is selected
    def on_file_picked(e):
        if e.files:
            file_path_text.value = f"Selected file: {e.files[0].path}"
            page.update()

    # Start the conversion in a separate thread
    def start_conversion_thread():
        # Run the conversion in a separate thread to keep the UI responsive
        thread = Thread(target=convert_video)
        thread.start()

    # Custom logger for progress
    class FletProgressLogger(TqdmProgressBarLogger):
        def __init__(self):
            super().__init__()
            self.total_progress = 1  # Initialize with 1 to avoid division by zero

        def bars_callback(self, bar, attr, value, total=None):
            if total:
                self.total_progress = total
            # Ensure value and progress are within the range [0.0, 1.0]
            if value < 0:
                value = 0
            progress = max(0.0, min(value / self.total_progress, 1.0))
            progress_bar.value = progress
            page.update()

    # Conversion function
    def convert_video():
        nonlocal converted_video_path

        if not file_picker.result or not output_format_dropdown.value:
            status_text.value = "Please select a video file and an output format."
            page.update()
            return

        file_path = file_picker.result.files[0].path
        file_path_text.value = f"File: {file_path}"
        output_format = output_format_dropdown.value.lower()
        output_file = os.path.splitext(file_path)[0] + f"_converted.{output_format}"

        # Show progress bar and disable buttons during conversion
        progress_bar.visible = True
        progress_bar.value = 0.0
        convert_button.disabled = True
        download_button.disabled = True
        status_text.value = "Converting, please wait..."
        page.update()

        try:
            clip = VideoFileClip(file_path)

            # Perform the conversion with custom progress updates
            logger = FletProgressLogger()
            if output_format == "gif":
                clip.write_gif(output_file, logger=logger)
            elif output_format == "mp4":
                clip.write_videofile(output_file, codec="libx264", logger=logger)
            elif output_format == "avi":
                clip.write_videofile(output_file, codec="png", logger=logger)

            clip.close()
            converted_video_path = output_file
            status_text.value = "Conversion successful! Click Download."
            download_button.disabled = False

        except Exception as ex:
            status_text.value = f"Error: {str(ex)}"

        # Hide progress bar and enable buttons after conversion
        progress_bar.visible = False
        convert_button.disabled = False
        page.update()

    # Handler for choosing the save location
    def on_save_location_selected(e):
        if e.path and converted_video_path:
            # Copy converted video to the selected location
            try:
                with open(converted_video_path, 'rb') as src_file:
                    with open(e.path, 'wb') as dst_file:
                        dst_file.write(src_file.read())

                # Trigger a success notification
                page.snack_bar = ft.SnackBar(ft.Text("Download completed!"), open=True)
                status_text.value = "Download successful!"
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Download failed: {str(ex)}"), open=True)
                status_text.value = f"Download failed: {str(ex)}"
            page.update()

    # UI layout
    page.add(
        ft.Column([
            ft.Text("Video Converter", style="headlineMedium"),
            ft.Row([ft.Text("Select a video file:"), ft.ElevatedButton("Choose File", on_click=pick_file)]),
            file_path_text,
            ft.Text("Select output format:"),
            output_format_dropdown,
            convert_button,
            download_button,
            status_text,
            progress_bar
        ])
    )

    page.update()


ft.app(target=main)
