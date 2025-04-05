# Auto Clicker

A simple and efficient Windows autoclicker application with a graphical user interface.

## Features

- Simple and intuitive GUI
- Configurable click delay
- Start/Stop functionality
- F6 hotkey to toggle clicking
- Status display
- No installation required

## Download

1. Go to [Releases](https://github.com/danit595/octo-chainsaw/releases)
2. Download `AutoClicker.exe` from the latest release
3. Run the executable (no installation required)

## Usage

1. Run `AutoClicker.exe`
2. Enter the desired delay in milliseconds
3. Click the Start button or press F6 to begin autoclicking
4. Click Stop or press F6 again to stop

## System Requirements

- Windows 10 or later
- No additional software required

## Notes

- Run as administrator if you encounter permission issues
- Some applications may block automated input
- The application is portable and can be run from any location

## Development

If you want to modify or build the application:

1. Clone the repository
2. Install Python 3.8 or higher
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python autoclicker.py
   ```
5. Build the executable:
   ```bash
   pyinstaller --onefile --windowed --name AutoClicker autoclicker.py
   ``` 