TreadMillTracker:

A Python desktop GUI for tracking mechanical treadmill activity using a Raspberry Pi Pico. It logs distance, time, and can simulate key presses to control virtual movement (e.g., in games).

## Features
- Reads data from Raspberry Pi Pico via serial. 
- Displays distance and time on GUI and as a overlay display.
- Key override (presses "W" during movement)
- Multi-monitor overlay
- Save config and log progress


## Install and use:

1. After following the tutorial on building the hardware for this script (link), you can now connect your Pico to a USB port. 
2. Copy and paste main.py script from the /Install folder. Disconnect/Reconnect your pico as main.py scripts runs at starting time.
3. Run `TreadmillTracker.py` or the compiled TreadmillTracker.exe (not recommended: the script overrides the key 'W' when it detects motion on the treadmill, which is a flagged behavior for most 3rd party anti-virus.
   If you choose to do so, add an exclusion rule for the executable in your windows defender, under Virus & threat protection settings.)
5. Choose monitor for overlay, overlay does not work on full-screen apps. Please change your display setting to windowed or borderless window. Save your selection.
6. Test your treadmill for at least 2 minutes. Pulses, distance and time should update correctly. If so, press the "Keyboard" button to activate the keyboard override. Open a .txt file and test it. If the setup works it will write "wwwwww" in your .txt
7. If using switch joycon: start BetterJoyforCemu. Connect your controller via bluetooth and use BetterJoyForCemu to map the buttons as you wish. Steam takes care of supporting the controllers.
8. Enjoy!

## Build Instructions

To build using PyInstaller:

```bash
pyinstaller treadmill_gui.py --clean --noupx --noconsole --onefile -n TreadMillTracker --add-data "config.json;." --add-data "gui_log.txt;." --add-data "LICENSE.txt;." --add-data "TreadmillTracker_icon.png;."  --icon=TreadmillTracker_icon.png

