# HUD Project
by [B6Infinity](https://github.com/B6Infinity/)
## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Run on Startup](#run-on-startup)
- [Contributing](#contributing)


## Introduction
The **HUD Project** is a Python-based desktop application designed to provide a streamlined and efficient heads-up display (HUD) for monitoring system vitals such as CPU usage, RAM usage, and network activity. This project aims to enhance user experience by offering real-time data visualization in a lightweight and customizable interface.

## Features
- **Real-Time Updates**: Display live data with minimal latency.
- **Cross-Platform Support**: Compatible with Windows, macOS, and Linux.
- **Lightweight and Fast**: Optimized for performance and low resource usage.
- **Customizable Appearance**: Modify fonts, colors, and layout.

## Installation
Follow these steps to set up the project:

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/hud.git
    cd hud
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

   Ensure you have Python 3.8+ installed on your system.

3. Run the application:
    ```bash
    python system_panel.py
    ```

## Usage
Once the application is running, a frameless HUD panel will appear on your desktop. The panel displays:
- **CPU Usage**: Real-time percentage of CPU utilization.
- **RAM Usage**: Real-time percentage of RAM utilization.
- **Network Activity**: Upload and download speeds in KB/s or MB/s.

You can drag the panel to reposition it or minimize it to the system tray. Right-click on the panel for additional options such as toggling "Always on Top" or exiting the application.

## Run on Startup
To run this Python script automatically on startup, you can create a `.desktop` file:

1. Create a `.desktop` file in the `~/.config/autostart/` directory:
    ```bash
    mkdir -p ~/.config/autostart
    nano ~/.config/autostart/hud.desktop
    ```

2. Add the following content to the `hud.desktop` file:
    ```ini
    [Desktop Entry]
    Type=Application
    Exec=python3 /path/to/system_panel.py # Replace this with where you have saved the system_panel.py file
    Hidden=false
    NoDisplay=false
    X-GNOME-Autostart-enabled=true
    Name=HUD
    Comment=Start the HUD application on login
    ```

    Replace `/path/to/system_panel.py` with the full path to the `system_panel.py` file.

3. Save and close the file.

4. Ensure the script is executable:
    ```bash
    chmod +x /path/to/system_panel.py
    ```

The HUD application will now start automatically when you log in.

## Contributing
We welcome contributions! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix:
    ```bash
    git checkout -b feature-name
    ```
3. Commit your changes and push to your fork.
4. Submit a pull request with a detailed description of your changes.

Thank you for using the HUD Project!