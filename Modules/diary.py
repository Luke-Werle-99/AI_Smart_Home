import os
import datetime
import wave
import time
import pygame
from speech_recognition import Recognizer, AudioFile, UnknownValueError, Microphone
from main import speak, listen
from dateutil import parser

# Folder for diary entries
DIARY_FOLDER = os.path.join(os.getcwd(), "diary_entries")
if not os.path.exists(DIARY_FOLDER):
    os.makedirs(DIARY_FOLDER)

# Function for audio recording
def record_audio(filename):
    recognizer = Recognizer()

    speak("You can now start recording your diary entry. Say 'entry end' when you are done.")

    audio_data = []
    with Microphone() as source:  # Adjust `device_index` if needed
        recognizer.adjust_for_ambient_noise(source)
        print("Recording started...")
        while True:
            try:
                audio = recognizer.listen(source)
                command = recognizer.recognize_google(audio, language="en-US").lower()
                if "entry end" in command:
                    speak("Recording stopped")
                    print("Recording stopped")
                    break
                else:
                    audio_data.append(audio.frame_data)
            except UnknownValueError:
                pass

    # Save audio
    with wave.open(filename, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)  # Assuming 16-bit PCM
        wav_file.setframerate(44100)
        wav_file.writeframes(b"".join(audio_data))

# Function to create a diary entry
def create_entry():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    audio_file = os.path.join(DIARY_FOLDER, f"{today}.wav")
    text_file = os.path.join(DIARY_FOLDER, f"{today}.txt")

    # Start recording
    record_audio(audio_file)

    # Convert audio to text
    recognizer = Recognizer()
    try:
        with AudioFile(audio_file) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio, language="en-US")
    except UnknownValueError:
        text = "No speech recognized."

    # Save text
    with open(text_file, "w", encoding="utf-8") as file:
        file.write(text)

    speak(f"Your entry has been saved under today's date: {today}.")

# Function to read or play a diary entry
def read_entry():
    speak("Please state the date of the entry, for example, 'December 17th, 2023' or '17th December 2023'.")
    date_spoken = listen()

    if not date_spoken:
        speak("I couldn't understand the date.")
        return

    try:
        # Attempt to parse the spoken date
        date_object = parser.parse(date_spoken)
        date = date_object.strftime("%Y-%m-%d")
        speak(f"Searching for the entry dated {date}.")
    except ValueError:
        speak("I couldn't understand the date format. Please try again.")
        return

    audio_file = os.path.join(DIARY_FOLDER, f"{date}.wav")
    text_file = os.path.join(DIARY_FOLDER, f"{date}.txt")

    if os.path.exists(audio_file) and os.path.exists(text_file):
        speak("Should I read the entry as text or play the audio recording?")
        choice = listen()

        if "text" in choice.lower():
            with open(text_file, "r", encoding="utf-8") as file:
                text = file.read()
            speak("Here is your entry:")
            speak(text)
        elif "audio" in choice.lower():
            pygame.mixer.init()
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
        else:
            speak("I didn't understand your choice.")
    else:
        speak("There is no entry for that date.")

