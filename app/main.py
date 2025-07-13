import asyncio
from contextlib import asynccontextmanager
from typing import Any
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from app.agent import invoke
from app.cron import cron_receive_user_message
from app.store import message_queue, vote_option_map

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load OPENAI_API_KEY from .env
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting background task for cron_receive_user_message")
    task = asyncio.create_task(cron_receive_user_message())
    yield
    logger.info("Cancelling background task")
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        logger.info("Background task cancelled")

app = FastAPI(lifespan=lifespan)

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    response: Any = None
    session_id: str

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    logger.info(f"Received chat request: session_id={req.session_id}, message={req.message}")
    text = req.message.strip()
    if not text:
        logger.warning("Empty message received")
        raise HTTPException(400, "Message cannot be empty")

    output = invoke(text, req.session_id)
    logger.info(f"Chat response: {output}")
    return ChatResponse(response=output["message"], session_id=req.session_id)

@app.get("/health")
async def health():
    logger.info("Health check requested")
    return {"status": "ok", "message_queue": message_queue, "vote_option_map": vote_option_map}
