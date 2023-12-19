from bisect import bisect_left
from commons import read_file, subdictionary, constrain, write_json_file, read_json_file
from driver import get_tkinter_root, BeatTrackDriver
from task_timer import get_task_timer
from time_value import TimeValue
from timing import BeatTimer
from track_section import TrackSection
from typing import Any
import sys
import tkinter as tk

current_videos = []

TRACK_HEIGHT = 30

class Track():
    def __init__(self, **kwargs):
        self.url = kwargs.get("url", "")
        # default: 1 beat per millisecond
        self.timing_sections = kwargs.get("timing_sections", [[0, 60000]])
        self.timing_offset = kwargs.get("timing_offset", 0)
        self.data = kwargs.get("data", []) # invariant: sorted by play_time
        self.canvas = kwargs["canvas"]
        self.track_sections: list[TrackSection] = []
        self.track_driver = BeatTrackDriver(self.url, self.timing_offset, self.timing_sections)
        self.track_index = kwargs["track_index"]
        for track_data in self.data:
            self.track_sections.append(TrackSection(
                canvas=self.canvas, driver=self.track_driver, track=self,
                track_index=self.track_index, **track_data
            ))
    
    def get_section_index(self, song_beat):
        return bisect_left(self.track_sections, song_beat, key=lambda x: x.song_beat+x.duration_beats/x.track_beats_per_song_beat)

    def play_music_track(self, song_beat_timer: BeatTimer):
        task_timer = get_task_timer()
        current_time = task_timer.get_current_time()
        self.play_music_track_section(self.get_section_index(song_beat_timer.beat_from_time(current_time)), song_beat_timer)

    def play_music_track_section(self, section_index: int, song_beat_timer: BeatTimer):
        task_timer = get_task_timer()
        if section_index >= len(self.track_sections):
            return
        current_section = self.track_sections[section_index]
        def play_task():
            self.track_driver.play_video(
                song_beat_timer=song_beat_timer,
                track_section=current_section
            )
            if section_index+1 < len(self.track_sections):
                self.play_music_track_section(section_index+1, song_beat_timer)
        task_timer.add_task(song_beat_timer.time_from_beat(current_section.song_beat), play_task)
    
    def pause_music_track(self):
        self.track_driver.pause_video()

    def serialize(self):
        """Returns a value that can be interpreted as JSON."""
        return {
            "url": self.url,
            "timing_offset": self.timing_offset,
            "timing_sections": self.timing_sections,
            "data": [section.serialize() for section in self.track_sections]
        }

CANVAS_VALID_KWARGS = ["background", "bg", "borderwidth", "bd", "closeenough", "confine", "cursor", "height", "highlightbackground", "highlightcolor", "highlightthickness", "insertbackground", "insertborderwidth", "insertontime", "insertontime", "insertwidth", "relief", "scrollregion", "selectbackground", "selectborderwidth", "selectforeground", "state", "takefocus", "width", "xscrollcommand", "xscrollincrement", "yscrollcommand", "yscrollincrement"]

class TrackVisualizer(tk.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, **subdictionary(kwargs, CANVAS_VALID_KWARGS))
        self.master = master
        data = kwargs.get("data", {})
        self.track_data: list[dict[str, Any]] = data.get("tracks")
        self.beat_timer: BeatTimer = BeatTimer(data.get("beat_timer"))
        self.cursor_position = 0 # show cursor position
        self.cursor = None # some line

        self.tracks: list[Track] = []
        for index, track in enumerate(self.track_data):
            self.tracks.append(Track(canvas=self, track_index=index, **track))
        
        self.bind("<Button-1>", self.select_track_section)
        self.selected_rectangle = None

    def draw(self):
        # probably want to draw some sort of cursor
        # ask about drawing vertical line and z-order?
        #canvas.tag_raise(item_id, aboveThis=None) #put vertical line on top
        pass

    def play_music(self):
        for track in self.tracks:
            track.play_music_track(self.beat_timer)
    
    def pause_music(self):
        task_timer = get_task_timer()
        task_timer.override_stop()
        for track in self.tracks:
            track.pause_music_track()

    def select_track_section(self, event):
        # Get the clicked coordinates
        x, y = event.x, event.y

        # Deselect the currently selected rectangle
        if self.selected_rectangle:
            self.itemconfig(self.selected_rectangle, outline="black")
            self.selected_rectangle = None

        # Check if any rectangle is clicked
        track_num = y // TRACK_HEIGHT
        if track_num >= len(self.tracks):
            return
        for track_section in self.tracks[track_num].track_sections:
            x1, y1, x2, y2 = self.coords(track_section.rect_id)
            if x1 < x < x2:
                # Select the clicked rectangle
                self.itemconfig(track_section.rect_id, outline="red")
                self.selected_rectangle = track_section.rect_id
                break

    def add_track(self, url, timing_sections):
        self.tracks.append(Track(url=url, canvas=self, data=[],
            timing_sections=timing_sections))

    def serialize(self):
        """Returns a value that can be interpreted as JSON."""
        return {
            "tracks": [track.serialize() for track in self.tracks],
            "beat_timer": self.beat_timer.serialize()
        }

class MusicEditorUi:
    def __init__(self, **kwargs):
        self.root = get_tkinter_root()
        self.root.title("Music Editor")
        self.data = kwargs.get("data", [])
        default_pad = 10

        # Create the entry widget
        self.entry = tk.Entry(self.root, width=40)
        self.entry.pack(pady=default_pad)
        self.entry.bind("<Return>", self.handle_command)

        # Create a TrackVisualizer instance
        self.track_visualizer = TrackVisualizer(self.root, width=500, height=200, bg="white", data=self.data)
        self.track_visualizer.pack(pady=default_pad)

        self.timer = get_task_timer(self.root)
        self.root.mainloop()

    def handle_command(self, event):
        command = self.entry.get().strip(" ")
        print("Command:", command)
        if command.startswith("bpm"):
            pass
        elif command == "exit":
            #write_json_file(self.track_visualizer.serialize(), "data.json")
            for track in self.track_visualizer.tracks:
                track.track_driver.exit()
            self.root.destroy()
            sys.exit()
        elif command.startswith("play") or command.startswith("start"):
            if " " in command:
                self.play_music(float(command.split(" ")[1]))
            else:
                self.play_music()
        elif command in ["pause", "stop"]:
            self.stop_music()
        elif command.startswith("seek"):
            pass
        elif command.startswith("add"): # edit commands
            # track number, start beat, number of beats
            # bpm scale
            pass
        elif command.startswith("del"):
            pass
        elif command.startswith("eval"):
            print(eval(command[5:])) # debugging purposes
        else:
            print("Unknown Command: ", command)
        self.entry.delete(0, tk.END)
    
    def add_track(self, **kwargs):
        if not kwargs.get("url", ""):
            print("add_track: no url")
            return
        if not kwargs.get("timing_sections", []):
            print("add_track: no timing_sections")
            return
        url = kwargs.get("url")
        # each thing is tuple (start_time, bpm)
        timing_sections = kwargs.get("timing_sections", [])
        self.track_visualizer.add_track(url, timing_sections)

    def play_music(self, start_time=0.0):
        self.timer.set_current_time(TimeValue(seconds=start_time))
        self.track_visualizer.play_music()

    def stop_music(self):
        self.track_visualizer.pause_music()


def main():
    filename = "data.txt" #input("Filename: ")
    data = read_json_file(filename) # python object
    music_editor = MusicEditorUi(data=data)

if __name__ == "__main__":
    main()