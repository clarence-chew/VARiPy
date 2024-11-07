from bisect import bisect_left
from commons import constrain
from commons.file import read_file, get_absolute_path
from config import DISCARD_NEGLIGIBLE_SECTIONS
import json
import os
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, JavascriptException
from selenium.webdriver.chrome.service import Service
from controller.time import get_task_timer
from model.time import TimeValue, BeatTimer, OffsetBeatTimer
from model.music import TrackSection

MILLISECONDS_PER_SECOND = 1000

DRIVER_PATH = get_absolute_path("chromedriver.exe")
VIDEO_JS_CODE = read_file("src/controller/video/main.js")

def get_chrome_driver(window_name=None):
    # Create the absolute path by joining the current directory and the relative path
    service = Service(executable_path=DRIVER_PATH)
    options = webdriver.ChromeOptions()
    # Allow videos to autoplay and run Web Audio automatically
    # More switches at https://peter.sh/experiments/chromium-command-line-switches/
    options.add_argument("--autoplay-policy=no-user-gesture-required")
    options.add_argument('--blink-settings=imagesEnabled=false,hideScrollbars=true')
    options.add_argument('--enable-chrome-browser-cloud-management')

    # These three should deal with the "Failed to decode OID: 0" issue.
    # options.add_argument('--ignore-certificate-errors')
    options.add_argument('--disable-web-security')
    # options.add_argument('--allow-running-insecure-content')

    #options.add_argument("--app='about:blank'")
    #options.add_argument("--disable-gpu") # TODO check remove
    #options.add_argument("--disable-features=IsolateOrigins,site-per-process") # TODO check remove
    options.add_argument("--guest")
    if window_name: options.add_argument(f'--window-name="{window_name}"')
    # Keep running after code ends
    # options.add_experimental_option("detach", True)
    # Remove banner
    # options.add_experimental_option("excludeSwitches", ["enable-automation"]); 
    return webdriver.Chrome(service=service, options=options)

