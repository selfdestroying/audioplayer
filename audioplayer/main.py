import time
import wave
import flet as ft  # type: ignore
import simpleaudio as sa  # type: ignore
from pydub import AudioSegment  # type: ignore

MIN_HEIGHT = 300
MIN_WIDTH = 500
TRACK_TIME = 10


def main(page: ft.Page):
    page.window_width = MIN_WIDTH
    page.window_height = MIN_HEIGHT
    page.window_resizable = False
    play_flag = True
    current_track_time = 0
    play_obj = None
    wave_obj = None

    def format_time(sec: int) -> str:
        minutes = sec // 60
        sec = sec % 60
        formatted_time = '{0}:{1:02d}'.format(minutes, sec)
        return formatted_time

    def show_file_name(e: ft.FilePickerResultEvent):
        nonlocal wave_obj
        mp3_path = e.files[0].path
        wav_path = f'{e.files[0].name[:-4]}.wav'
        sound = AudioSegment.from_mp3(mp3_path)
        sound.export(wav_path, format="wav")

        wav = wave.open(wav_path, mode="r")
        (nchannels, sampwidth, framerate, nframes, comptype, compname) = wav.getparams()
        content = wav.readframes(nframes)
        wave_obj = sa.WaveObject(content)

    def pause(e):
        nonlocal play_flag, play_obj
        buttons_row.controls[1] = ft.IconButton(ft.icons.PLAY_ARROW, on_click=play_track)
        play_flag = False
        play_obj.stop()

    def play_track(e):
        nonlocal play_flag, current_track_time, wave_obj, play_obj
        play_obj = wave_obj.play()
        play_flag = True
        buttons_row.controls[1] = ft.IconButton(ft.icons.PAUSE, on_click=pause)
        for i in range(current_track_time, TRACK_TIME + 1):
            if play_flag:
                print(play_flag)
                track_length_bar.value = ((i * 100) / TRACK_TIME) * 0.01
                current_track_time = i
                current_time_text.value = format_time(current_track_time)
                page.update()
                time.sleep(1)
        if current_track_time == TRACK_TIME:
            current_track_time = 0
            current_time_text.value = format_time(current_track_time)
            track_length_bar.value = 0
        buttons_row.controls[1] = ft.IconButton(ft.icons.PLAY_ARROW, on_click=play_track)
        page.update()

    play_pause_button = ft.IconButton(ft.icons.PLAY_ARROW, on_click=play_track)
    next_button = ft.IconButton(ft.icons.SKIP_NEXT)
    prev_button = ft.IconButton(ft.icons.SKIP_PREVIOUS)
    current_time_text = ft.Text(value=format_time(current_track_time))
    end_time = ft.Text(value=format_time(TRACK_TIME))
    time_row = ft.Row(
        [current_time_text,
         end_time],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )
    track_length_bar = ft.ProgressBar(value=0)
    buttons_row = ft.Row([prev_button, play_pause_button, next_button],
                         alignment=ft.MainAxisAlignment.CENTER,
                         )

    file_picker = ft.FilePicker(on_result=show_file_name)
    page.overlay.append(file_picker)
    page.update()

    add_track_button = ft.IconButton(
        ft.icons.ADD,
        on_click=lambda e: file_picker.pick_files(
            allow_multiple=True,
            file_type=ft.FilePickerFileType.AUDIO),
    )
    page.add(
        ft.Container(
            content=ft.Column([time_row, track_length_bar, buttons_row, add_track_button],
                              alignment=ft.MainAxisAlignment.CENTER),
            height=MIN_HEIGHT,
            width=MIN_WIDTH
        ),
    )


if __name__ == '__main__':
    ft.app(main, upload_dir='uploads')
