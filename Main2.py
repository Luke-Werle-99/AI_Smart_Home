import time, subprocess, wave, os, re
import speech_recognition as sr
from openai import OpenAI

import multiprocessing
from gtts import gTTS
import pygame
import os
from dotenv import load_dotenv
import subprocess
import warnings
import sys
import traceback
from Modules import music_player, diary
import sounddevice

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
    "diary"
}

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

    subprocess.run(['mpv', '--no-video', audio_file])

    #Play the audio using pygame
    #pygame.mixer.music.load(audio_file)
    #pygame.mixer.music.play()

    #Wait for playback to finish
    #while pygame.mixer.music.get_busy():
    #    time.sleep(0.1)

    #Clean up the temporary file

    if os.path.exists(audio_file):
             os.remove(audio_file)

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
            return "UnknownValueError"
    except sr.RequestError:
            speak("Sorry, I couldn't connect to the speech service.")
            return ""

# Function to detect wake word
#def detect_command(input, keyword):
#    return re.search(rf"\b{keyword}\b", input)

def detect_command(input_text, keyword):
    if keyword in input_text:
        return True, input_text[input_text.find(keyword)+len(keyword):]
    return False, None

# Function to handle OpenAI GPT query
def ask_openai(prompt):
    print("Asking OpenAI...")
    # Using the new API structure with valid model name
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",  # Use "gpt-4" or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            )
        #print response to console

        print(f"FULL API Response: {completion}")
        print('***')
        print(completion.choices[0].message.content)

            # Extract and return the AI's response
        return completion.choices[0].message.content.strip()
    except Exception:
        traceback.print_exc()

def stop_processes(process_names):
    for process_name in process_names:
        existing_process = process_dict.get(process_name)
        if existing_process and existing_process.is_alive():
            print(f"Stopping process: {process_name}")
            existing_process.terminate()
            existing_process.join()
        else:
            print(f"No active process found for: {process_name}")

def handle_voice_command(user_input):
    # Handle a voice command by routing it to the appropriate module.
    if detect_command(user_input, "play music"):
        print("Music command detected. Opening music_player module...")
        song_query = user_input.replace("play music", "").strip()
        if song_query:
            # Check if there's an existing stoppable process
            stop_processes(stoppable_processes)

            # Start a new process for playing the song
            new_process = multiprocessing.Process(
                target=music_player.play_song,
                args=(song_query,)
            )
            process_dict['play_music'] = new_process
            new_process.start()
        else:
            speak("Please specify the song you'd like to play.")

    elif detect_command(user_input, "calendar"):
        print("Opening Calendar module...")
        # calendar_module.create_entry(command)  # Example function in calendar_module

    elif detect_command(user_input, "diary entry"):
        print("Diary entry command detected. Starting a new diary entry...")
        stop_processes(stoppable_processes)

        # Start a new process for playing the song
        new_process = multiprocessing.Process(
            target=diary.create_entry
        )
        process_dict['diary_create_entry'] = new_process
        new_process.start()

    elif detect_command(user_input, "read diary"):
        print("Read diary entry command detected. Fetching the diary entry...")
        stop_processes(stoppable_processes)

        # Start a new process for playing the song
        new_process = multiprocessing.Process(
            target=diary.read_entry
        )
        process_dict['diary_read_entry'] = new_process
        new_process.start()

    elif detect_command(user_input, "stop"):
        print("Stopping process...")
        stop_processes(stoppable_processes)

    else:  # Default: Send query to OpenAI
        response = ask_openai(user_input)
        speak(response)

# Main function
def voice_assistant():
    print(__name__)
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
        time.sleep(1)

if __name__ == '__main__':
    voice_assistant()
