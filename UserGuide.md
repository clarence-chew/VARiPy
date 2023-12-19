# User Guide

## Installation Instructions

1. Create a local fork of the repo.
2. Download the [chrome driver](https://googlechromelabs.github.io/chrome-for-testing/).
3. Place the chrome driver executable in the same directory as this README.

## How to Run

Run main.py.

## Commands
- `play` Play your remix from the start.
- `play 10` Play your remix from 10 seconds.
- `pause` Stop playing your remix.
- `exit` Quit the program.

## Data File Format

The only data file accepted so far is `data.txt`. Edit the example provided to make your own remix.

# Configuration

In `config.py`, you can set the width and height of the windows. The program would automatically find values to help tile the screen with windows of at least that size. An important limitation is that Chrome driver windows are 500px wide.