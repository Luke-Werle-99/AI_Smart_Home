from bleak import BleakScanner
import asyncio

# This Hygrometer module can be used to read temperature and humidity from any bluetooth enabled govee hygrometer

async def decode_govee_data():
    target_mac = "A4:C1:38:0F:9D:63"  # Replace with your Govee H5075 MAC address

    def parse_govee_data(data):
        """
        Parse Govee H5075 manufacturer data.
        Format (per ESPHome example):
        Byte 1-3: Combined integer (basenum) for temperature and humidity.
        Byte 4: Battery level.
        """
        if len(data) < 6:
            return None, None, None

        # Combine bytes 1-3 into a single integer (basenum)
        basenum = (data[1] << 16) | (data[2] << 8) | data[3]

        # Extract temperature (Celsius)
        temperature = basenum / 10000.0

        # Extract humidity
        humidity = (basenum % 1000) / 10.0

        # Extract battery level (Byte 4)
        battery = data[4]
        print(f"Temperature: {temperature:.2f}°C, Humidity: {humidity:.2f}%, Battery: {battery}%")
        return temperature, humidity, battery

    result = {"temperature": None, "humidity": None, "battery": None}

    def detection_callback(device, advertisement_data):
        if device.address == target_mac:
            for key, raw_data in advertisement_data.manufacturer_data.items():
                if key == 60552:  # Manufacturer data key for Govee devices
                    temperature, humidity, battery = parse_govee_data(raw_data)
                    if temperature is not None and humidity is not None and battery is not None:
                        result["temperature"] = temperature
                        result["humidity"] = humidity
                        result["battery"] = battery

                        return  # Stop after retrieving the desired data

    scanner = BleakScanner(detection_callback=detection_callback)
    await scanner.start()
    try:
        await asyncio.sleep(5)  # Scan for 5 seconds
    finally:
        await scanner.stop()
    return result

def read_temperature(speak):
    """Fetch and speak the temperature."""
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(decode_govee_data())
    temperature = result.get("temperature")
    if temperature is not None:
        speak(f"The current temperature is {temperature:.2f}°C.")
    else:
        speak("Unable to fetch the temperature.")

def read_humidity(speak):
    """Fetch and speak the humidity."""
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(decode_govee_data())
    humidity = result.get("humidity")
    if humidity is not None:
        speak(f"The current humidity is {humidity:.2f} percent.")
    else:
        speak("Unable to fetch the humidity.")

def read_battery(speak):
    """Fetch and speak the humidity."""
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(decode_govee_data())
    battery = result.get("battery")
    if battery is not None:
        speak(f"The current battery percentage is {battery} percent.")
    else:
        speak("Unable to fetch the battery percentage.")
