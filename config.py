import os
from typing import Dict, Any
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class LLMConfig(BaseModel):
    """Configuration for an LLM provider"""
    name: str
    model: str
    api_key: str
    temperature: float = 0.7
    max_tokens: int = 1000

class DialogueConfig(BaseModel):
    """Configuration for the dialogue system"""
    rounds: int = 10
    system_prompt: str = "You are engaging in a thoughtful conversation. Respond naturally and thoughtfully to the other person's message."
    conversation_topic: str = ""

# Default LLM configurations
DEFAULT_LLMS = {
    "kimi-k2": LLMConfig(
        name="Kimi K2",
        model="moonshotai/kimi-k2-instruct",
        api_key=os.getenv("GROQ_API_KEY", ""),
        temperature=0.7,
        max_tokens=1000
    ),
        "qwen3-32b": LLMConfig(
        name="Qwen 3 (32B)",
        model="qwen/qwen3-32b",
        api_key=os.getenv("GROQ_API_KEY", ""),
        temperature=0.7,
        max_tokens=1000
    ),
    "llama-3.3-70b": LLMConfig(
        name="Llama 3.3 (70B)",
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY", ""),
        temperature=0.7,
        max_tokens=1000
    ),
    "gpt-4o": LLMConfig(
        name="GPT-4o",
        model="gpt-4o",
        api_key=os.getenv("OPENAI_API_KEY", ""),
        temperature=0.7,
        max_tokens=1000
    ),
    "claude-3.5-sonnet": LLMConfig(
        name="Claude 3.5 Sonnet",
        model="anthropic.claude-3-5-sonnet-20241022-v2",
        api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        temperature=0.7,
        max_tokens=1000
    )
}

def get_llm_config(llm_name: str) -> LLMConfig:
    """Get LLM configuration by name"""
    if llm_name not in DEFAULT_LLMS:
        raise ValueError(f"Unknown LLM: {llm_name}. Available: {list(DEFAULT_LLMS.keys())}")
    return DEFAULT_LLMS[llm_name] 