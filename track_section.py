from commons import constrain

TRACK_HEIGHT = 30
class TrackSection():
    """Class that stores data."""
    def __init__(self, **kwargs):
        self.song_beat = kwargs["song_beat"] # what time in the song to play
        self.start_beat = kwargs["start_beat"] # when the cropped section starts
        self.duration_beats = kwargs["duration_beats"] # duration in video beats
        self.track_beats_per_song_beat = kwargs["track_beats_per_song_beat"]
        self.pitch = kwargs.get("pitch", 0)
        self.volume = constrain(kwargs.get("volume", 1), 0, 1)

    @property
    def song_end_beat(self):
        return self.song_beat + self.duration_beats / self.track_beats_per_song_beat

    def transpose_track(self, new_pitch): # TODO remove
        self.pitch = new_pitch
        # Access the selected track using the index stored in the context menu
        #self.pitch = simpledialog.askinteger("Transpose", "Pitch increase (semitones):", initialvalue=self.pitch)
        #print(f"Transposing track at index {self.index}")

    def crop_track(self, start_beat, duration_beats): # TODO remove
        # Access the selected track using the index stored in the context menu
        self.start_beat = start_beat
        self.duration_beats = duration_beats

    def change_speed(self, track_beats_per_song_beat):
        self.track_beats_per_song_beat = track_beats_per_song_beat

    def serialize(self):
        """Returns a value that can be interpreted as JSON."""
        return {
            "song_beat": self.song_beat,
            "start_beat": self.start_beat,
            "duration_beats": self.duration_beats,
            "track_beats_per_song_beat": self.track_beats_per_song_beat,
            "pitch": self.pitch,
            "volume": self.volume
        }