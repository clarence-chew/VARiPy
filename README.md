# VARiPy: Video-Audio Remix in Python

Remix online music from various videos. You can specify which online videos to use.

This uses Chrome WebDriver to play videos online. With a bit of JavaScript and Python, we can modify the videos and play them at certain times to form remixes.

This program specifies the timing using beats, so videos need to be timed in beats, and the timing of the remix is also given in beats.

Features:
- Store your remixes in JSON files
- Play your remixes as online videos
- CLI-based UI

Known issues:
- Some sites might have CORS issues.
- Videos are limited to being between (1/16)x and 16x speed.
- Lag may affect the timing of the videos.
- Using shortened URLs increase reloading time since we detect if the URL is the same to skip reloading.

Unknown issues:
- This has only been tested on Windows.

Credits:
- JavaScript code adapted from [Pitch shifter - HTML5 Video audio FX](https://chromewebstore.google.com/detail/pitch-shifter-html5-video/mpmkclglcbkjchakihfpblainfncennj)