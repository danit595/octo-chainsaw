# OctoAutoClicker v1.0.1

A powerful and user-friendly auto-clicker application with macro recording capabilities.

## Features

### Auto Clicker
- Configurable click intervals (hours, minutes, seconds, milliseconds)
- Multiple mouse button support (left, right, middle)
- Single and double click options
- Fixed repetitions or continuous clicking
- Custom click position or current cursor location
- Hotkey support (F6 to start/stop)

### Macro Recording
- Record mouse movements and clicks
- Playback recorded macros with exact timing
- Save and manage multiple macros
- Hotkey support (F7 to start/stop recording)
- Support for all mouse buttons during recording

### General
- User-friendly interface with tabbed organization
- Emergency stop with ESC key
- PyAutoGUI failsafe (move mouse to corner to stop)
- Click counter
- Error handling and user feedback

## Installation

### From Release
1. Download the latest release from the releases page
2. Extract the zip file
3. Run `OctoAutoClicker.exe`

### From Source
1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Run the application:
```bash
python op_autoclicker.py
```

## Building from Source
To create an executable:
```bash
pyinstaller AutoClicker.spec
```
The executable will be created in the `dist` directory.

## Usage

### Auto Clicker Tab
1. Set your desired click interval
2. Choose mouse button and click type
3. Select repeat options (continuous or fixed number)
4. Choose click position (current or custom coordinates)
5. Press F6 or click "Start" to begin
6. Press F6 again or "Stop" to end

### Macro Recording Tab
1. Click "Start Recording" or press F7
2. Perform the actions you want to record
3. Click "Stop Recording" or press F7 again
4. Enter a name for your macro
5. Click "Save Macro"
6. To play: select a macro and click "Play"

### Hotkeys
- F6: Start/Stop auto-clicking
- F7: Start/Stop macro recording
- ESC: Emergency stop (stops both clicking and macro playback)

## Safety Features
- Move mouse to any corner to stop (PyAutoGUI failsafe)
- ESC key emergency stop
- Error handling for invalid inputs
- Thread-safe implementation

## Requirements
- Windows 10/11
- Python 3.7+ (if running from source)
- Dependencies listed in requirements.txt

## Version History
- v1.0.1: Initial release with auto-clicking and macro recording functionality

## License
MIT License

## Acknowledgments
Built with:
- PyAutoGUI
- Tkinter
- Mouse
- Keyboard 