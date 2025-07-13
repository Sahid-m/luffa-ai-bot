from app.config import config
import requests
import json
from langchain.tools import tool

# Tool to generate an image from a given prompt using our custom model.
# You can replace the endpoint with another model if desired (e.g., OpenAI, Stability.ai, etc.)
# NOTE: LuffaBot currently does not support sending image or video files directly.
# You can use `upload_to_tmpfiles` from utils.py to upload the file to tmpfiles.org and share the returned URL.

@tool
def generate_image(prompt):
    """generate an image from a prompt."""
    payload = json.dumps({
        "prompt": prompt
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(config.TEXT_TO_IMAGE_SERVER, headers=headers, data=payload)

    if response.status_code == 200:
        result = response.json()
        url = result.get("url")
        print(f"Image URL: {url}")
        return url
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None