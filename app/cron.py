import asyncio
import json

from app.agent import invoke
from app.store import message_queue
from app.utils import receive_user_message

 # Background task to continuously poll for user messages.
async def cron_receive_user_message():
    # Continuously polls the Luffa bot for new user messages.
    # Stores messages in the in-memory queue and forwards non-vote messages to the AI agent for processing.
    while True:
        # Call the Luffa bot API to receive a batch of messages
        response = receive_user_message()

        # Iterate over each message group in the response
        for item in response:
            types = item.get("type") # 0: user 1: group
            uid = item.get("uid")
            count = item.get("count")

            # Extract the list of messages from this group
            messages = item.get("message", [])
            for text in messages:
                try:
                    # Parse each individual message as JSON
                    # message body structure
                    # {"uid":"","aiIsHidden":false,"msgId":"","text":"","languageCode":"","isHidden":false}
                    message_body = json.loads(text)

                    from_uid = message_body.get("uid", "")
                    message_text = message_body.get("text", "")
                    if not message_text:
                        continue

                    # Store the parsed message in the in-memory queue
                    message_queue.append({
                        "from_uid": from_uid,
                        "message_text": message_text
                    })

                    # Send non-vote messages to the AI agent for handling
                    if not message_text.startswith("vote:"):
                        invoke(message_text, from_uid)

                except json.JSONDecodeError:
                    print(f"Failed to decode message: {text}")

        # Wait for 1 second before polling for new messages again
        await asyncio.sleep(1)