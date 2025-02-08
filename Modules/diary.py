import os
import datetime
import wave
import pygame
import time
from speech_recognition import Recognizer, UnknownValueError, Microphone, AudioData
import re
from dateutil import parser

# Define diary folder
DIARY_FOLDER = os.path.join(os.getcwd(), "Modules", "diary_entries")
if not os.path.exists(DIARY_FOLDER):
    os.makedirs(DIARY_FOLDER)

# Listen function (mocked for testing with `input`)
def listen():
    inp = input("You: ")
    return inp.strip().lower()

# Create a diary entry
def create_entry(speak, listen, stop_flag):
    now = datetime.datetime.now().strftime("%Y-%m-%d")  #  Only use YYYY-MM-DD (no timestamp)
    audio_filename = os.path.join(DIARY_FOLDER, f"{now}.wav")
    text_filename = os.path.join(DIARY_FOLDER, f"{now}.txt")

    #  Remove existing entry for today before saving a new one
    if os.path.exists(audio_filename):
        os.remove(audio_filename)
    if os.path.exists(text_filename):
        os.remove(text_filename)

    def record_audio_with_stop():
        recognizer = Recognizer()
        recognizer.dynamic_energy_threshold = True
        speak("You may now record your diary entry. Say 'entry end' or 'finished' to stop recording.")
        frames = []
        try:
            with Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                speak("Recording started.")
                while True:
                    if stop_flag.value:  # Check the stop flag
                        speak("Recording stopped.")
                        return None  # Exit without saving audio
                    try:
                        audio = recognizer.listen(source, phrase_time_limit=10)
                        recognized_text = recognizer.recognize_google(audio, language="en-US").lower()
                        print("Recognized:", recognized_text)

                        # Stop recording if termination phrase is detected
                        if "entry end" in recognized_text or "diary end" in recognized_text or "finished" in recognized_text:
                            speak("Recording ended.")
                            break

                        # Append raw audio data
                        frames.append(audio.get_raw_data())
                        print(f"Frames collected: {len(frames)}")
                    except UnknownValueError:
                        print("No speech detected.")
                    except Exception as ex:
                        speak("Error during recording.")
                        print("Error:", ex)
                        break
        except Exception as ex:
            speak("Could not access the microphone.")
            print("Microphone error:", ex)
            return None

        return frames

    # Record audio
    frames = record_audio_with_stop()
    if not frames:  # If recording was stopped or no audio was captured
        return

    # Save the recorded audio to a WAV file
    try:
        with wave.open(audio_filename, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(44100)
            wf.writeframes(b"".join(frames))
        print("Audio saved to", audio_filename)
    except Exception as ex:
        speak("Error saving audio file.")
        print("Error writing WAV file:", ex)
        return

    # Transcribe audio to text
    recognizer = Recognizer()
    try:
        with wave.open(audio_filename, "rb") as wf:
            audio_data = AudioData(wf.readframes(wf.getnframes()), 44100, 2)
            text = recognizer.recognize_google(audio_data, language="en-US")
    except UnknownValueError:
        text = "No speech recognized."
    except Exception as e:
        text = f"Error during speech recognition: {e}"

    # Save text transcription
    try:
        with open(text_filename, "w", encoding="utf-8") as f:
            f.write(text)
        speak(f"Your diary entry for {now} has been saved.")
    except Exception as e:
        speak(f"Error saving diary entry: {e}")


def normalize_date_input(date_input):
    """
    Converts compact date formats (e.g., "0802 2025" or "08022025") into "08 02 2025".
    """
    date_input = date_input.replace("st", "").replace("nd", "").replace("rd", "").replace("th", "")

    # Match formats like "08022025" (DDMMYYYY) or "0802 2025" (DDMM YYYY)
    match = re.match(r"^(\d{2})(\d{2})(\d{4})$", date_input)  # Example: "08022025" → "08 02 2025"
    if match:
        return f"{match.group(1)} {match.group(2)} {match.group(3)}"

    match = re.match(r"^(\d{2})(\d{2})\s?(\d{4})$", date_input)  # Example: "0802 2025" → "08 02 2025"
    if match:
        return f"{match.group(1)} {match.group(2)} {match.group(3)}"

    return date_input  # Return unchanged if no match



def read_entry(speak, listen, stop_flag):
    speak("Please state the date of the entry, for example, 08 02 2025.")
    date_input = listen()

    if not date_input or stop_flag.value:
        speak("Operation canceled.")
        return

    try:
        #  Normalize and parse date
        date_input = normalize_date_input(date_input)
        date_obj = parser.parse(date_input, dayfirst=True)
        date_str = date_obj.strftime("%Y-%m-%d")  # Ensure format YYYY-MM-DD
        speak(f"Searching for the entry from {date_str}.")
    except Exception as e:
        speak("Invalid date format. Please try again.")
        print(f"Diary Module - Date parse error: {e}")  # Debugging output
        return

    #  Construct the expected filename
    audio_filename = os.path.join(DIARY_FOLDER, f"{date_str}.wav")

    #  Check if the file exists
    if not os.path.exists(audio_filename):
        speak(f"No audio entry found for {date_str}.")
        print(f"DEBUG: File not found - {audio_filename}")
        return

    #  Play the audio recording
    speak("Playing audio entry...")
    if not pygame.mixer.get_init():
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    pygame.mixer.music.load(audio_filename)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        if stop_flag.value:
            speak("Audio playback stopped.")
            pygame.mixer.music.stop()
            return
        time.sleep(0.1)