class TrackDriver():
    def __init__(self):
        self.init_driver()
        self.current_url = "about:blank"

    def init_driver(self):
        is_init = False
        while not is_init:
            try:
                self.driver = get_chrome_driver()
                is_init = True
            except Exception as e:
                # Check if the error message contains the specific text you provided
                if "Failed to decode OID" in str(e):
                    print("Caught error: Failed to decode OID - restarting driver")
                else:
                    raise e
    
    def set_window_dimensions(self, x, y, w, h):
        self.dimensions = (x, y, w, h)
        self.driver.set_window_position(x, y)
        self.driver.set_window_size(w, h)
    
    def refresh_driver(self):
        self.init_driver()
        self.driver.set_window_position(self.dimensions[0], self.dimensions[1])
        self.driver.set_window_size(self.dimensions[2], self.dimensions[3])
    
    def refresh_url(self):
        self.refresh_driver()
        is_run = False
        while not is_run:
            try:
                self.driver.get(self.current_url)
                is_run = True
            except WebDriverException as e:
                print("Caught error: WebDriverException - restarting driver")
                self.refresh_driver()
        self.inject_scripts()
    
    def inject_scripts(self):
        self.driver.execute_script(VIDEO_JS_CODE)
        self.driver.execute_script("window.trackTimeout=setInterval("
            "()=>{let v=document.getElementsByTagName('video')[0], a=document.getElementsByTagName('audio')[0];"
            "(v||a)&&(v&&(v.pause(),window.mediaType='video')||(window.mediaType='audio'),clearInterval(window.trackTimeout))}, 500)")

    def set_url(self, url):
        # Don't reload pages that are already correct.
        if self.current_url == url:
            return
        is_run = False
        while not is_run:
            try:
                self.driver.get(url)
                is_run = True
            except WebDriverException as e:
                print("Caught error: WebDriverException - restarting driver")
                self.refresh_driver()
        self.current_url = url
        self.inject_scripts()

    def clear_url(self):
        self.driver.get("about:blank")
    
    def execute_script(self, script):
        is_executed = False
        while not is_executed:
            try:
                self.driver.execute_script(script)
                is_executed = True
            except JavascriptException as e:
                print("Caught error: JavaScriptException - restarting driver")
                self.refresh_url()
        
    def play_video(self, **kwargs):
        """
        Plays the video now with a custom video start time and duration.
        """
        start_time = kwargs.get("start_time", 0) # in seconds
        duration = kwargs.get("duration", 0) # milliseconds
        pitch = kwargs.get("pitch", 0)
        speed = constrain(kwargs.get("speed", 1), 1/16, 16)
        volume = constrain(kwargs.get("volume", 1), 0, 1)
        self.execute_script(
            f"window.video=document.getElementsByTagName(window.mediaType)[0];"
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
        self.execute_script("document.getElementsByTagName(window.mediaType)[0].pause();clearInterval(window.trackTimeout);")

    def exit(self):
        """
        Terminates the video driver.
        """
        self.driver.quit()

class BeatTrackDriver():
    def __init__(self):
        self.track_driver = TrackDriver()
        self.offset_beat_timer = None
    
    def set_url(self, url):
        self.track_driver.set_url(url)
    
    def set_offset_sections(self, offset, sections):
        self.offset_beat_timer = OffsetBeatTimer(TimeValue(seconds=offset), sections)

    def set_window_dimensions(self, x, y, w, h):
        self.track_driver.set_window_dimensions(x, y, w, h)

    def play_video(self, *, song_beat_timer: BeatTimer, track_section: TrackSection):
        song_beat = track_section.song_beat
        video_beats_per_song_beat = track_section.track_beats_per_song_beat
        duration_beats = track_section.duration_beats
        video_start_beat = track_section.start_beat
    
        const_speed_sections = []
        song_beat_pointer = song_beat
        section_start_time = song_beat_timer.time_from_beat(song_beat)
        video_beat_pointer = video_start_beat
        beats_left = duration_beats
    
        while beats_left > 0:
            song_section = song_beat_timer.get_current_beat_section(song_beat_pointer)
            video_section = self.offset_beat_timer.get_current_beat_section(video_beat_pointer)
            current_beats = min(song_section[0] * video_beats_per_song_beat, video_section[0], beats_left)
            beats_left -= current_beats
            song_beat_pointer += current_beats / video_beats_per_song_beat
            # one sample > 1e-8 minutes, negligible
            section_is_negligible = current_beats / video_beats_per_song_beat / song_section[1] < 1e-8
            if not DISCARD_NEGLIGIBLE_SECTIONS or not section_is_negligible:
                const_speed_sections.append((
                    # section end time
                    song_beat_timer.time_from_beat(song_beat_pointer).milliseconds,
                    # video time when the section starts (recalibration in case of lag)
                    self.offset_beat_timer.time_from_beat(video_beat_pointer).seconds,
                    # speed of this section
                    song_section[1] * video_beats_per_song_beat / video_section[1]
                ))
            video_beat_pointer += current_beats
        pitch = track_section.pitch
        volume = constrain(track_section.volume, 0, 1)
        task_timer = get_task_timer()
        current_time = task_timer.get_current_time()
        start_index = bisect_left(const_speed_sections,
            current_time.milliseconds, key=lambda x: x[0])
        if start_index == len(const_speed_sections):
            print("too slow")
            return # it's over
        speed = const_speed_sections[start_index][2]
        # number of seconds ago this section started
        section_time = current_time.seconds - (const_speed_sections[start_index - 1][0]/1000 if start_index else section_start_time.seconds)
        start_time = const_speed_sections[start_index][1] + section_time * speed
        script = "window.video=document.getElementsByTagName(window.mediaType)[0];window.video.pause();"\
            f"window.speedIndex={start_index};window.speedData={json.dumps(const_speed_sections)};"\
            f"window.video.currentTime={start_time};window.video.volume={volume};window.pitch={pitch};"\
            f"window.setPitchSpeed({pitch},{speed});"\
            f"window.video.play();window.playTime={task_timer.get_start_time().milliseconds};"\
            "clearTimeout(window.trackTimeout);"\
            "window.trackTimeout=setTimeout(timeoutFn,Math.max(0,window.speedData[window.speedIndex][0]-Date.now()+window.playTime))"
        self.track_driver.execute_script(script)

    def pause_video(self):
        self.track_driver.pause_video()

    def clear_data(self):
        self.track_driver.clear_url()
        self.offset_beat_timer = None
    
    def skip_ad(self):
        self.track_driver.execute_script("document.getElementsByTagName('video')[0].currentTime=1e7")

    def exit(self):
        self.track_driver.exit()


