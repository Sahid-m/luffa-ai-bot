from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DEBUG = os.getenv("DEBUG", "False") == "True"
    LLM_MODEL = "gpt-3.5-turbo"
    LUFFA_BOT_SECRET = os.getenv("LUFFA_BOT_SECRET")
    TEXT_TO_IMAGE_SERVER = os.getenv("TEXT_TO_IMAGE_SERVER")

config = Config()