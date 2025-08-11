from typing import Dict
from fastapi import FastAPI, HTTPException, Request
from models import ChatInput, Conversation
from irt_app import process_chat_message_stream, process_chat_message

import logging
from fastapi.responses import StreamingResponse
from logging_config import setup_logging

# Initialize logging
setup_logging()

logger = logging.getLogger(__name__)

app = FastAPI()

# In-memory store for conversations
conversations: Dict[str, Conversation] = {}


@app.post("/chat/stream")
async def stream_chat_endpoint(request: Request):
    try:
        body = await request.json()
        chat_input = ChatInput.from_dict(body)

        logger.info(
            f"Processing streaming chat request for session: {chat_input.session_id[:8]}..."
        )

        # Get or create conversation
        conversation = conversations.get(chat_input.session_id)
        if not conversation:
            conversation = Conversation(
                session_id=chat_input.session_id, user_id=chat_input.user_id
            )
            conversations[chat_input.session_id] = conversation

        return StreamingResponse(
            process_chat_message_stream(chat_input, conversation),
            media_type="text/event-stream",
        )

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
async def chat_endpoint(request: Request):
    try:
        body = await request.json()
        chat_input = ChatInput.from_dict(body)

        # Get or create conversation
        conversation = conversations.get(chat_input.session_id)
        if not conversation:
            conversation = Conversation(
                session_id=chat_input.session_id, user_id=chat_input.user_id
            )
            conversations[chat_input.session_id] = conversation

        response = await process_chat_message(chat_input, conversation)
        return response.to_dict()

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
