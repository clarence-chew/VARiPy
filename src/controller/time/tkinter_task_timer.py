import threading
import time
from model.time import TimeValue
class TkinterTaskTimer:
    def __init__(self, root):
        self.root = root
        self.reset()
        self.tasks = dict()

    def set_current_time(self, current_time: TimeValue):
        """
        Sets the start time of the timer such that the time now is the current time.
        """
        self.start = time.time() - current_time.seconds
    
    def get_current_time(self):
        return TimeValue(seconds = time.time() - self.start)
    
    def get_start_time(self):
        return TimeValue(seconds = self.start)
    
    def reset(self):
        """
        Resets the timer.
        """
        self.start = time.time()

    def add_task(self, start_time: TimeValue, callback):
        """
        Adds a new task.
        
        Args:
            start_time: TimeValue for time the callback should run.
            callback: Callback function.
        """
        task_id = self.root.after(max(0, round(start_time.milliseconds-self.get_current_time().milliseconds)), callback)
        self.tasks[task_id] = None

    def override_stop(self):
        """
        Clears all the tasks.
        """
        for task_id in self.tasks:
            self.root.after_cancel(task_id)
        self.tasks.clear()

GLOBAL_TASK_TIMER = None

def get_task_timer(root=None) -> TkinterTaskTimer:
    """Gets the TaskTimer singleton."""
    global GLOBAL_TASK_TIMER
    if GLOBAL_TASK_TIMER is None:
        GLOBAL_TASK_TIMER = TkinterTaskTimer(root) # type: ignore
    return GLOBAL_TASK_TIMER