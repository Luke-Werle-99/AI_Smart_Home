import time, subprocess, wave, os, re, sounddevice, warnings, threading
import speech_recognition as sr
from openai import OpenAI
import multiprocessing
from gtts import gTTS
import pygame
import os
from dotenv import load_dotenv
import traceback
from Modules import music_player, diary, hygrometer, alarm_clock, light_control

# Redirect stderr to suppress ALSA and JACK errors
#sys.stderr = open(os.devnull, 'w')
#warnings.filterwarnings("ignore")  # Suppress other warnings

# Suppress ALSA and PulseAudio warnings
os.environ["SDL_AUDIODRIVER"] = "pulse"  # Use ALSA driver explicitly
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"  # Suppress pygame startup message
os.environ["ALSA_LOG_LEVEL"] = "none"  # Suppress ALSA messages

#Load the environment variables from the .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
# Debugging: Print the API key to verify
if api_key:
    print("API Key loaded successfully!")
else:
    print("Error: API Key not loaded!")

#Setting API-Key
client = OpenAI(
    api_key=api_key
)
#initializing thread dictionary
process_dict = {}

# Wake word
WAKE_WORD = "assistant"

stoppable_processes = {
    "play_music",
    "diary_read_entry",
    "diary_create_entry",
    "hygrometer_read_humidity",
    "hygrometer_read_temperature",
    "ask_openai",

}
stop_flag = multiprocessing.Value("b", False)

#Optimize the speech_recognition Library Settings
#sr.energy_threshold = 50  # Default is around 300; increase for noisy environments
sr.dynamic_energy_threshold = True  # Automatically adjust during runtime
sr.pause_threshold = 1.0  # Default is 0.8; increase to 1.0 or higher

# Initialize pygame mixer
pygame.mixer.pre_init(44100, -16, 2, 512)  # Standard audio settings
pygame.init()

# Function to play TTS output
def speak(text):
    print(f"Assistant: {text}")
    tts = gTTS(text=text, lang="en")
    audio_file = "output.mp3"
    tts.save(audio_file)

    #subprocess.run(['mpv', '--no-video', audio_file])

    #Play the audio using pygame
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()

    # Wait for playback to finish, but check for stop flag periodically
    while pygame.mixer.music.get_busy():
        # Check if the global stop flag is set
        if stop_flag.value:
            print("Stop flag detected. Stopping playback.")
            pygame.mixer.music.stop()
            stop_flag.value = False  # Reset for future playback
            break
        time.sleep(0.1)

    #Clean up the temporary file
    if os.path.exists(audio_file):
             os.remove(audio_file)

def speak_async(text):
    threading.Thread(target=speak, args=(text,), daemon=True).start()

# Function to listen to user input
def listen():
    recognizer = sr.Recognizer()
    try:
        mic = sr.Microphone()
        with mic as source:
            print("Listening...")
            audio = recognizer.listen(source)
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
        return command.lower()
    except sr.UnknownValueError:
            print("No Input Detected")
            return ""
    except sr.RequestError:
            speak("Could not connect to the speech service")
            return ""

def detect_command(input_text, keyword):
    if keyword in input_text:
        return True, input_text[input_text.find(keyword)+len(keyword):]
    return False, None

