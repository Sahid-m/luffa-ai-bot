from langgraph.prebuilt import create_react_agent
from app.tools.transcript import transcribe
from app.tools.video_downloader import download_video
from app.tools.book_hotel import book_hotel
from app.tools.start_vote import initiate_vote, count_vote_result
from app.tools.image_generator import generate_image
from app.config import config
from app.utils import send_user_message
import google.generativeai as genai
import json
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

openai_api_key = config.OPENAI_API_KEY

tools = [download_video, transcribe, book_hotel, initiate_vote, count_vote_result, generate_image]

system_instruction="""
You are an AI Agent. YOU HAVE TO GIVE REPLY IN A SPECIFIC FORMAT and the format is:

{
  "message": "<your direct answer to the user prompt>",
  "function_call_used": <true | false>,
  "function_call": <function_name | null>
}

- Use function_call only if it's one of the following:
  - summarizeEndlessTransaction
  - summarizeSpecificAccountTransactions
  - [add more here as needed]

- If none of the allowed function names apply, set:
  - "function_call_used": false
  - "function_call": null

- Always provide a relevant "message" for the user, even when a function_call is made.

- Also SEND ONLY JSON RESPONSE NOTHING ELSE
"""

# Configure Google Generative AI
genai.configure(api_key=config.OPENAI_API_KEY)
client = genai.GenerativeModel(model_name="gemini-1.5-flash")

# In-memory game state storage for each session
game_state = {}

def initialize_game_state(session_id):
    """Initialize game state for a session if it doesn't exist."""
    if session_id not in game_state:
        game_state[session_id] = {
            "in_game": False,
            "user_score": 0,
            "ai_score": 0,
            "last_message": "Do you want to play Rock, Paper, Scissors?"
        }
    return game_state[session_id]

def play_round(user_choice, session_id):
    """Play a single round of Rock, Paper, Scissors."""
    valid_choices = ["rock", "paper", "scissors"]
    user_choice = user_choice.lower().strip()

    # Validate user input
    if user_choice not in valid_choices:
        return {
            "message": "Invalid input. Please type rock, paper, or scissors.",
            "function_call_used": False,
            "function_call": None
        }

    # AI makes a random choice
    ai_choice = random.choice(valid_choices)

    # Determine the winner
    if user_choice == ai_choice:
        result = f"It's a tie! Both chose {user_choice}."
    elif (user_choice == "rock" and ai_choice == "scissors") or \
         (user_choice == "paper" and ai_choice == "rock") or \
         (user_choice == "scissors" and ai_choice == "paper"):
        game_state[session_id]["user_score"] += 1
        result = f"You win this round! {user_choice} beats {ai_choice}."
    else:
        game_state[session_id]["ai_score"] += 1
        result = f"I win this round! {ai_choice} beats {user_choice}."

    # Update score message
    score_message = f"Score: You {game_state[session_id]['user_score']} - AI {game_state[session_id]['ai_score']}"

    # Check for game end
    if game_state[session_id]["user_score"] >= 5:
        game_state[session_id]["in_game"] = False
        game_state[session_id]["last_message"] = "Do you want to play Rock, Paper, Scissors?"
        result = f"Congratulations, you won the game! Final score: You {game_state[session_id]['user_score']} - AI {game_state[session_id]['ai_score']}. {game_state[session_id]['last_message']}"
        game_state[session_id]["user_score"] = 0
        game_state[session_id]["ai_score"] = 0
    elif game_state[session_id]["ai_score"] >= 5:
        game_state[session_id]["in_game"] = False
        game_state[session_id]["last_message"] = "Do you want to play Rock, Paper, Scissors?"
        result = f"Haha, I crushed you! Final score: You {game_state[session_id]['user_score']} - AI {game_state[session_id]['ai_score']}. {game_state[session_id]['last_message']}"
        game_state[session_id]["user_score"] = 0
        game_state[session_id]["ai_score"] = 0
    else:
        result = f"{result} {score_message}"

    return {
        "message": result,
        "function_call_used": False,
        "function_call": None
    }

def invoke(prompt, from_uid):
    logger.info(f"Received prompt: {prompt} from {from_uid}")

    # Initialize or retrieve game state
    state = initialize_game_state(from_uid)

    # Handle game logic
    if not state["in_game"]:
        if prompt.lower().strip() == "yes":
            state["in_game"] = True
            state["last_message"] = "Great! Type rock, paper, or scissors to make your move."
            response = {
                "message": state["last_message"],
                "function_call_used": False,
                "function_call": None
            }
        else:
            # Fall back to Google Generative AI for non-game responses
            try:
                logger.info("Calling Google Generative AI")
                response = client.generate_content(
                    contents=[{
                        "role": "user",
                        "parts": [{"text": prompt}]
                    }],
                    generation_config={"system_instruction": system_instruction}
                )
                logger.debug(f"Google API response: {response.text}")
                response = decrypt_response(response.text)
            except Exception as e:
                logger.error(f"Error calling Google Generative AI: {e}")
                response = {
                    "message": "Sorry, something went wrong. Do you want to play Rock, Paper, Scissors?",
                    "function_call_used": False,
                    "function_call": None
                }
    else:
        response = play_round(prompt, from_uid)

    # Update last message in game state
    state["last_message"] = response["message"]
    logger.info(f"Agent response: {response}")

    # Send response to user
    try:
        send_user_message(from_uid, response["message"])
        logger.info(f"Sent response to user {from_uid}: {response['message']}")
    except Exception as e:
        logger.error(f"Failed to send user message: Luffa API error: {e}")

    return response

def decrypt_response(response_text):
    try:
        lines = response_text.strip().splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]

        cleaned_text = "\n".join(lines)
        logger.debug(f"Cleaned response text: {cleaned_text}")

        response_data = json.loads(cleaned_text)
        logger.info(f"Parsed response data: {response_data}")

        message = response_data.get("message", "")
        function_call_used = response_data.get("function_call_used", False)
        function_call = response_data.get("function_call", None)

        # Basic validation
        if not isinstance(message, str) or not isinstance(function_call_used, bool):
            raise ValueError("Invalid format in response.")
        
        return {
            "message": message,
            "function_call_used": function_call_used,
            "function_call": function_call if function_call_used else None
        }

    except Exception as e:
        logger.error(f"Failed to parse response: {e}")
        return {
            "message": response_text,
            "function_call_used": False,
            "function_call": None
        }
