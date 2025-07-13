import asyncio
import json
import logging
from app.agent import invoke
from app.store import message_queue
from app.utils import receive_user_message

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def cron_receive_user_message():
    logger.info("Starting cron_receive_user_message task")
    while True:
        try:
            # Call the Luffa bot API to receive a batch of messages
            response = receive_user_message()
            logger.info(f"Received response from Luffa API: {response}")

            # Check if the response is an error
            if isinstance(response, dict) and response.get("code") == 500:
                logger.error(f"Luffa API error: {response.get('msg', 'Unknown error')}")
                await asyncio.sleep(1)
                continue

            # Ensure response is a list of message items
            if not isinstance(response, list):
                logger.error(f"Expected list from Luffa API, got: {type(response)}")
                await asyncio.sleep(1)
                continue

            # Iterate over each message group in the response
            for item in response:
                types = item.get("type")  # 0: user, 1: group
                uid = item.get("uid")
                count = item.get("count")
                logger.debug(f"Processing item: type={types}, uid={uid}, count={count}")

                # Extract the list of messages from this group
                messages = item.get("message", [])
                for text in messages:
                    try:
                        # Parse each individual message as JSON
                        message_body = json.loads(text)
                        from_uid = message_body.get("uid", "")
                        message_text = message_body.get("text", "")
                        logger.info(f"Parsed message: from_uid={from_uid}, text={message_text}")

                        if not message_text:
                            logger.warning("Empty message text, skipping")
                            continue

                        # Store the parsed message in the in-memory queue
                        message_queue.append({
                            "from_uid": from_uid,
                            "message_text": message_text
                        })
                        logger.debug(f"Appended to message_queue: {message_queue[-1]}")

                        # Send non-vote messages to the AI agent for handling
                        if not message_text.startswith("vote:"):
                            logger.info(f"Invoking agent for message: {message_text}")
                            invoke(message_text, from_uid)

                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to decode message: {text}, error: {e}")

        except Exception as e:
            logger.error(f"Error in cron_receive_user_message: {e}")

        # Wait for 1 second before polling for new messages
        await asyncio.sleep(1)
