import json
import random
import time

import flet as ft  # type: ignore

MIN_HEIGHT = 700
MIN_WIDTH = 500


def main(page: ft.Page):
    # Page size settings
    page.window_prevent_close = True
    page.window_width = MIN_WIDTH
    page.window_height = MIN_HEIGHT
    page.window_resizable = False
    track_list_to_play: dict[str, str] = {}
    track_list_to_save: dict[str, str] = {}
    audio: ft.Audio

    # Formatting time in 00:00 format
    def format_time(sec: int) -> str:
        minutes = sec // 60
        sec = sec % 60
        formatted_time = '{0:02d}:{1:02d}'.format(minutes, sec)
        return formatted_time

    def find_key():
        for key, val in track_list_to_play.items():
            if val == audio.src:
                return key

    def create_json(e):
        if e.data == 'close':
            with open('playlist.json', 'w') as f:
                json.dump(track_list_to_save, f, indent=4)
                print(json.dumps(track_list_to_save, indent=4))
            page.window_destroy()

    def create_track_list():
        nonlocal track_list_to_play, track_list_to_save
        try:
            with open('playlist.json', 'r') as f:
                track_list_to_play = json.load(f)
                track_list_to_save = track_list_to_play
            display_tracks()
        except FileNotFoundError:
            print('File not found')

    def display_tracks():
        new_track_list = []
        for i in track_list_to_play.keys():
            new_track_list.append(
                ft.ElevatedButton(i, on_click=configure_track))
        track_list_view.controls = new_track_list
        page.update()

    def shuffle_track_list(e):
        nonlocal track_list_to_play
        print(track_list_to_play)
        tracks = list(track_list_to_play.keys())
        random.shuffle(tracks)
        track_list_to_play = dict([(m, track_list_to_play[m]) for m in tracks])
        print(track_list_to_play)
        configure_track(file_name=list(track_list_to_play.keys())[0])

    def change_volume(e):
        nonlocal audio
        audio.volume = float(e.data) / 100

    def change_bar(e):
        track_length_bar.value = e.data
        current_time.value = format_time(int(e.data) // 1000)
        print(e.data)
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

    def play_next_track(filename=None):
        nonlocal audio
        if filename:
            track = list(track_list_to_play.keys())
            if repeat.value:
                configure_track(file_name=filename)
            else:
                if track.index(filename) + 1 > len(track) - 1:
                    next_track = track[0]
                else:
                    next_track = track[track.index(filename) + 1]
                time.sleep(.1)
                configure_track(file_name=next_track)

    def play_prev_track(filename=None):
        nonlocal audio
        if filename:
            track = list(track_list_to_play.keys())
            next_track = track[track.index(filename) - 1]
            time.sleep(.1)
            configure_track(file_name=next_track)

    def check_state(e, filename):
        if e.data == 'completed':
            play_pause_button.icon = ft.icons.PLAY_ARROW
            if autoplay.value:
                play_next_track(filename)

    def set_text(file_name, duration):
        track_name.value = file_name
        end_time.value = format_time(duration // 1000)
        current_time.value = format_time(0)
        page.update()

    def configure_track(e=None, file_name=None):
        nonlocal audio
        if e is not None:
            file_name = e.control.text
        if type(ft.Audio()) in [type(i) for i in page.overlay]:
            page.overlay.pop()
        audio = ft.Audio(
            src=track_list_to_play[file_name],
            autoplay=False,
            volume=volume_slider.value / 100,
            balance=0,
            on_loaded=lambda _: print("Loaded"),
            on_position_changed=lambda e: change_bar(e),
            on_state_changed=lambda e: check_state(e, file_name)
        )
        page.overlay.append(audio)
        page.update()
        time.sleep(0.1)
        set_text(file_name, audio.get_duration())
        audio.play()
        track_length_bar.max = audio.get_duration()
        volume_slider.disabled = False
        play_pause_button.icon = ft.icons.PAUSE
        play_pause_button.disabled = False
        prev_button.disabled = False
        next_button.disabled = False
        page.update()

    def load_track(e):
        nonlocal track_list_to_play

        for j in e.files:
            file_name = j.name
            file_path = j.path
            if file_name not in [i.text for i in track_list_view.controls]:
                track_list_to_play[file_name] = file_path
                track_list_to_save[file_name] = file_path
                print(track_list_to_play)
            else:
                print('Track always in tracklist')
            page.update()
            display_tracks()

    # File picker
    file_picker = ft.FilePicker(on_result=load_track)
    # Buttons
    play_pause_button = ft.IconButton(ft.icons.PLAY_ARROW, disabled=True, on_click=lambda _: play_pause())
    next_button = ft.IconButton(ft.icons.SKIP_NEXT, disabled=True, on_click=lambda _: play_next_track(find_key()))
    prev_button = ft.IconButton(ft.icons.SKIP_PREVIOUS, disabled=True, on_click=lambda _: play_prev_track(find_key()))
    buttons_row = ft.Row([prev_button, play_pause_button, next_button],
                         alignment=ft.MainAxisAlignment.CENTER,
                         )
    add_track_button = ft.TextButton(
        text='Add Track',
        icon=ft.icons.ADD,
        on_click=lambda e: file_picker.pick_files(
            allow_multiple=True,)
    )
    shuffle_button = ft.IconButton(ft.icons.SHUFFLE, on_click=shuffle_track_list)
    # Repeat checkbox
    repeat = ft.Checkbox(label='Repeat')
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
    track_length_bar = ft.Slider(min=0, value=0,
                                 on_change=lambda e: audio.seek(position_milliseconds=int(float(e.data))))
    # Volume slider
    volume_slider = ft.Slider(min=0,
                              max=100,
                              divisions=10,
                              value=10,
                              disabled=True,
                              label="{value}%",
                              on_change=lambda e: change_volume(e))
    # Autoplay checkbox
    autoplay = ft.Checkbox(label='Autoplay')
    # Track list
    track_list_view = ft.ListView(expand=True, spacing=2)

    create_track_list()
    # Add elems to interface
    page.controls.append(
        ft.Column(
            [ft.Row([track_name], alignment=ft.MainAxisAlignment.CENTER), time_row, track_length_bar, buttons_row,
             ft.Row(
                 [
                     autoplay,
                     repeat,
                     shuffle_button,
                     volume_slider
                 ],
                 alignment=ft.MainAxisAlignment.SPACE_BETWEEN
             ),
             add_track_button],
            alignment=ft.MainAxisAlignment.CENTER),
    )
    page.controls.append(track_list_view)
    page.overlay.append(file_picker)
    page.on_window_event = create_json
    page.update()


if __name__ == '__main__':
    ft.app(main)
