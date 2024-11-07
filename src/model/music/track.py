from model.music import TrackSection

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


