# Developer Guide

## Classes

### MusicEditorUi

This mutable class handles the UI and the CLI interace.

### TrackVisualiser

This mutable class manages the visualisation of the tracks, track data in beats and remix timing in beats.

### Track

This immutable class stores the data for one track, by storing `TrackSection`s. A Track is composed of 0 or more `TrackSection`s.

### TrackSection

This immutable class stores the data about how to play a particular section of the remix, from when the video starts to when it stops.

### BeatTrackDriver

This mutable class manages a browser instance as well as the timing of the video in beats.

## TODO
Currently:
- Feature freeze.
  - Bugs would be fixed at our discretion.

Important:
- Use multithreading to handle browser driver instances?
- Tools to help edit remixes.
  - Model might need to be Observable.
  - Things to edit:
    - song beat
    - `set_song_beat`
    - tracks
      - track beat
      - `set_track_beat`
      - reorder tracks
      - `move_track_up`
      - `move_track_down`
      - `play_track` play the track to verify that the track beat is set up correctly
    - track sections
      - all data in track section
      - `add_section ...` define a section
      - `delete_section` delete currently selected section
  - Tools like being able to play a track to check if bpm and offset are correct, and playing from nth beat.

Mildly important:
- Check if having a profile or guest profile is faster for Chrome WebDriver
- Check if we can speed up Chrome WebDriver by loading fewer elements

Not important:
- More compatibility with different browser drivers.
  - Not very important: Chrome WebDriver is fast.