# Function to handle OpenAI GPT query
def ask_openai(prompt):
    print("Asking OpenAI...")

    try:
        completion = client.chat.completions.create(
            model="gpt-4o",  # Use "gpt-4" or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            )

        #print(f"FULL API Response: {completion}")
        response = completion.choices[0].message.content.strip()
        #print response to console
        print("Response from OpenAI:", response)

        return response
    except Exception:
        traceback.print_exc()
        return "Error when asking OpenAI."


# This function used to mitigate having to call speak in the subprocess
def ask_openai_worker(prompt, output_queue):
    response = ask_openai(prompt)
    output_queue.put(response)

def stop_processes(process_names):
    stop_flag.value = True  # Signal all tasks (including audio) to stop
    for process_name in process_names:
        existing_process = process_dict.get(process_name)
        if existing_process and existing_process.is_alive():
            print(f"Stopping process: {process_name}")
            existing_process.terminate()
            existing_process.join()
    # Only reset the flag if no audio is playing.
    if not pygame.mixer.music.get_busy():
        stop_flag.value = False

def handle_voice_command(user_input):
    # Handle voice commands by routing it to the appropriate module.
    play_music_bool, song_name = detect_command(user_input, "play music")
    if play_music_bool:
        print("Music command detected. Opening music_player module...")
        if song_name:
            stop_processes(stoppable_processes)

            new_process = multiprocessing.Process(
                target=music_player.play_song,
                args=(song_name, stop_flag)
            )
            process_dict['play_music'] = new_process
            new_process.start()
        else:
            speak("Please specify the song you'd like to play.")
        return

    diary_entry_bool, diary_command = detect_command(user_input, "diary")
    if diary_entry_bool:
        print("Diary entry command detected. Starting a new diary entry...")
        stop_processes(stoppable_processes)

        new_process = multiprocessing.Process(
            target=diary.create_entry,
            args=(speak,)
        )
        process_dict['diary_create_entry'] = new_process
        new_process.start()
        return

    read_diary_bool, read_diary_command = detect_command(user_input, "read diary")
    if read_diary_bool:
        print("Read diary entry command detected. Fetching the diary entry...")
        stop_processes(stoppable_processes)

        new_process = multiprocessing.Process(
            target=diary.read_entry,
            args=(speak,)
        )
        process_dict['diary_read_entry'] = new_process
        new_process.start()
        return

    read_temperature_bool, read_temperature_command = detect_command(user_input, "temperature")
    if read_temperature_bool:
        print("Read temperature command detected. Fetching temperature...")
        stop_processes(stoppable_processes)

        new_process = multiprocessing.Process(
            target=hygrometer.read_temperature,
            args=(speak,)
        )
        process_dict['hygrometer_read_temperature'] = new_process
        new_process.start()
        return

    read_humidity_bool, read_humidity_command = detect_command(user_input, "humidity")
    if read_humidity_bool:
        print("Read humidity command detected. Fetching the humidity...")
        stop_processes(stoppable_processes)

        new_process = multiprocessing.Process(
            target=hygrometer.read_humidity,
            args=(speak,)
        )
        process_dict['hygrometer_read_humidity'] = new_process
        new_process.start()
        return

    set_alarm_bool, set_alarm_command = detect_command(user_input, "set alarm")
    if set_alarm_bool:
        if set_alarm_command:
            print("Setting Up Alarm...")
            stop_processes(stoppable_processes)
            try:
                # Parse input details
                details = set_alarm_command.split(",")

                # Check if all required fields are provided
                if len(details) < 3:
                    raise ValueError("Incomplete input. Please specify the alarm details in the format: alarm name, alarm time with number for the hour and one for minutes, and the frequency as in daily, weekly, monthly, or by naming a weekday.")

                name = details[0].strip()
                alarm_time = details[1].strip()
                frequency = details[2].strip()

                # Start a new process to set the alarm
                new_process = multiprocessing.Process(
                    target=alarm_clock.set_alarm, args=(name, alarm_time, frequency, speak)
                )
                process_dict['set_alarm'] = new_process
                new_process.start()

            except ValueError as ve:
                speak(str(ve))
            except Exception as e:
                speak("An unexpected error occurred while setting the alarm.")
                print(f"Error: {e}")
        speak("Please provide the alarm name, time, and frequency in the format: 'name, HH:MM, frequency'.")
        return

    delete_alarm_bool, delete_alarm_command = detect_command(user_input, "delete alarm")
    if delete_alarm_bool:
        print("Deleting Alarm...")
        stop_processes(stoppable_processes)
        alarm_name = delete_alarm_command.strip()

        new_process = multiprocessing.Process(
            target=alarm_clock.delete_alarm,
            args=(alarm_name, speak)
        )
        process_dict['delete_alarm'] = new_process
        new_process.start()

        return

    set_light_bool, light_command = detect_command(user_input, "set light")
    if set_light_bool:
        print("Light control command detected.")
        stop_processes(stoppable_processes)
        # Process additional keywords; convert to lowercase and remove the word "brightness"
        params = light_command.lower().replace("brightness", "")

        # If the user explicitly says "on" or "off"
        if "on" in params:
            light_control.turn_on()
        elif "off" in params:
            light_control.turn_off()
        else:
            # Expanded mapping for common colors
            color_map = {
                "red": {"h": 0, "s": 1000},
                "green": {"h": 120, "s": 1000},
                "blue": {"h": 240, "s": 1000},
                "yellow": {"h": 60, "s": 1000},
                "purple": {"h": 270, "s": 1000},
                "pink": {"h": 330, "s": 1000},
                "white": {"h": 0, "s": 0},  # White: saturation 0
                "orange": {"h": 30, "s": 1000},
                "cyan": {"h": 180, "s": 1000},
                "magenta": {"h": 300, "s": 1000}
            }
            selected_color = None
            for color in color_map:
                if color in params:
                    selected_color = color
                    break
            # Look for a brightness percentage, e.g. "50 percent" or "50%"
            import re
            brightness_match = re.search(r'(\d+)\s*(?:percent|%)', params)
            brightness_value = None
            if brightness_match:
                percent = int(brightness_match.group(1))
                brightness_value = int(percent / 100 * 1000)
            if selected_color:
                # If a color is specified, use that color mapping.
                hue = color_map[selected_color]["h"]
                saturation = color_map[selected_color]["s"]
                if brightness_value is None:
                    brightness_value = 1000  # Default full brightness
                light_control.set_color(hue=hue, saturation=saturation, brightness=brightness_value)
            elif brightness_value is not None:
                # If only brightness is specified, adjust brightness while preserving the current color.
                light_control.adjust_brightness(brightness=brightness_value)
            else:
                speak(
                    "I didn't understand the light command. Please say a color (red, blue, etc.) or specify a brightness percentage.")
        return

    stop_bool, stop_command = detect_command(user_input, "stop")
    if stop_bool:
        print("Stopping process...")
        stop_processes(stoppable_processes)
        return

    # Default: Send query to OpenAI
    stop_processes(stoppable_processes)

    result_queue = multiprocessing.Queue()
    new_process = multiprocessing.Process(
        target=ask_openai_worker,
        args=(user_input, result_queue),
    )
    process_dict['ask_openai'] = new_process
    new_process.start()

    response = result_queue.get()
    new_process.join()
    speak_async(response)

# Main function
def voice_assistant():
    speak(f"Hello Luke. I am your voice assistant. Say {WAKE_WORD} to wake me up.")
    while True:
        audio_input = listen()
        detected, command = detect_command(audio_input, WAKE_WORD)
        if detected:
            if not command:
                print("Wake word detected")
                speak("How can I help you?")
                command = listen()
            handle_voice_command(command)

if __name__ == '__main__':
    voice_assistant()
