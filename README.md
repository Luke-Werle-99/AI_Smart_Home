# AI Smart Home 

**AI Smart Home** is an open source smart home system developed in Python, featuring an AI-powered voice assistant (powered by GPT4o) and a modular architecture. The system integrates various functionalities such as music playback, diary entry creation and playback, sensor readings (temperature, humidity, battery status), alarm clock management, light control (via Tinytuya), and a web console for remote monitoring and control.

This project was developed as part of a Bachelor’s degree in Computer Science and is primarily designed to run on a Raspberry Pi 4B, though it can be adapted to work with other hardware setups.

---

## Table of Contents

- [Features](#features)
- [Technologies](#technologies)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [File Structure](#file-structure)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Future Improvements](#future-improvements)
- [About](#about)

---

## Features

- **Voice Assistant:**
  - Activated with a wake word (default is "assistant").
  - Processes voice commands and integrates with OpenAI GPT4o for intelligent responses.

- **Music Player:**
  - Streams and plays music from YouTube using `yt-dlp` and `mpv`.
  - Example command: "Play music [Song Name]".

- **Diary Module:**
  - Records diary entries via audio.
  - Converts recordings to text and saves both audio and text files with the current date.
  - Supports playback of diary entries.

- **Sensor Module (Hygrometer):**
  - Retrieves temperature, humidity, and battery status from a Bluetooth-enabled hygrometers from Govee.
  - Uses asynchronous BLE scanning with the `bleak` library.

- **Alarm Clock:**
  - Schedules and manages alarms using the `schedule` module.
  - Triggers alarms with voice notifications and custom alarm sounds.
  - Commands for setting and deleting alarms.

- **Light Control:**
  - Controls Tuya-compatible smart lights via the Tuya Cloud API (using `tinytuya`).
  - Supports adjusting color, brightness, and operating mode.

- **Web Console:**
  - Provides a web interface for remote system monitoring.

---

## Technologies

- **Programming Language:** Python 3.11
- **Libraries:**
  - `speech_recognition` for voice command detection.
  - `pygame` for audio playback and TTS.
  - `gTTS` for text-to-speech conversion.
  - `yt-dlp` and `mpv` for streaming and playing YouTube audio.
  - `bleak` for Bluetooth Low Energy (BLE) scanning.
  - `tinytuya` for controlling Tuya-compatible devices.
  - `OpenAI` for GPT4o integration.
- **Target Hardware:**
  - Raspberry Pi 4B (primarily)
  - Razer Seiren Mini Microphone
  - Soundcore Boom 2 Bluetooth Speaker
  - Govee H5075

## Installation

### Prerequisites

- A Raspberry Pi 4B running Raspberry Pi OS (or compatible hardware).
- Python 3.11 installed.
- Miniforge3 (or an alternative Python environment manager).
- Internet access for API queries and music streaming.
  
### Installation Steps

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/Luke-Werle-99/AI_Smart_Home.git
    cd AI_Smart_Home
    ```

2. **Create and Activate a Python Environment:**
    ```bash
    conda create -n AI_Smart_Home python=3.11
    conda activate AI_Smart_Home
    ```

3. **Install Dependencies:**
    ```bash
    cd installation
    sh install_dependencies.sh
    sh install_libraries.sh
    ```

4. **Configure API Keys:**
    - Create or edit the `.env` file in the project root:
      ```env
      OPENAI_API_KEY=your_openai_api_key_here
      ```
    - Also ensure that any other required configurations (e.g., Tuya credentials) in the corresponding modules are correctly set.

---

## Configuration

- **Environment Variables:**  
  The `.env` file contains sensitive data such as the OpenAI API key. Make sure this file is configured correctly.
- **Audio Settings:**  
  - Ensure the correct audio devices (microphone and speakers) are selected.
  - On the Raspberry Pi, additional configuration (e.g., PulseAudio settings) might be necessary.
- **Bluetooth & Sensors:**  
  - Enable Bluetooth and ensure your Govee hygrometer is properly paired.
- **Tuya Cloud:**  
  - Update your Tuya Cloud credentials (DEVICE_ID, ACCESS_ID, ACCESS_SECRET, API_REGION) in the relevant modules.

---

## Usage

1. **Start the Assistant:**
    ```bash
    python main.py
    ```
    The voice assistant will start and listen for the wake word (default "assistant").

2. **Available Voice Commands:**
    - **Wake the Assistant:** "assistant" (optionally followed by a command).
    - **Play Music:** "Play music [Song Name]".
    - **Diary Functions:** "create diary" to start a new diary entry, "read diary" to playback an entry.
    - **Sensor Readings:** "temperature", "humidity", or "battery" to fetch current sensor values.
    - **Alarm Clock:** "set alarm" to create an alarm and "delete alarm" to remove an alarm.
    - **Light Control:** "set light" followed by commands such as "on", "off", color names (e.g., "red", "blue"), or brightness percentages.
    - **General Queries:** All other queries are forwarded to OpenAI GPT4o.

3. **Systemd Service (Optional):**  
   To have the assistant start automatically on system boot, set up a systemd service as described below.
   
### Example Interaction
1. Say "Assistant" to wake up the system.
2. Use commands like:
   - "Play music Believer by Imagine Dragons."
     
You also wake the system and input your command in one sentence like: "Assistant Play music Believer by Imagine Dragons"


---

Alternatively, you can configure it to start automatically using a systemd service file (see below).

## Systemd Service Setup
To run the assistant on system startup:
1. Create a systemd service file:
   ```bash
   sudo nano /etc/systemd/system/autostart.service
   ```
2. Add the following content:
   ```ini
   [Unit]
   Description=Start AI Smart Home Assistant
   After=sound.target bluetooth.target network.target

   [Service]
   User=your-username
   WorkingDirectory=/home/your-username/ai-smart-home
   ExecStart=/home/your-username/miniforge3/condabin/conda run -n AI_Smart_Home --no-capture-output python main.py
   Environment="XDG_RUNTIME_DIR=/run/user/1000"
   Environment="DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus"
   Restart=on-failure

   [Install]
   WantedBy=multi-user.target
   ```
3. Enable and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable autostart.service
   sudo systemctl start autostart.service
   ```
4. Additinally you can set up automatic bluetooth pairing in case you are using a bluetooth speaker like this:
    ```bash
        echo "Connecting to Bluetooth speaker..."
        for i in {1..5}; do
        echo "Attempt $i: Connecting to F4:2B:7D:29:50:41..."
        bluetoothctl -- connect F4:2B:7D:29:50:41 && break
        sleep 5
        done
    ```

## File Structure
```
AI_Smart_Home/
├── main.py
├── Modules/
│ ├── init.py
│ ├── music_player.py
│ ├── diary.py
│ ├── hygrometer.py
│ ├── alarm_clock.py
│ ├── light_control.py
│ └── web_console.py
├── diary_entries/
│ ├── YYYY-MM-DD.txt
│ ├── YYYY-MM-DD.wav
├── installation/
│ ├── install_dependencies.sh
│ └── install_libraries.sh
├── .env
└── README.md
```

## Troubleshooting

## Troubleshooting

- **Audio Playback:**  
  - Ensure `pygame` is properly initialized.
  - If you encounter issues in subprocesses, consider using threads instead of processes to share the Pygame mixer context.
  
- **Microphone Issues:**  
  - Verify the device index using `arecord -l` (on Linux) and adjust the settings in the `listen()` function if needed.
  - Adjust parameters like `energy_threshold` or `dynamic_energy_threshold` in the `speech_recognition` library.

- **Bluetooth and Sensor Readings:**  
  - Ensure Bluetooth is enabled and your hygrometer is paired correctly.
  - Watch for potential conflicts between asynchronous BLE scans (using `bleak`) and other async operations.

- **Bluetooth Speaker Issues**:
  - Ensure the speaker is paired and set as the default audio sink using:
     ```bash
     pactl set-default-sink [sink-name]
     ```
     
- **OpenAI API:**  
  - Confirm that your API key is correct and that you have an active network connection.
  - Check logs for any error messages related to API requests.

- **General Debugging:**  
  - Monitor console logs to identify error messages.
  - Review the specific module in the `Modules/` directory for module-related issues.


## Contributing

Contributions to AI Smart Home are welcome!

To contribute:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes with clear, descriptive messages.
4. Open a Pull Request describing your changes and the benefits they provide.

For any questions or suggestions, please open an issue on the GitHub repository.

## License
This project is licensed under the MIT License.

---

## About

**AI Smart Home** was developed by **Luke Werle** as a Bachelor’s degree project in Computer Science. The aim is to provide a privacy-friendly and modular alternative to commercial smart home systems. Feedback and suggestions for improvements are always welcome!

---

Enjoy your AI Smart Home Assistant! 

