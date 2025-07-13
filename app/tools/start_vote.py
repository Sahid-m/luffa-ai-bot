import uuid
from langchain.tools import tool

from app.store import message_queue
from app.store import vote_option_map
from app.utils import send_group_message, send_user_message

@tool
# Tool to initiate a group vote by sending a message with clickable options.
# This function generates unique selectors for each option and tracks them in memory.
# NOTE: This is a temporary implementation; vote_option_map should be persisted in a database for production use.
def initiate_vote(group_id: str, title: str, options: list):
    """
    Initiate a vote in a group.

    CRITICAL RULES:
    1. MUST use the EXACT title provided by the user
    2. MUST use the EXACT options provided by the user
    3. NEVER assume or generate group_id
    4. ALWAYS ask user for group_id if missing
    5. NEVER use default/placeholder values for ANY parameter

    Parameters:
    - group_id: MUST be explicitly provided by user (no default)
    - title: User's exact vote title
    - options: List of vote choices (exact user input)
    """

    if not group_id:
        raise ValueError("Group ID is required")
    if not title:
        raise ValueError("Title is required")
    if not options:
        raise ValueError("Options are required")

    button_options = []
    for option in options:
        selector = f"vote:{uuid.uuid4().hex}"
        button_options.append({
            "name": option,
            "selector": selector,
            "type": "default",
            "isHidden": "1"
        })
        vote_option_map[selector] = option

    payload = {
        "text": title,
        "button": button_options
    }

    send_group_message(group_id, payload)

@tool
# Tool to count the vote results from the in-memory message queue.
# It tallies votes based on message content and the vote_option_map.
# NOTE: In production, both the message queue and vote mapping should be persisted in a database.
def count_vote_result() -> str:
    """count the vote result."""

    # print(message_queue)
    # [
    #     {
    #         "from_uid": "QseG8BQZyHh",
    #         "message_text": "vote:138ee59a7c7f4ce088adf3c7fcb3fa88"
    #     },
    #     {
    #         "from_uid": "TZFAq4w9vC3",
    #         "message_text": "vote:138ee59a7c7f4ce088adf3c7fcb3fa88"
    #     }
    # ]

    # print(vote_option_map)
    # {
    #     "vote:137b2a8fb3cc44da9aecb4d560a78212": "Rock",
    #     "vote:138ee59a7c7f4ce088adf3c7fcb3fa88": "Paper",
    #     "vote:8316c54188b043c78174ceb88a07fd2e": "Scissors"
    # }

    # Initialize the result count dictionary with all vote options set to 0
    result_count = {value: 0 for value in vote_option_map.values()}

    # Iterate through all messages in the queue to count valid votes
    for message in message_queue:
        vote_key = message["message_text"]
        if vote_key in vote_option_map:
            option = vote_option_map[vote_key]
            result_count[option] += 1

    # Format the counted results into a string for display
    result = "\n".join(f"{option}: {count}" for option, count in result_count.items())
    return result
