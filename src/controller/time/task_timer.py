import threading
import time
from model.time import TimeValue
class TaskTimer:
    def __init__(self):
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
        cancel_flag = threading.Event()
        task_id = None
        def worker():
            sleep_time = max(0, start_time.seconds-self.get_current_time().seconds)
            time.sleep(sleep_time)
            if not cancel_flag.is_set():
                callback()
            self.tasks.pop(task_id, None)
        task_id = threading.Thread(target=worker)
        task_id.start()
        self.tasks[task_id] = cancel_flag

    def override_stop(self):
        """
        Clears all the tasks.
        """
        for cancel_flag in self.tasks.values():
            cancel_flag.set() # set the cancel flag
        self.tasks.clear()

GLOBAL_TASK_TIMER = None

def get_task_timer() -> TaskTimer:
    """Gets the TaskTimer singleton."""
    global GLOBAL_TASK_TIMER
    if GLOBAL_TASK_TIMER is None:
        GLOBAL_TASK_TIMER = TaskTimer() # type: ignore
    return GLOBAL_TASK_TIMER


if __name__ == "__main__":
    def test_task_timer():
        t = get_task_timer()
        def print_task(number):
            def callback():
                print(f"task {number}")
            return callback
        t.add_task(TimeValue(milliseconds=500), print_task(1))
        t.add_task(TimeValue(milliseconds=500), print_task(2))
        t.add_task(TimeValue(milliseconds=1000), print_task(3))
        def clear_tasks():
            print("stopped")
            t.override_stop()
        def add_more_tasks():
            print("add more tasks")
            t.add_task(TimeValue(milliseconds=100), print_task(4))
            t.add_task(TimeValue(milliseconds=400), print_task(5))
            t.add_task(TimeValue(milliseconds=1000), print_task(6))
            t.add_task(TimeValue(milliseconds=500), clear_tasks)
        t.add_task(TimeValue(milliseconds=750), add_more_tasks)
    test_task_timer()
