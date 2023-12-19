from bisect import bisect_left
from commons import read_file, constrain
from config import MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from task_timer import get_task_timer
from time_value import TimeValue
from timing import BeatTimer, OffsetBeatTimer
import tkinter as tk
from track_section import TrackSection

MILLISECONDS_PER_SECOND = 1000

def get_chrome_driver_path():
    # Get the directory where the current Python script is located
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Specify the relative path to the driver executable from the script's directory
    relative_path = "chromedriver.exe"
    return os.path.join(current_directory, relative_path)

DRIVER_PATH = get_chrome_driver_path()
VIDEO_JS_CODE = read_file("min_js.txt")

def get_chrome_driver(window_name=None):
    # Create the absolute path by joining the current directory and the relative path
    service = Service(executable_path=DRIVER_PATH)
    options = webdriver.ChromeOptions()
    # Allow videos to autoplay and run Web Audio automatically
    # More switches at https://peter.sh/experiments/chromium-command-line-switches/
    options.add_argument("--autoplay-policy=no-user-gesture-required")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--disable-web-security") # TODO check remove
    options.add_argument("--disable-gpu") # TODO check remove
    options.add_argument("--disable-features=IsolateOrigins,site-per-process") # TODO check remove
    #options.add_argument("--user-data-dir='C://ChromeDev'")
    if window_name: options.add_argument('--window-name="{window_name}"')
    # Keep running after code ends
    options.add_experimental_option("detach", True)
    
    return webdriver.Chrome(service=service, options=options)

TKINTER_ROOT = None
def get_tkinter_root():
    global TKINTER_ROOT
    if TKINTER_ROOT is None:
        TKINTER_ROOT = tk.Tk()
    return TKINTER_ROOT

WINDOW_POSITIONS = []
WINDOW_COUNT = 0
WINDOW_WIDTH = 0
WINDOW_HEIGHT = 0
def get_unused_window_position():
    global WINDOW_POSITIONS, WINDOW_COUNT, WINDOW_WIDTH, WINDOW_HEIGHT
    if WINDOW_COUNT == 0:
        root = get_tkinter_root()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_count_width = screen_width // MIN_WINDOW_WIDTH
        window_count_height = screen_height // MIN_WINDOW_HEIGHT
        WINDOW_WIDTH = screen_width // window_count_width
        WINDOW_HEIGHT = screen_height // window_count_height
        WINDOW_POSITIONS = [(x,y) for y in range(0, screen_height, WINDOW_HEIGHT)
            for x in range(0, screen_width, WINDOW_WIDTH)]
    WINDOW_COUNT += 1
    return WINDOW_POSITIONS[WINDOW_COUNT - 1]

class TrackDriver():
    def __init__(self, url):
        driver = get_chrome_driver()
        driver.get(url)
        driver.set_window_position(*get_unused_window_position())
        driver.set_window_size(WINDOW_WIDTH, WINDOW_HEIGHT)
        driver.execute_script(VIDEO_JS_CODE)
        driver.execute_script("document.getElementsByTagName('video')[0].crossOrigin='anonymous';") # TODO check remove
        driver.execute_script("document.getElementsByTagName('video')[0].pause()")
        
        #driver.execute_script("window.video=document.getElementsByTagName('video')[0];window.video.volume=0;window.setPitchSpeed(0,16);")
        self.driver = driver

    def play_video(self, **kwargs):
        """
        Plays the video now with a custom video start time and duration.
        """
        start_time = kwargs.get("start_time", 0) # in seconds
        duration = kwargs.get("duration", 0) # milliseconds
        pitch = kwargs.get("pitch", 0)
        speed = constrain(kwargs.get("speed", 1), 1/16, 16)
        volume = constrain(kwargs.get("volume", 1), 0, 1)
        self.driver.execute_script(
            f"window.video=document.getElementsByTagName('video')[0];"
            f"window.video.currentTime={start_time};"
            f"window.video.volume={volume};"
            f"window.setPitchSpeed({pitch},{speed});"
            f"window.video.play();"
            f"window.trackTimeout=setTimeout(()=>window.video.pause(),{duration})"
        )

    def pause_video(self):
        """
        Pauses the video.
        """
        self.driver.execute_script("document.getElementsByTagName('video')[0].pause();clearInterval(window.trackTimeout);")

    def exit(self):
        """
        Terminates the video driver.
        """
        self.driver.quit()

class BeatTrackDriver():
    def __init__(self, url, offset, sections):
        self.track_driver = TrackDriver(url)
        self.offset_beat_timer = OffsetBeatTimer(TimeValue(seconds=offset), sections)
    
    def play_video(self, *, song_beat_timer: BeatTimer, track_section: TrackSection):
        song_beat = track_section.song_beat
        video_beats_per_song_beat = track_section.track_beats_per_song_beat
        duration_beats = track_section.duration_beats
        video_start_beat = track_section.start_beat
    
        const_speed_sections = []
        song_beat_pointer = song_beat
        song_start_time = song_beat_timer.time_from_beat(song_beat)
        video_beat_pointer = video_start_beat
        beats_left = duration_beats
    
        while beats_left > 0:
            song_section = song_beat_timer.get_current_beat_section(song_beat_pointer)
            video_section = self.offset_beat_timer.get_current_beat_section(video_beat_pointer)
            current_beats = min(song_section[0], video_section[0]/video_beats_per_song_beat, beats_left)
            beats_left -= current_beats
            song_beat_pointer += current_beats
        
            const_speed_sections.append((
                # section end time compared to the time we start playing
                song_beat_timer.time_from_beat(song_beat_pointer).milliseconds - song_start_time.milliseconds,
                # video time when the section starts (recalibration in case of lag)
                self.offset_beat_timer.time_from_beat(video_beat_pointer).seconds,
                # speed of this section
                song_section[1] * video_beats_per_song_beat / video_section[1]
            ))
            video_beat_pointer += current_beats * video_beats_per_song_beat
        pitch = track_section.pitch
        volume = constrain(track_section.volume, 0, 1)
        current_time = get_task_timer().get_current_time()
        start_index = bisect_left(const_speed_sections,
            current_time.milliseconds, key=lambda x: x[0])
        speed = const_speed_sections[start_index][2]
        section_time = current_time.seconds - (const_speed_sections[start_index][1] if start_index else song_start_time.seconds)
        start_time = const_speed_sections[start_index][1] + section_time * speed
        print(current_time) # expect around 3
        print(section_time) # expect same
        script = "window.video=document.getElementsByTagName('video')[0];window.video.pause();"\
            f"window.speedIndex={start_index};window.speedData={json.dumps(const_speed_sections)};"\
            f"window.video.currentTime={start_time};window.video.volume={volume};window.pitch={pitch};"\
            f"window.setPitchSpeed({pitch},{speed});"\
            f"window.video.play();window.playTime=Date.now()-{section_time}*1000;"\
            "clearTimeout(window.trackTimeout);"\
            "window.trackTimeout=setTimeout(timeoutFn,Math.max(0,window.speedData[window.speedIndex][0]-Date.now()+window.playTime))"
        self.track_driver.driver.execute_script(script)

    def pause_video(self):
        self.track_driver.pause_video()

    def exit(self):
        self.track_driver.exit()


