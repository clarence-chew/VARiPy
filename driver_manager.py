from commons import get_tkinter_root
from config import MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT
from driver import BeatTrackDriver

WINDOW_POSITIONS = None
WINDOW_COUNT = 0
WINDOW_WIDTH = 0
WINDOW_HEIGHT = 0
def get_window_position(index):
    global WINDOW_POSITIONS, WINDOW_COUNT, WINDOW_WIDTH, WINDOW_HEIGHT
    if WINDOW_POSITIONS is None:
        root = get_tkinter_root()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_count_width = screen_width // MIN_WINDOW_WIDTH
        window_count_height = screen_height // MIN_WINDOW_HEIGHT
        WINDOW_WIDTH = screen_width // window_count_width
        WINDOW_HEIGHT = screen_height // window_count_height
        WINDOW_POSITIONS = [(x, y, WINDOW_WIDTH, WINDOW_HEIGHT) for y in range(0, screen_height, WINDOW_HEIGHT)
            for x in range(0, screen_width, WINDOW_WIDTH)]
    return WINDOW_POSITIONS[index % len(WINDOW_POSITIONS)]


class DriverManager():
    def __init__(self):
        self.drivers: list[BeatTrackDriver] = []

    def allocate_drivers(self, total):
        # TODO: consider multithreading
        for i in range(total, len(self.drivers)):
            self.drivers[i].exit()
        self.drivers = self.drivers[:total]
        for i in range(len(self.drivers), total):
            driver = BeatTrackDriver()
            driver.set_window_dimensions(*get_window_position(i))
            self.drivers.append(driver)

    def get_driver(self, index):
        return self.drivers[index]

DRIVER_MANAGER = None
def get_driver_manager():
    global DRIVER_MANAGER
    if DRIVER_MANAGER is None:
        DRIVER_MANAGER = DriverManager()
    return DRIVER_MANAGER