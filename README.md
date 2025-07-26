# Monkeytype Auto Typer

This project provides a user-friendly GUI to automate typing on [Monkeytype](https://monkeytype.com/) using Python, Selenium, PyAutoGUI, and CustomTkinter.

## Features

-   Launches Chrome with automation warnings suppressed
-   Graphical interface for all controls (start/stop bot, open/close browser, adjust typing speed)
-   Supports both fast (bot) and human-like (natural) typing modes
-   Automatically fetches and types words as long as the timer is running
-   Hotkey (Ctrl+Alt+T) to start typing for each test
-   Responsive stopping when timer reaches 00:00
-   Instructions and status updates built into the GUI

## Requirements

-   Python 3.x
-   Google Chrome browser
-   ChromeDriver (compatible with your Chrome version)

## Installation

1. Clone this repository or download the files.
2. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```
3. Download the correct version of ChromeDriver and ensure it is in your PATH.

## Usage

1. Run the script:
    ```sh
    python main.py
    ```
2. Use the GUI to:
    - Open the browser
    - Start the bot (enables hotkey listening)
    - Press `Ctrl+Alt+T` to begin auto-typing for each test
    - Adjust typing speed and select typing mode (Bot or Human)
    - Stop the bot or close all browsers as needed

## Notes

-   The script uses Selenium to control Chrome and PyAutoGUI to simulate typing.
-   Make sure the Chrome window is focused when typing starts.
-   Use at your own risk; automating typing tests may violate the terms of service of some websites.

## License

MIT
