from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class Message(BaseModel):
    content: str
    role: str  # 'user' or 'assistant'
    stage: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class Conversation(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    messages: List[Message] = Field(default_factory=list)
    stages: List[str] = Field(default_factory=list)

    def add_message(self, content: str, role: str, stage: Optional[str] = None) -> None:
        message = Message(content=content, role=role, stage=stage)
        self.messages.append(message)

    def get_history_as_string(self, max_messages: int = 100) -> str:
        """Convert recent conversation history to string format for prompt context"""
        recent_messages = self.messages[-max_messages:] if self.messages else []
        history = []
        for msg in recent_messages:
            role = "User" if msg.role == "user" else "Assistant"
            history.append(f"{role}: {msg.content}")
        return "\n".join(history)


# Regular classes for API
class ChatInput(BaseModel):
    session_id: str
    message: str
    user_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict):
        return cls.model_validate(data)


class ChatResponse(BaseModel):
    session_id: str
    stage: str
    response: str
    stages: List[str]
    usage: Optional[Dict] = None

    def to_dict(self):
        return self.model_dump()


class Stage(str, Enum):
    RECORDING = "recording"
    REWRITING = "rewriting"
    SUMMARY = "summary"
    FINAL = "final"


class StageResponse(BaseModel):
    stage: Stage

    def to_dict(self):
        return {"stage": self.stage}
