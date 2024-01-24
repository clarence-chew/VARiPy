from commons.command_parser import parse_command
from commons import write_json_file, read_json_file
from model.music import Remix
from view import RemixView
from model.time import TimeValue
from typing import Any
import sys
from tkinter.filedialog import askopenfilename, asksaveasfilename
from controller.settings import SettingsController

class RemixController:
    def __init__(self, model: Remix, view: RemixView):
        self.model = model
        self.view = view
        self.initialize_app()
        self.initialize_data()
    
    def initialize_app(self):
        self.view.set_command_handler(self.handle_command)
        self.current_file = ""
        self.settings_controller = SettingsController(self.view.get_settings_panel())

    def initialize_data(self):
        self.read_data(self.settings_controller.get_setting("DEFAULT_FILE"))

    def handle_command(self, event):
        command = self.view.get_command()
        tokens = parse_command(command)
        clear_command = True
        self.view.display_text("") # clear from previous command
        match tokens:
            case ["eval", *args]: # debugging purposes
                try:
                    result = eval(command[5:]) 
                    self.view.display_text(result)
                    print(result)
                except Exception as e:
                    self.view.display_text(repr(e))
                    print(repr(e))
            case ["exit"]:
                self.clear_data()
                self.view.root.destroy()
                sys.exit()
            case ["open", *args]:
                filename = args[0] if args else askopenfilename()
                if filename == "":
                    self.view.display_text("no file chosen")
                    clear_command = False
                else:
                    self.read_data(filename)
            case ["pause"] | ["stop"]:
                self.view.pause_music()
            case ["play"] | ["start"]:
                self.play_music()
            case ["play", start, *args] | ["start", start, *args]:
                self.play_music(float(start))
            case ["play_section"]:
                self.view.play_selected_section()
            case ["reload"]:
                self.read_data(self.current_file)
            case ["save"]:
                write_json_file(self.model.serialize(), self.current_file)
            case ["save_as", *args]:
                filename = args[0] if args else asksaveasfilename()
                if filename == "":
                    self.view.display_text("no file chosen")
                    clear_command = False
                else:
                    write_json_file(self.model.serialize(), filename)
            case ["skip_ad", video]:
                self.view.skip_ad(int(video))
            case _:
                self.view.display_text("unknown command")
                clear_command = False
        """
            case ["bpm", *args]:
                pass
            case ["seek", *args]:
                pass
            case ["add", *args]:
                pass
            case ["del", *args]: # edit commands
                # track number, start beat, number of beats
                # bpm scale
                pass
        """
        if clear_command:
            self.view.clear_command()
    
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
        self.view.add_track(url, timing_sections)

    def play_music(self, start_time=0.0):
        self.view.set_current_time(TimeValue(seconds=start_time))
        self.view.play_music()
    
    def play_music_from_current_time(self):
        song_beat = self.view.get_song_beat()
        current_time = self.model.get_time_from_song_beat(song_beat)
        self.view.set_current_time(current_time)
        self.view.play_music()
    
    def read_data(self, filename):
        data = read_json_file(filename)
        if data is None:
            self.view.display_text(f"cannot open file {filename}")
        else:
            self.current_file = filename
            self.model.set_data(data)
            self.view.set_data(data)
            self.view.display_text(f"read data from {filename}")
    
    def write_data(self, filename):
        write_json_file(self.model.serialize(), filename)
        self.current_file = filename
        self.view.display_text(f"written data to {filename}")
    
    def clear_data(self):
        self.model.clear_data()
        self.view.clear_data()