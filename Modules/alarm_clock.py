import schedule
import time
import threading
import pygame
import os

# This alarm clock  module can be used to set up regular alarms with custom names as a reminder and to delete them
pygame.mixer.init()
alarms = {}

def validate_time_format(alarm_time):
    try:
        time.strptime(alarm_time, "%H:%M")
        return True
    except ValueError:
        return False

def play_alarm_sound():
    alarm_sound_path = os.path.join("data", "alarm_sound.mp3")
    if os.path.exists(alarm_sound_path):
        try:
            pygame.mixer.music.load(alarm_sound_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
        except Exception as e:
            print(f"Error playing alarm sound: {e}")
    else:
        print("Alarm sound file not found.")

def trigger_alarm(name, speak):
    print(f"Triggering alarm: {name}")
    speak(f"Alarm '{name}' is ringing!")
    time.sleep(0.5)  # short pause between announcements
    speak(f"Alarm '{name}' is ringing!")
    play_alarm_sound()

def set_alarm(name, alarm_time, frequency, speak):
    if not validate_time_format(alarm_time):
        speak("Invalid time format. Please use HH:MM (24-hour format).")
        return

    if name in alarms:
        speak(f"Alarm with name '{name}' already exists.")
        return

    def add_schedule():
        if frequency in ["once", "daily"]:
            schedule.every().day.at(alarm_time).do(trigger_alarm, name, speak).tag(name)
        else:
            weekdays = {
                "monday": schedule.every().monday,
                "tuesday": schedule.every().tuesday,
                "wednesday": schedule.every().wednesday,
                "thursday": schedule.every().thursday,
                "friday": schedule.every().friday,
                "saturday": schedule.every().saturday,
                "sunday": schedule.every().sunday,
            }
            day_freq = frequency.lower()
            if day_freq not in weekdays:
                speak(f"Invalid frequency: {frequency}. Choose from 'once', 'daily', or a specific weekday.")
                return
            weekdays[day_freq].at(alarm_time).do(trigger_alarm, name, speak).tag(name)

    add_schedule()
    alarms[name] = {
        "time": alarm_time,
        "frequency": frequency,
    }
    speak(f"Alarm '{name}' set for {alarm_time} with frequency '{frequency}'.")
    print(f"Scheduler thread is_alive: {scheduler_thread.is_alive()}")

def delete_alarm(name, speak):
    if name not in alarms:
        speak(f"No alarm found with name '{name}'.")
        return

    schedule.clear(name)
    del alarms[name]
    speak(f"Alarm '{name}' has been deleted.")

def setup_alarm(speak, listen, stop_flag):
    # Request alarm name until valid input is given.
    while True:
        speak("Please provide the alarm name:")
        name = listen().strip()
        if name:
            break
        else:
            speak("Alarm name cannot be empty. Please try again.")

    # Request alarm time until exactly 4 digits are provided.
    while True:
        speak("Please provide the alarm time as exactly 4 digits (e.g., 1355:")
        alarm_time_input = listen().strip()
        digits = "".join(filter(str.isdigit, alarm_time_input))
        if len(digits) == 4:
            normalized_time = digits[:2] + ":" + digits[2:]
            if validate_time_format(normalized_time):
                alarm_time = normalized_time
                break
            else:
                speak("Invalid time format.")
        else:
            speak("Please enter exactly 4 digits for the time.")

    # Allowed frequencies: once, daily, or a specific weekday.
    allowed_frequencies = [
        "once", "daily",
        "monday", "tuesday", "wednesday", "thursday",
        "friday", "saturday", "sunday"
    ]
    while True:
        speak("Please provide the frequency for the alarm (once, daily, or a specific weekday):")
        frequency = listen().strip().lower()
        if frequency in allowed_frequencies:
            break
        else:
            speak("Invalid frequency.")

    set_alarm(name, alarm_time, frequency, speak)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()
