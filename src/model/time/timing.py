from model.time.time_value import TimeValue

class BeatTimer():
    def __init__(self, sections):
        self.sections = sections # [[number of beats, bpm]]
        self.sections[-1][0] = float("inf")

    def time_from_beat(self, beat_number):
        cur_time = TimeValue(seconds=0)
        for section in self.sections:
            cur_time = cur_time.add(minutes=min(section[0], beat_number)/section[1])
            if section[0] >= beat_number:
                return cur_time
            beat_number -= section[0]
        assert(False) # unreachable

    def beat_from_time(self, current_time: TimeValue):
        """Gets the current beat number."""
        cur_beats = 0
        for section in self.sections:
            cur_beats += min(section[0], current_time.minutes*section[1])
            if section[0] >= current_time.minutes*section[1]:
                return cur_beats
            current_time = current_time.add(minutes = -section[0]/section[1])
        assert(False) # unreachable
    
    def get_current_beat_section(self, beat_number):
        for section in self.sections:
            if section[0] > beat_number:
                return section[0] - beat_number, section[1]
            beat_number -= section[0]
        assert(False) # unreachable
    
    def serialize(self):
        return self.sections

class OffsetBeatTimer(BeatTimer):
    def __init__(self, offset: TimeValue, sections):
        super().__init__(sections)
        self.offset = offset

    def time_from_beat(self, beat_number):
        return self.offset.add(seconds=super().time_from_beat(beat_number).seconds)
    
    def beat_from_time(self, current_time):
        if current_time.seconds < self.offset.seconds:
            return (current_time.minutes - self.offset.minutes) / self.sections[0][1]
        return super().beat_from_time(current_time.add(seconds=-self.offset.seconds))
    
    def serialize(self):
        return {
            "offset": self.offset.seconds,
            "sections": self.sections
        }



