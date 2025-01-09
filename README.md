# AI Smart Home Assistant

## Description
The **AI Smart Home Assistant** is a Python-based voice assistant designed to automate and simplify daily tasks. It integrates with various modules such as music playback, calendar management, and a diary functionality. This project is designed to run on a Raspberry Pi 4B, using a Razer Seiren Mini microphone and Bluetooth-connected speakers. The assistant is built to recognize voice commands, perform tasks, and provide audio feedback.

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
  - Bluetooth-connected speakers

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
   pip install -r requirements.txt
   ```
4. Ensure required directories exist:
   ```bash
   mkdir Tagebuch
   ```
5. Set up your OpenAI API key by replacing the placeholder in `main.py`:
   ```python
   client = OpenAI(
       api_key="your_openai_api_key"
   )
   ```
6. Ensure `yt-dlp`, `mpv`, and `pavucontrol` are installed:
   ```bash
   sudo apt install yt-dlp mpv pavucontrol
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

## File Structure
```
ai-smart-home/
├── main.py
├── Modules/
│   ├── music_player.py
│   ├── diary.py
├── Tagebuch/
│   ├── 2023-12-17.txt
│   ├── 2023-12-17.wav
└── README.md
```

## How to Use

### Available Commands
- **"Assistant"**: Activates the assistant.
- **"Play music [song name]"**: Plays music from YouTube.
- **"Tagebuch Eintrag"**: Starts a new diary entry.
- **"Tagebuch Lesen"**: Reads or plays a diary entry.

### Example Interaction
1. Say "Assistant" to wake up the system.
2. Use commands like:
   - "Play music Believer by Imagine Dragons."
   - "Tagebuch Eintrag."
   - "Tagebuch Lesen."

## Troubleshooting

### Common Issues
1. **Microphone Not Detected**:
   - Ensure the correct device index or name is set in `listen()`.
   - Run `arecord -l` to verify available devices.

2. **ALSA Errors**:
   - Ensure `pulseaudio` is running:
     ```bash
     pulseaudio --start
     ```
   - Add the user to the `audio` group:
     ```bash
     sudo usermod -aG audio your-username
     ```

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

