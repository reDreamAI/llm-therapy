import openai
import anthropic
import groq
from typing import List, Dict, Any
from config import LLMConfig

class BaseLLMProvider:
    """Base class for LLM providers"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.name = config.name
        
    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate a response based on conversation history"""
        raise NotImplementedError

class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        openai.api_key = config.api_key
        
    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        try:
            response = openai.ChatCompletion.create(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"

class AnthropicProvider(BaseLLMProvider):
    """Anthropic API provider"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.client = anthropic.Anthropic(api_key=config.api_key)
        
    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        try:
            # Convert OpenAI format to Anthropic format
            prompt = self._convert_messages_to_prompt(messages)
            
            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI message format to Anthropic prompt format"""
        prompt = ""
        for message in messages:
            role = message["role"]
            content = message["content"]
            if role == "system":
                prompt += f"System: {content}\n\n"
            elif role == "user":
                prompt += f"Human: {content}\n\n"
            elif role == "assistant":
                prompt += f"Assistant: {content}\n\n"
        prompt += "Assistant:"
        return prompt

class GroqProvider(BaseLLMProvider):
    """Groq API provider for Kimi K2 and other Groq models"""
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.client = groq.Groq(api_key=config.api_key)
    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"

def create_llm_provider(config: LLMConfig) -> BaseLLMProvider:
    """Factory function to create the appropriate LLM provider"""
    if "kimi" in config.model.lower() or "groq" in config.model.lower():
        return GroqProvider(config)
    if "qwen" in config.model.lower() or "groq" in config.model.lower():
        return GroqProvider(config)
    if "llama" in config.model.lower() or "groq" in config.model.lower():
        return GroqProvider(config)            
    elif "gpt" in config.model.lower():
        return OpenAIProvider(config)
    elif "claude" in config.model.lower():
        return AnthropicProvider(config)
    else:
        raise ValueError(f"Unsupported model: {config.model}") 