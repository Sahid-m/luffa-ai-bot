import asyncio
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from app.agent import invoke
from app.cron import cron_receive_user_message
from app.store import message_queue, vote_option_map

# load OPENAI_API_KEY from .env
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start background task
    task = asyncio.create_task(cron_receive_user_message())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(lifespan=lifespan)


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    response: Any = None
    session_id: str

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    text = req.message.strip()
    if not text:
        raise HTTPException(400, "Message cannot be empty")

    output = invoke(text, req.session_id)
    return ChatResponse(response=output, session_id=req.session_id)


@app.get("/health")
async def health():
    return {"status": "ok", "message_queue": message_queue, "vote_option_map": vote_option_map}
