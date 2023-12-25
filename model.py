from bisect import bisect_left
from driver import BeatTrackDriver
from task_timer import get_task_timer
from timing import BeatTimer
from track_section import TrackSection
from typing import Any


class Track():
    def __init__(self, **kwargs):
        self.url = kwargs.get("url", "")
        # default: 1 beat per millisecond
        self.timing_sections = kwargs.get("timing_sections", [[0, 60000]])
        self.timing_offset = kwargs.get("timing_offset", 0)
        self.data = kwargs.get("data", []) # invariant: sorted by play_time
        self.canvas = kwargs["canvas"]
        self.track_sections: list[TrackSection] = []
        #self.track_driver = BeatTrackDriver()
        #self.track_driver.set_url(self.url)
        #self.track_driver.set_offset_sections(self.timing_offset, self.timing_sections)
        self.track_index = kwargs["track_index"]
        for track_data in self.data:
            self.track_sections.append(TrackSection(
                canvas=self.canvas, track=self,
                track_index=self.track_index, **track_data
            ))

    def add_track_section(self, **kwargs):
        pass

    def serialize(self):
        """Returns a value that can be interpreted as JSON."""
        return {
            "url": self.url,
            "timing_offset": self.timing_offset,
            "timing_sections": self.timing_sections,
            "data": [section.serialize() for section in self.track_sections]
        }


class RemixModel:
    def __init__(self):
        self.track_data: list[dict[str, Any]] = None
        self.beat_timer: BeatTimer = None
        self.tracks: list[Track] = None

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
            "beat_timer": self.beat_timer.serialize()
        }
