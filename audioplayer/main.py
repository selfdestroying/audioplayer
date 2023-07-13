import time
import flet as ft  # type: ignore
import pygame.mixer

MIN_HEIGHT = 700
MIN_WIDTH = 500


def main(page: ft.Page):
    # Page size settings
    page.window_width = MIN_WIDTH
    page.window_height = MIN_HEIGHT
    page.window_resizable = False
    track_list = {}
    audio: type(ft.Audio())

    # Formatting time in 00:00 format
    def format_time(sec: int) -> str:
        minutes = sec // 60
        sec = sec % 60
        formatted_time = '{0:02d}:{1:02d}'.format(minutes, sec)
        return formatted_time

    def change_volume(e):
        nonlocal audio
        audio.volume = float(e.data) / 100
        print(audio.volume)

    def change_bar(e, duration):
        track_length_bar.value = e.data
        track_length_bar.value = int(e.data) / duration
        current_time.value = format_time(int(e.data) // 1000)
        page.update()

    def play_pause():
        nonlocal audio
        if play_pause_button.icon == ft.icons.PAUSE:
            play_pause_button.icon = ft.icons.PLAY_ARROW
            audio.pause()
        elif play_pause_button.icon == ft.icons.PLAY_ARROW:
            play_pause_button.icon = ft.icons.PAUSE
            audio.resume()
        page.update()

    def set_text(file_name, duration):
        track_name.value = file_name
        end_time.value = format_time(duration // 1000)
        current_time.value = format_time(0)
        page.update()

    def configure_track(file_path, file_name):
        nonlocal audio
        if type(ft.Audio()) in [type(i) for i in page.overlay]:
            page.overlay.pop()
        audio = ft.Audio(
            src=file_path,
            autoplay=False,
            volume=1,
            balance=0,
            on_loaded=lambda _: print("Loaded"),
            on_position_changed=lambda e: change_bar(e, audio.get_duration())
        )
        page.overlay.append(audio)
        audio.volume = 0.1
        page.update()
        time.sleep(0.1)
        set_text(file_name, audio.get_duration())
        audio.play()
        play_pause_button.icon = ft.icons.PAUSE
        volume_slider.disabled = False
        play_pause_button.disabled = False
        prev_button.disabled = False
        next_button.disabled = False
        page.update()

    def load_track(e):
        nonlocal track_list
        file_name = e.files[0].name
        file_path = e.files[0].path
        if file_name not in [i.text for i in track_list_view.controls]:
            track_list[file_name] = file_path
            print(track_list)
            track_list_view.controls.append(
                ft.ElevatedButton(e.files[0].name, on_click=lambda _: configure_track(file_path, file_name)))
            page.update()
        else:
            print('Track always in tracklist')

    # File picker
    file_picker = ft.FilePicker(on_result=load_track)
    # Buttons
    play_pause_button = ft.IconButton(ft.icons.PLAY_ARROW, disabled=True, on_click=lambda _: play_pause())
    next_button = ft.IconButton(ft.icons.SKIP_NEXT, disabled=True)
    prev_button = ft.IconButton(ft.icons.SKIP_PREVIOUS, disabled=True)
    buttons_row = ft.Row([prev_button, play_pause_button, next_button],
                         alignment=ft.MainAxisAlignment.CENTER,
                         )
    add_track_button = ft.TextButton(
        text='Add Track',
        icon=ft.icons.ADD,
        on_click=lambda e: file_picker.pick_files(
            allow_multiple=True,
            file_type=ft.FilePickerFileType.AUDIO),
    )
    # Time text
    track_name = ft.Text(value='-TRACK NAME-', text_align=ft.TextAlign.CENTER)
    current_time = ft.Text(value='--:--')
    end_time = ft.Text(value='--:--')
    time_row = ft.Row(
        [current_time,
         end_time],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )
    # Progress bar
    track_length_bar = ft.ProgressBar(value=0)
    # Volume slider
    volume_slider = ft.Slider(min=0,
                              max=100,
                              divisions=10,
                              disabled=True,
                              label="{value}%",
                              on_change=lambda e: change_volume(e))
    # Track list
    track_list_view = ft.ListView(expand=True, spacing=2)
    # Add elems to interface
    page.controls.append(
        ft.Column(
            [ft.Row([track_name], alignment=ft.MainAxisAlignment.CENTER), time_row, track_length_bar, buttons_row,
             ft.Row(
                 [
                     add_track_button,
                     volume_slider
                 ],
                 alignment=ft.MainAxisAlignment.SPACE_BETWEEN
             )],
            alignment=ft.MainAxisAlignment.CENTER),
    )
    page.controls.append(track_list_view)
    page.overlay.append(file_picker)
    page.update()


if __name__ == '__main__':
    ft.app(main)
