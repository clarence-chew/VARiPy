MILLISECONDS_PER_SECOND = 1000
MILLISECONDS_PER_MINUTE = 60000

class TimeValue:
    def __init__(self, *, minutes=None, seconds=None, milliseconds=None):
        """
        Stores a time value.

        Parameters:
        - minutes (float or int, optional): Time duration in minutes.
        - seconds (float or int, optional): Time duration in seconds.
        - milliseconds (float or int, optional): Time duration in milliseconds.
        """
        self._milliseconds = 0
        if milliseconds is not None:
            self._milliseconds += milliseconds
        if seconds is not None:
            self._milliseconds += seconds * MILLISECONDS_PER_SECOND
        if minutes is not None:
            self._milliseconds += minutes * MILLISECONDS_PER_MINUTE
    @property
    def minutes(self) -> float:
        return self._milliseconds / MILLISECONDS_PER_MINUTE
    @property
    def seconds(self) -> float:
        return self._milliseconds / MILLISECONDS_PER_SECOND
    @property
    def milliseconds(self) -> float:
        return self._milliseconds
    def add(self, *, minutes=None, seconds=None, milliseconds=None):
        ms = 0
        if milliseconds is not None:
            ms += milliseconds
        if seconds is not None:
            ms += seconds * MILLISECONDS_PER_SECOND
        if minutes is not None:
            ms += minutes * MILLISECONDS_PER_MINUTE
        return TimeValue(milliseconds=self.milliseconds+ms)
    def __str__(self):
        return f"TimeValue(milliseconds={self.milliseconds})"