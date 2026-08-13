# WoW Fishing Assistant

English | [简体中文](README.md)

A Windows desktop automation project intended only for learning about image recognition and desktop automation. Automated input may violate the game's terms of service and may result in account penalties. You are responsible for evaluating and accepting those risks.

The application uses OpenCV to locate a fishing bobber inside the selected game window. A bite is confirmed using three signals together: mean image difference, changed-pixel ratio, and consecutive confirmation frames.

## Features

- Simplified Chinese and English interface with instant language switching.
- Multiple bobber templates, including files stored in Unicode paths.
- Recognition limited to the game client area instead of the entire screen.
- Cached templates for faster repeated searches.
- Adjustable template confidence and bite-detection thresholds.
- Optional bait hotkey and configurable anti-AFK interval.
- Cooperatively stoppable worker thread without forced thread termination.
- Settings are saved automatically between sessions.

## Requirements

- Windows 10 or Windows 11
- Python 3.10 or newer
- A game mode that allows screenshots and simulated mouse or keyboard input

The Windows modules `win32gui` and `win32con` are provided by the `pywin32` package. Do not try to install them as separate packages.

## Installation

Open PowerShell or Command Prompt in the project directory, then run:

```powershell
py -3 -m pip install -r requirements.txt
```

If you use a specific Python installation, use that same executable for both installation and startup:

```powershell
"C:\Path\To\python.exe" -m pip install -r requirements.txt
"C:\Path\To\python.exe" auto_fishing.py
```

## Running the Application

```powershell
py -3 auto_fishing.py
```

The interface defaults to Simplified Chinese. Open the **Game Window** tab and set **Language** to **English**. The selection is applied immediately and saved for the next launch.

## Usage

1. Capture a small image of the distinctive upper portion of the fishing bobber. Avoid including a large area of water. Adding templates for different lighting conditions and viewing angles can improve recognition.

2. Select **Add Images** and add one or more template images.

3. Enter the same fishing hotkey configured in the game. The bait hotkey is optional.

4. Open the **Game Window** tab and verify the exact window title. The default is `魔兽世界`, but it can be changed for another client title or locale.

5. Select **Start**. The application activates the target window, casts, searches for the bobber, moves the pointer to it, and monitors the bobber area for a confirmed bite.

6. Use **Stop Safely** to request a cooperative stop. Closing the application while it is running also requests a safe stop before exiting.

## Detection Settings

- **Template confidence:** Controls how closely the screen region must match a template. Lower it if the bobber is not found; raise it when incorrect areas are matched.
- **Mean difference threshold:** The average visual change from the baseline bobber image.
- **Pixel-change threshold:** The amount an individual pixel must change before it is counted.
- **Changed-pixel ratio:** The portion of the bobber image that must change significantly.
- **Confirmation frames:** The number of consecutive changed frames required to confirm a bite.

If the assistant reels in too early, raise the changed-pixel ratio or confirmation-frame count. If it consistently misses bites, first lower the mean difference threshold. The activity log displays all three detection values for calibration.

## Project Structure

```text
wow_auto_fishing/
├─ auto_fishing.py               # Application entry point
├─ fishing_assistant/
│  ├─ config.py                  # Settings model and persistence
│  ├─ texts.py                   # Chinese and English translations
│  ├─ ui.py                      # PyQt5 interface
│  ├─ vision.py                  # Template matching and change detection
│  └─ worker.py                  # Automation loop and safe stopping
├─ docs/
│  ├─ PROJECT.md                 # Architecture and feature notes (Chinese)
│  ├─ CHANGELOG.md               # Change history (Chinese)
│  └─ OPTIMIZATION.md            # Detection improvement notes (Chinese)
├─ tests/                        # Configuration and translation tests
├─ requirements.txt              # Python dependencies
├─ README.md                     # Chinese README
└─ README_EN.md                  # English README
```

## Troubleshooting

### `No module named 'win32con'`

Install `pywin32` into the same Python environment used to start the application:

```powershell
py -3 -m pip install --upgrade pywin32
```

### `No module named 'cv2'`

```powershell
py -3 -m pip install --upgrade opencv-python
```

### The bobber is not found

- Confirm that the game window title is exact.
- Capture a clearer or slightly larger template.
- Add templates for other bobber appearances.
- Lower template confidence in small increments.
- Keep the game window visible and unobstructed.

### False bite detections

- Increase the changed-pixel ratio.
- Increase confirmation frames from 2 to 3.
- Raise the mean difference threshold gradually.
- Capture a template that includes less moving water.

## Disclaimer

This project is provided for study and reference only. It is not affiliated with or endorsed by Blizzard Entertainment. Automated gameplay may violate applicable terms of service and may lead to account restrictions or bans.
