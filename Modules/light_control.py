#This Module can be used to control any tuya compatible smart light
import tinytuya

# Tuya Cloud Credentials (from your configuration)
DEVICE_ID = "bf429e6c5b54bd43f3xpzz"  # Your device ID
ACCESS_ID = "rde3nw5sswh9yvgvcqdu"     # Your Tuya IoT Access ID
ACCESS_SECRET = "8b30deba0a8d416eb00762060ae70d14"  # Your Tuya IoT Access Secret
API_REGION = "eu"  # Change to "us", "eu", "cn", "in" as appropriate

# Initialize Tuya Cloud API
cloud = tinytuya.Cloud(apiRegion=API_REGION, apiKey=ACCESS_ID, apiSecret=ACCESS_SECRET)

# Global state: store the current color settings.
# Default is white at full brightness.
current_color = {"h": 0, "s": 0, "v": 1000}

def turn_on():
    payload = {"commands": [{"code": "switch_led", "value": True}]}
    response = cloud.sendcommand(str(DEVICE_ID), payload)
    print("Turn On Response:", response)

def turn_off():
    payload = {"commands": [{"code": "switch_led", "value": False}]}
    response = cloud.sendcommand(str(DEVICE_ID), payload)
    print("Turn Off Response:", response)

def set_color(hue=0, saturation=1000, brightness=1000):
    """
    Sets the light color using HSB values and updates the global state.
    :param hue: 0-360 (e.g., 0 = Red, 120 = Green, 240 = Blue)
    :param saturation: 0-1000 (0 = white, 1000 = full color)
    :param brightness: 0-1000 (0 = dark, 1000 = bright)
    """
    global current_color
    current_color = {"h": hue, "s": saturation, "v": brightness}
    payload = {"commands": [{"code": "colour_data", "value": current_color}]}
    response = cloud.sendcommand(str(DEVICE_ID), payload)
    print(f"Set Color (H:{hue}, S:{saturation}, B:{brightness}) Response:", response)

def adjust_brightness(brightness=500):
    """
    Adjusts only the brightness while preserving the current hue and saturation.
    :param brightness: 0-1000 (0 = dark, 1000 = bright)
    """
    global current_color
    current_color["v"] = brightness
    payload = {"commands": [{"code": "colour_data", "value": current_color}]}
    response = cloud.sendcommand(str(DEVICE_ID), payload)
    print(f"Adjusted Brightness (using colour_data, {brightness}/1000) Response:", response)

def set_mode(mode="colour"):
    """
    Changes the light mode.
    :param mode: Options include "white", "colour", "scene", "music"
    """
    payload = {"commands": [{"code": "work_mode", "value": mode}]}
    response = cloud.sendcommand(str(DEVICE_ID), payload)
    print(f"Set Mode to {mode} Response:", response)