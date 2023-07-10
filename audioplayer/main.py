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
    # Sound init
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.mixer.init()
    # Other variables
    play_flag = True
    current_track_time = 0
    track_time = 0
    track_list: dict[str, str] = {
    }

    # Formatting time in 00:00 format
    def format_time(sec: int) -> str:
        minutes = sec // 60
        sec = sec % 60
        formatted_time = '{0:02d}:{1:02d}'.format(minutes, sec)
        return formatted_time

    # Formatting file name without file extension
    def format_file_name(raw_file_name: str) -> str:
        return raw_file_name[:-4]

    def add_track(e):
        nonlocal track_time, current_track_time
        file_path = track_list[e.control.text]
        track_name.value = e.control.text
        # Get track time
        track_time = int(pygame.mixer.Sound(file_path).get_length())


        current_track_time = 0
        track_length_bar.value = 0
        current_time_text.value = format_time(current_track_time)
        end_time.value = format_time(track_time)

        pygame.mixer.music.load(file_path)
        pygame.mixer.music.stop()
        play_track(e)
        page.update()

    def create_track_list():
        track_list_view.controls = [ft.ElevatedButton(f"{i}",
                                                      style=ft.ButtonStyle(
                                                          shape={
                                                              ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder()
                                                          },
                                                          bgcolor={
                                                              ft.MaterialState.DEFAULT: ft.colors.GREY_900,
                                                              ft.MaterialState.HOVERED: ft.colors.GREY_800
                                                          },
                                                          color={
                                                              ft.MaterialState.DEFAULT: ft.colors.WHITE70
                                                          }

                                                      ), on_click=add_track) for i in track_list.keys()]

    # Get track file function
    def show_file_name(e: ft.FilePickerResultEvent):
        nonlocal track_time, current_track_time
        # Get file name and file path
        file_path = e.files[0].path
        file_name = e.files[0].name
        # Change file name in formatted text
        formatted_file_name = format_file_name(file_name)
        # Add track to name list
        track_list[formatted_file_name] = file_path
        create_track_list()


        current_track_time = 0
        track_length_bar.value = 0
        current_time_text.value = format_time(current_track_time)
        end_time.value = format_time(track_time)

        pause_track(e)
        page.update()

    def pause_track(e):
        nonlocal play_flag
        buttons_row.controls[1] = ft.IconButton(ft.icons.PLAY_ARROW, on_click=play_track)
        play_flag = False
        pygame.mixer.music.pause()

    def play_track(e):
        nonlocal play_flag, current_track_time
        pygame.mixer.music.play(start=current_track_time)
        play_flag = True
        buttons_row.controls[1] = ft.IconButton(ft.icons.PAUSE, on_click=pause_track)
        for i in range(current_track_time, track_time + 1):
            if play_flag:
                track_length_bar.value = ((i * 100) / track_time) * 0.01
                current_track_time = i
                current_time_text.value = format_time(current_track_time)
                page.update()
                time.sleep(1)
        if current_track_time == track_time:
            current_track_time = 0
            track_length_bar.value = 0
            current_time_text.value = format_time(current_track_time)
        buttons_row.controls[1] = ft.IconButton(ft.icons.PLAY_ARROW, on_click=play_track)
        page.update()

    # File picker
    file_picker = ft.FilePicker(on_result=show_file_name)
    # Buttons
    play_pause_button = ft.IconButton(ft.icons.PLAY_ARROW, on_click=play_track)
    next_button = ft.IconButton(ft.icons.SKIP_NEXT)
    prev_button = ft.IconButton(ft.icons.SKIP_PREVIOUS)
    buttons_row = ft.Row([prev_button, play_pause_button, next_button],
                         alignment=ft.MainAxisAlignment.CENTER,
                         )
    add_track_button = ft.IconButton(
        ft.icons.ADD,
        on_click=lambda e: file_picker.pick_files(
            allow_multiple=True,
            file_type=ft.FilePickerFileType.AUDIO),
    )
    # Time text
    current_time_text = ft.Text(value=format_time(current_track_time))
    track_name = ft.Text(value='', text_align=ft.TextAlign.CENTER)
    end_time = ft.Text(value=format_time(track_time))
    time_row = ft.Row(
        [current_time_text,
         end_time],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )
    # Progress bar
    track_length_bar = ft.ProgressBar(value=0)

    # Track list
    track_list_view = ft.ListView(expand=True, spacing=2)

    # Add elems to interface
    page.controls.append(
        ft.Column(
            [ft.Row([track_name], alignment=ft.MainAxisAlignment.CENTER), time_row, track_length_bar, buttons_row,
             add_track_button],
            alignment=ft.MainAxisAlignment.CENTER),
    )
    page.controls.append(track_list_view)
    page.overlay.append(file_picker)
    page.update()


if __name__ == '__main__':
    ft.app(main, upload_dir='uploads')
