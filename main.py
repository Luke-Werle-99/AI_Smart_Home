import time, subprocess, wave, os, re
import speech_recognition as sr
from openai import OpenAI
import threading
from gtts import gTTS
import pygame
import os
import subprocess
import warnings
import sys
import traceback
from Modules import music_player
import sounddevice

# Redirect stderr to suppress ALSA and JACK errors
sys.stderr = open(os.devnull, 'w')

import speech_recognition as sr


# Suppress ALSA and PulseAudio warnings
os.environ["SDL_AUDIODRIVER"] = "pulse"  # Use ALSA driver explicitly
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"  # Suppress pygame startup message
os.environ["ALSA_LOG_LEVEL"] = "none"  # Suppress ALSA messages
warnings.filterwarnings("ignore")  # Suppress other warnings

#Setting API-Key
client = OpenAI(
    api_key="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"
)

# Wake word
WAKE_WORD = "assistant"

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

    #Wait for playback to finish
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

    # Clean up the temporary file
    os.remove(audio_file)

# Function to listen to user input
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone(device_index=1) as source:
        print("Listening...")
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio)
        print(f"You said: {command}")
        return command.lower()
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        speak("Sorry, I couldn't connect to the speech service.")
        return ""

# Function to detect wake word
def detect_command(input, keyword):
    return re.search(rf"\b{keyword}\b", input)

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

def handle_voice_command(user_input):
    #Handle a voice command by routing it to the appropriate module.
    if detect_command(user_input, "play music"):
        print("Music command detected. Opening music_player module...")
        song_query = user_input.replace("play music", "").strip()
        if song_query:
            music_player.play_song(song_query)
        else:
            speak("Please specify the song you'd like to play.")
    elif detect_command(user_input, "calendar"):
        print("Opening Calendar module...")
        #calendar_module.create_entry(command)  # Example function in calendar_module
    else: # prompting ChatGPT
        response = ask_openai(user_input)
        speak(response)

# Main function
def voice_assistant():
    speak(f"Hello Luke. I am your voice assistant. Say {WAKE_WORD} to wake me up.")
    while True:
        wake_up = listen()
        if detect_command(wake_up, WAKE_WORD):
            print("Wake word detected")
            speak("Yes, how can I help you?")
            user_input = listen()
            if user_input:
                handle_voice_command(user_input)
        time.sleep(1)

# Start the assistant in a separate thread
assistant_thread = threading.Thread(target=voice_assistant)
assistant_thread.start()
