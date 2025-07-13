import json
import requests

from app.config import config

# Sends a direct message to a specific user via the Luffa bot API.
# Parameters:
#   uid (str): The user ID to send the message to.
#   message (str): The message content to send.
def send_user_message(uid, message):
    url = "https://apibot.luffa.im/robot/send"

    # Prepare the payload with secret, user ID, and message content
    payload = json.dumps({
        "secret": config.LUFFA_BOT_SECRET,
        "uid": uid,
        "msg": json.dumps({"text": f"{message}"})
    })
    headers = {
        'Content-Type': 'application/json'
    }

    # Send POST request to the Luffa bot API
    response = requests.request("POST", url, headers=headers, data=payload)

    # Print the response text for debugging purposes
    print(f"Sent: {response.text}")

# Sends a message to a group via the Luffa bot API.
# Parameters:
#   uid (str): The group ID to send the message to.
#   message (dict): The message content (as a dictionary) to send.
def send_group_message(uid, message):
    url = "https://apibot.luffa.im/robot/sendGroup"

    # Prepare the payload with secret, group ID, message type, and message content
    payload = json.dumps({
        "secret": config.LUFFA_BOT_SECRET,
        "uid": uid,
        "type": "2",
        "msg": json.dumps(message)
    })
    headers = {
        'Content-Type': 'application/json'
    }

    # Send POST request to the Luffa bot API for group messaging
    response = requests.request("POST", url, headers=headers, data=payload)

    # Print the response text for debugging purposes
    print(f"Sent: {response.text}")

# Polls the Luffa bot API to receive incoming user messages.
# Returns:
#   dict: The JSON response from the Luffa bot API containing incoming messages.
def receive_user_message():
    url = "https://apibot.luffa.im/robot/receive"

    # Prepare the payload with the secret key
    payload = json.dumps({
        "secret": config.LUFFA_BOT_SECRET,
    })
    headers = {
        'Content-Type': 'application/json'
    }

    # Send POST request to receive messages from the Luffa bot API
    response = requests.request("POST", url, headers=headers, data=payload)

    # Return the JSON response containing incoming messages
    return response.json()

# Uploads a file to tmpfiles.org and returns the URL.
# Parameters:
#   file_path (str): The local path to the file to be uploaded.
# Returns:
#   str: The URL where the uploaded file can be accessed.
def upload_to_tmpfiles(file_path):
    # Open the file in binary mode for uploading
    with open(file_path, 'rb') as f:
        # POST the file to tmpfiles.org API
        r = requests.post('https://tmpfiles.org/api/v1/upload', files={'file': f})
    # Return the URL of the uploaded file from the response JSON
    return r.json()['data']["url"]