from langgraph.prebuilt import create_react_agent
# from langchain.agents import load_tools, create_react_agent

from app.tools.transcript import transcribe
from app.tools.video_downloader import download_video
from app.tools.book_hotel import book_hotel
from app.tools.start_vote import initiate_vote, count_vote_result
from app.tools.image_generator import generate_image

from app.config import config
from app.utils import send_user_message
from google import genai
from google.genai import types
import json

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



client = genai.Client()

# Receives a user prompt and forwards it to the AI agent for processing.
# Handles collecting tool call arguments and constructing responses based on tool usage.
def invoke(prompt, from_uid):
    print(f"Received prompt: {prompt} from {from_uid}")

    response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction=system_instruction), contents={prompt})

    print(response.text)
    parsed_output = decrypt_response(response.text)
    
    print(parsed_output["function_call_used"])
    
    #Write logic to get the text from user and see if its asking for one of three questions if not use llm and give normal answerr
    #Question 1 Give details about specific transaction, Account or anything on Endless chain make a function to get that 
    #Question 2 Make a transaction on behalf of the user if yes then the user would need to make a function or a tool to do that

    # Format the user message and append it to the interaction history
    # message = {
    #     "role": "user",
    #     "content": f"{prompt}",
    # }
    # history.append(message)

    # query = {
    #     "messages": history
    # }

    # # Invoke the AI agent with the accumulated history
    # result = agent.invoke(query)
    # # result = ""

    # # Initialize variables for tracking tool usage and arguments
    # tool_name = None
    # collected_args = {}
    # required_params = []

    # # Inspect agent's returned steps for tool calls and extract arguments
    # for step in result.get("messages", []):
    #     if hasattr(step, "tool_calls"):
    #         for call in step.tool_calls:
    #             tool_name = call.get("name")
    #             collected_args.update(call.get("args", {}))
    #             # You can define required_params based on the tool manually if needed
    #             if tool_name == "book_hotel":
    #                 required_params = ["location", "check_in", "check_out", "guests", "room_type"]
    #             if tool_name == "initiate_vote":
    #                 required_params = ["group_id", "title", "options"]

    #     elif hasattr(step, "name") and step.name == "book_hotel":
    #         try:
    #             parsed = eval(step.content)
    #             if isinstance(parsed, dict):
    #                 collected_args.update(parsed)
    #         except Exception:
    #             pass

    # # Construct structured response
    # # Skip structured response if tool is in excluded list (e.g., image generation, counting)
    # excluded_tools = {"count_vote_result", "generate_image"}
    # if tool_name and tool_name not in excluded_tools:
    #     missing_params = [p for p in required_params if
    #                       p not in collected_args or not collected_args[p] or collected_args[p] == "undefined"]
    #     if missing_params:
    #         result["response"] = f"Got partial info for `{tool_name}`. Please provide: {', '.join(missing_params)}"
    #     else:
    #         result["response"] = f"All parameters collected for `{tool_name}`: {collected_args}"
    # else:
    #     result["response"] = result.get("messages", [])[-1].content if result.get("messages") else ""

    # history.append({"role": "assistant", "content": result["response"]})

    # Send the final response back to the user via bot message
    send_user_message(from_uid,parsed_output["message"] )

    return "asdf";



def decrypt_response(response_text):
    try:
        
        lines = response_text.strip().splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]

        cleaned_text = "\n".join(lines)
        
        response_data = json.loads(cleaned_text)

        print(response_data)

        message = response_data.get("message", "")
        function_call_used = response_data.get("function_call_used", False)
        function_call = response_data.get("function_call", None)

        # Basic validation
        if not isinstance(message, str) or not isinstance(function_call_used, bool):
            raise ValueError("Invalid format in response.")
        print(message)
        
        return {
            "message": message,
            "function_call_used": function_call_used,
            "function_call": function_call if function_call_used else None
        }

    except Exception as e:
        print(f"Failed to parse response: {e}")
        return {
            "message": response_text,
            "function_call_used": False,
            "function_call": None
        }