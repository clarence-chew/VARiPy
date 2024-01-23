from model.music import Track
from model.time import BeatTimer
from typing import Any

class Remix:
    def __init__(self):
        self.track_data: list[dict[str, Any]] = None
        self.beat_timer: BeatTimer = None
        self.tracks: list[Track] = None
        self.script: str = ""

    def get_time_from_song_beat(self, song_beat):
        return self.beat_timer.time_from_beat(song_beat)

    def add_track(self, url, timing_sections):
        self.tracks.append(Track(url=url, canvas=self, data=[],
            timing_sections=timing_sections))

    def delete_track(self, index):
        self.tracks.pop(index)

    def add_track_section(self, index, **kwargs):
        self.tracks[index].add_track_section(**kwargs)

    def set_data(self, data):
        self.track_data = data.get("tracks")
        self.beat_timer = BeatTimer(data.get("beat_timer"))
        self.script = data.get("script", "")
        self.tracks = []
        for index, track in enumerate(self.track_data):
            self.tracks.append(Track(canvas=self, track_index=index, **track))

    def clear_data(self):
        self.track_data = None
        self.beat_timer = None
        self.tracks = None

    def serialize(self):
        """Returns a value that can be interpreted as JSON."""
        return {
            "tracks": [track.serialize() for track in self.tracks],
            "beat_timer": self.beat_timer.serialize(),
            "script": self.script
        }