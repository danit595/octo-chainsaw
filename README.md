# Auto Clicker

A Python-based autoclicker application with a graphical user interface.

## Features

- Simple and intuitive GUI
- Configurable click delay
- Start/Stop functionality
- Hotkey support (F6 to toggle)
- Status display

## Requirements

- Python 3.8 or higher
- Required packages (install using `pip install -r requirements.txt`):
  - PyQt6
  - pyautogui
  - keyboard

## Installation

1. Clone the repository
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python autoclicker.py
   ```

2. Enter the desired delay in milliseconds
3. Click the Start button or press F6 to begin autoclicking
4. Click Stop or press F6 again to stop

## Controls

- Start/Stop Button: Toggle autoclicking
- F6 Key: Hotkey to toggle autoclicking
- Delay Input: Set the time between clicks in milliseconds

## Note

This application requires appropriate permissions to simulate mouse clicks. Some applications or games may block automated input. 