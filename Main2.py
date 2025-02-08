import time
import hashlib
import hmac
import requests

# Your Tuya IoT credentials
CLIENT_ID = 'rde3nw5sswh9yvgvcqdu'     # Your Access ID
CLIENT_SECRET = '8b30deba0a8d416eb00762060ae70d14'  # Your Access Secret

# Generate a timestamp (in milliseconds)
timestamp = str(int(time.time() * 1000))

# Create the string to sign: CLIENT_ID + timestamp
string_to_sign = CLIENT_ID + timestamp

# Generate HMAC-SHA256 signature and convert to uppercase hexadecimal
signature = hmac.new(
    CLIENT_SECRET.encode('utf-8'),
    string_to_sign.encode('utf-8'),
    hashlib.sha256
).hexdigest().upper()

# Define headers for the request
headers = {
    'client_id': CLIENT_ID,
    'sign': signature,
    't': timestamp,
    'sign_method': 'HMAC-SHA256',
    'Content-Type': 'application/json'
}

# Correct Tuya API token endpoint with query parameter
token_url = 'https://openapi.tuyaeu.com/v1.0/token?grant_type=1'

# Send the GET request (not POST)
response = requests.get(token_url, headers=headers)
token_data = response.json()

# Handle the response
if token_data.get('success'):
    access_token = token_data['result']['access_token']
    print("Access Token:", access_token)
else:
    print("Error obtaining token:", token_data)
