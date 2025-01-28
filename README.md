# AI Smart Home 

## Description
The **AI Smart Home ** is a Python-based Smart Home System designed to offer an open source alternative to existing solutions which respects users privacy and offers an innovative GPT4o powered voice assistant. It integrates with various modules such as music playback, connecting to humidity and temperature sensors, and alarm, a diary functionality and many more. This project is designed to run on a Raspberry Pi 4B, using a Razer Seiren Mini microphone and a Soundcore Boom 2 Bluetooth speakers, but can easily be adapted to work with a variety of hardwar options. The assistant is built to recognize voice commands to control IoT devices and perform tasks, and provide AI powered voice assistance.

## Features

### 1. **Music Player**
- **Command**: "Play music [song name]"
- Plays music directly from YouTube using `yt-dlp` and `mpv`.

### 2. **Diary Module**
- **Command**: "Tagebuch Eintrag"
  - Starts a new diary entry by recording audio.
  - Converts audio to text and saves both formats with the current date in the `Tagebuch/` directory.
- **Command**: "Tagebuch Lesen"
  - Reads a diary entry by text-to-speech or plays the original audio file.

### 3. **Calendar (Future Implementation)**
- Manage events and schedules (placeholder).

### 4. **Integration with OpenAI GPT**
- Handles general queries and provides intelligent responses.

## Technologies Used
- **Python 3.11.2**
- **Libraries**:
  - `speech_recognition`: Voice recognition and command detection.
  - `pygame`: Text-to-speech audio playback.
  - `gTTS`: Text-to-speech conversion.
  - `yt-dlp`: Stream and download YouTube audio.
  - `pyaudio`/`sounddevice`: Audio input/output.
  - `OpenAI`: Integration for intelligent responses.
- **Hardware**:
  - Raspberry Pi 4B
  - Razer Seiren Mini microphone
  - Souncdore Boom 2 Bluetooth speakers

## Installation

### Prerequisites
1. Raspberry Pi 4B with Raspberry Pi OS.
2. Python 3 installed.
3. Miniforge3 for managing Python environments.

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/ai-smart-home.git
   cd ai-smart-home
   ```
2. Create and activate a Python environment:
   ```bash
   conda create -n AI_Smart_Home python=3.11
   conda activate AI_Smart_Home
   ```
3. Install dependencies:
   ```bash
   cd installation
   sh install_dependencies.sh
   sh install_libraries.sh
   ```
5. Set up your OpenAI API key by placing it in `.env`:
   ```bash
   sudo nano .env
   ```

### Running the Assistant
Run the program manually:
```bash
python main.py
```

Alternatively, configure it to start automatically using a systemd service file (see below).

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
ai-smart-home/
├── main.py
├── Modules/
│   ├── __innit__.py
│   ├── music_player.py
│   ├── diary.py
│   ├── hygrometer.py
├── diary_entries/
│   ├── 2023-12-17.txt
│   ├── 2023-12-17.wav
├── .env
└── README.md
```

## How to Use

### Available Commands
- **"Assistant"**: Activates the assistant.
- **"Play music [song name]"**: Plays music from YouTube.
- **"diary"**: Starts a new diary entry.
- **"read diary"**: Reads or plays a diary entry.
- **"current temperature"**: Requests sensors and outputs the current temperature.
- **"current humidity"**: Requests sensors and outputs the current relative humidity.

### Example Interaction
1. Say "Assistant" to wake up the system.
2. Use commands like:
   - "Play music Believer by Imagine Dragons."
     
You also wake the system and input your command in one sentence like: "Assistant Play music Believer by Imagine Dragons"

## Troubleshooting

### Common Issues
1. **Microphone Not Detected**:
   - Ensure the correct device index or name is set in `listen()`.
   - Run `arecord -l` to verify available devices.

3. **Bluetooth Speaker Issues**:
   - Ensure the speaker is paired and set as the default audio sink using:
     ```bash
     pactl set-default-sink [sink-name]
     ```

## Contributing
Feel free to fork this repository, open issues, and submit pull requests to improve the assistant.

## License
This project is licensed under the MIT License.

---

Enjoy your AI Smart Home Assistant! 🚀

