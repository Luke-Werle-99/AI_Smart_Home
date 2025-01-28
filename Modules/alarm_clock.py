import schedule
import time
import threading
import pygame
import os

# Initialize pygame mixer for audio playback
pygame.mixer.init()

# Dictionary to store alarms
alarms = {}

# Helper function to validate time format (HH:MM)
def validate_time_format(alarm_time):
    try:
        time.strptime(alarm_time, "%H:%M")
        return True
    except ValueError:
        return False

# Helper function to play the alarm sound
def play_alarm_sound():
    alarm_sound_path = os.path.join("data", "alarm_sound.mp3")
    if os.path.exists(alarm_sound_path):
        pygame.mixer.music.load(alarm_sound_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
    else:
        print("Alarm sound file not found.")

# Helper function to trigger an alarm
def trigger_alarm(name, speak):
    speak(f"Alarm '{name}' is ringing!")
    play_alarm_sound()

# Function to set an alarm
def set_alarm(name, alarm_time, frequency, speak):
    if not validate_time_format(alarm_time):
        speak("Invalid time format. Please use HH:MM (24-hour format).")
        return

    if name in alarms:
        speak(f"Alarm with name '{name}' already exists.")
        return

    def add_schedule():
        if frequency == "once":
            schedule.every().day.at(alarm_time).do(trigger_alarm, name, speak).tag(name)
        elif frequency == "daily":
            schedule.every().day.at(alarm_time).do(trigger_alarm, name, speak).tag(name)
        elif frequency == "weekly":
            schedule.every().week.at(alarm_time).do(trigger_alarm, name, speak).tag(name)
        elif frequency == "monthly":
            speak("Monthly frequency is not directly supported by the 'schedule' library.")
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
                speak(f"Invalid frequency: {frequency}. Choose from 'once', 'daily', or specific weekdays.")
                return

            weekdays[day_freq].at(alarm_time).do(trigger_alarm, name, speak).tag(name)

    add_schedule()

    alarms[name] = {
        "time": alarm_time,
        "frequency": frequency,
    }

    speak(f"Alarm '{name}' set for {alarm_time} with frequency '{frequency}'.")

# Function to delete an alarm
def delete_alarm(name, speak):
    if name not in alarms:
        speak(f"No alarm found with name '{name}'.")
        return

    schedule.clear(name)
    del alarms[name]

    speak(f"Alarm '{name}' has been deleted.")

# Function to continuously run the scheduler
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Start the scheduler in a separate thread
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()
