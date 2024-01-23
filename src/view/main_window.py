from bisect import bisect_left
from commons import get_tkinter_root, subdictionary
from config import TRACK_HEIGHT
from model.music import TrackSection
from controller.video import BeatTrackDriver, get_driver_manager
from view.scrollable_canvas import ScrollableCanvas
from view.settings_panel import SettingsPanel
from controller.time import get_task_timer
from model.time import BeatTimer
from typing import Any
import tkinter as tk
from tkinter import ttk

CANVAS_VALID_KWARGS = ["background", "bg", "borderwidth", "bd", "closeenough", "confine", "cursor", "height", "highlightbackground", "highlightcolor", "highlightthickness", "insertbackground", "insertborderwidth", "insertontime", "insertontime", "insertwidth", "relief", "scrollregion", "selectbackground", "selectborderwidth", "selectforeground", "state", "takefocus", "width", "xscrollcommand", "xscrollincrement", "yscrollcommand", "yscrollincrement"]

# TODO refactor as Timetable since that's what it does.
# Refactor as view and controller
class TrackVisualizer(tk.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, **subdictionary(kwargs, CANVAS_VALID_KWARGS))
        self.master = master
        self.tracks: list[list[dict]] = None
        self.beat_timer: BeatTimer = None
        self.cursor_position = 0 # show cursor position
        self.cursor = None # some line
        
        self.offset_x = 0
        self.offset_y = 0

        self.bind("<Button-1>", self.select_track_section)
        self.selected_rectangle = None

    def play_music(self):
        driver_manager = get_driver_manager()
        for idx, track in enumerate(self.tracks):
            self.play_music_track(track, driver_manager.get_driver(idx))

    def play_music_track(self, track, track_driver):
        task_timer = get_task_timer()
        current_time = task_timer.get_current_time()
        song_beat = self.beat_timer.beat_from_time(current_time)
        section_index = bisect_left(track, song_beat, key=lambda x: x["track_section"].song_end_beat)
        self.play_music_track_section(track, track_driver, section_index)

    def play_music_track_section(self, track, track_driver: BeatTrackDriver, section_index: int):
        task_timer = get_task_timer()
        if section_index >= len(track):
            return
        current_section: TrackSection = track[section_index]["track_section"]
        def play_task():
            track_driver.play_video(
                song_beat_timer=self.beat_timer,
                track_section=current_section
            )
            if section_index+1 < len(track):
                self.play_music_track_section(track, track_driver, section_index+1)
        task_timer.add_task(self.beat_timer.time_from_beat(current_section.song_beat), play_task)
    
    def play_selected_section(self):
        if not self.selected_rectangle:
            return # no selected section
        track_num, section_index = self.selected_rectangle
        track_driver = get_driver_manager().get_driver(track_num)
        track = self.tracks[track_num]
        current_section: TrackSection = track[section_index]["track_section"]
        get_task_timer().set_current_time(self.beat_timer.time_from_beat(current_section.song_beat))
        track_driver.play_video(
            song_beat_timer=self.beat_timer,
            track_section=current_section
        )

    def pause_music(self):
        task_timer = get_task_timer()
        task_timer.override_stop()
        driver_manager = get_driver_manager()
        for idx in range(len(self.tracks)):
            driver_manager.get_driver(idx).pause_video()

    def select_track_section(self, event):
        # Get the clicked coordinates
        x, y = int(self.canvasx(event.x)), int(self.canvasy(event.y))

        # Deselect the currently selected rectangle
        if self.selected_rectangle:
            track_num, idx = self.selected_rectangle
            self.itemconfig(self.tracks[track_num][idx]["rect_id"], fill="#333333")
            self.selected_rectangle = None

        # Check if any rectangle is clicked
        track_num = y // TRACK_HEIGHT
        if track_num >= len(self.tracks):
            return
        for idx, track_section in enumerate(self.tracks[track_num]):
            x1, y1, x2, y2 = self.coords(track_section["rect_id"])
            if x1 < x < x2:
                # Select the clicked rectangle
                self.itemconfig(track_section["rect_id"], fill="#666666")
                self.selected_rectangle = (track_num, idx)
                break
    
    def get_selected_track_section(self):
        return self.selected_rectangle

    def add_track(self, url, timing_sections):
        pass

    def set_data(self, data):
        self.delete("all")
        self.selected_rectangle = None
        track_data = data["tracks"]
        self.tracks = []
        self.beat_timer = BeatTimer(data["beat_timer"])
        driver_manager = get_driver_manager()
        driver_manager.allocate_drivers(len(track_data))
        for idx, track in enumerate(track_data):
            driver: BeatTrackDriver = driver_manager.get_driver(idx)
            driver.set_url(track["url"])
            driver.set_offset_sections(track["timing_offset"], track["timing_sections"])
            self.tracks.append([{
                "track_section": track_section,
                "rect_id": self.create_rectangle(
                    track_section.song_beat, idx * TRACK_HEIGHT,
                    track_section.song_end_beat, (idx + 1) * TRACK_HEIGHT,
                    fill="#333333", width=2)
            } for track_section in (TrackSection(**section_data) for section_data in track["data"])])

    def set_cursor_position(self, position):
        pass

    def get_song_beat(self):
        return 0 # TODO

    def clear_data(self):
        self.delete("all")
        self.selected_rectangle = None
        self.tracks = []
        self.beat_timer = None
        get_driver_manager().allocate_drivers(0)

class RemixView:
    def __init__(self, **kwargs):
        self.root = get_tkinter_root()
        self.root.title("Music Editor")
        default_pad = 5

        # Create the entry widget
        self.entry = tk.Entry(self.root, width=40)
        self.entry.pack(pady=default_pad, fill=tk.X)

        self.text_output =  tk.Text(self.root, wrap="word", height=5, state="disabled")
        self.text_output.pack(pady=default_pad, fill=tk.X)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=default_pad, fill=tk.BOTH, expand=True)

        # Create a scrollable TrackVisualizer instance
        self.scrollable_canvas = ScrollableCanvas(self.notebook, TrackVisualizer, width=500, height=200, bg="white")
        self.scrollable_canvas.pack(pady=default_pad, fill=tk.BOTH, expand=True)
        self.track_visualizer: TrackVisualizer = self.scrollable_canvas.canvas
        self.notebook.add(self.scrollable_canvas, text="Tracks")

        self.js_frame = tk.Frame(self.notebook)
        self.js_text = tk.Text(self.js_frame, wrap="word")
        self.js_text.pack(pady=default_pad, fill=tk.BOTH, expand=True)
        self.notebook.add(self.js_frame, text="Script")

        self.settings_frame = tk.Frame(self.notebook)
        self.settings_panel = SettingsPanel(self.settings_frame)
        self.notebook.add(self.settings_frame, text="Settings")

        self.timer = get_task_timer(self.root)
    def get_settings_panel(self):
        return self.settings_panel
    def get_command(self):
        return self.entry.get().strip(" ")
    def display_text(self, text=""):
        self.text_output.config(state="normal")
        self.text_output.delete("1.0", tk.END)
        self.text_output.insert(tk.END, text)
        self.text_output.config(state="disabled")
    def get_song_beat(self):
        return self.track_visualizer.get_song_beat()
    def set_command_handler(self, handler):
        self.entry.bind("<Return>", handler)
    def add_track(self, track):
        self.track_visualizer.add_track(track)
    def set_data(self, data):
        self.track_visualizer.set_data(data)
        self.js_text.delete("1.0", tk.END)
        self.js_text.insert(tk.END, data.get("script", ""))
        self.scrollable_canvas.resize_canvas_to_content()
    def play_music(self):
        self.track_visualizer.play_music()
    def pause_music(self):
        self.track_visualizer.pause_music()
    def clear_data(self):
        self.track_visualizer.clear_data()
        self.js_text.delete("1.0", tk.END)
    def set_current_time(self, current_time):
        self.timer.set_current_time(current_time)
    def play_selected_section(self):
        self.track_visualizer.play_selected_section()
    def clear_command(self):
        self.entry.delete(0, tk.END)
    def skip_ad(self, video):
        get_driver_manager().get_driver(video).skip_ad()
