from typing import Tuple, AsyncGenerator
import os
from dotenv import load_dotenv
from prompts import STAGE_PROMPT, SYSTEM_PROMPT_TEMPLATES
from models import Conversation, Stage, ChatInput, ChatResponse
from agent import routing_agent, response_agent
import logging
import json
from langfuse.decorators import observe, langfuse_context

# Load environment variables
load_dotenv()

# Verify API key exists
if not os.getenv("GROQ_API_KEY"):
    raise ValueError("GROQ_API_KEY environment variable is not set")

# Get logger instances
logger = logging.getLogger(__name__)

# Configure Langfuse after load_dotenv()
langfuse_context.configure(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
)


@observe(
    name="process_chat_message",
    as_type="generation",
    capture_input=False,
    capture_output=False,
)
async def process_chat_message(
    chat_input: ChatInput, conversation: Conversation
) -> ChatResponse:
    """Process a chat message and return complete response"""
    try:
        # Update the trace level input/output
        langfuse_context.update_current_trace(
            name=f"Chat Session: {chat_input.session_id[:8]}",
            session_id=chat_input.session_id,
            user_id=chat_input.user_id,
            tags=conversation.stages,
            input=chat_input.message,
            output=None,
        )

        # Update observation level input/output
        langfuse_context.update_current_observation(
            name="Process Message",
            input=chat_input.message,
            output=None,
            metadata={"type": "chat_processing", "is_streaming": False},
        )

        conversation.add_message(chat_input.message, "user")
        stage = await determine_stage_async(chat_input.message, conversation)

        response, usage = await get_response_async(
            stage, chat_input.message, conversation
        )
        conversation.add_message(response, "assistant", stage)

        response_obj = ChatResponse(
            session_id=chat_input.session_id,
            stage=stage,
            response=response,
            stages=conversation.stages,
            usage=usage,
        )

        # Update both trace and observation output
        langfuse_context.update_current_trace(output=response)
        langfuse_context.update_current_observation(output=response, usage=usage)

        return response_obj
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        raise


@observe(
    name="process_chat_message_stream",
    as_type="generation",
    capture_input=False,
    capture_output=False,
)
async def process_chat_message_stream(
    chat_input: ChatInput, conversation: Conversation
) -> AsyncGenerator[str, None]:
    """Process a chat message and yield streaming response"""
    try:
        # Update trace level input
        langfuse_context.update_current_trace(
            name=f"Streaming Chat Session: {chat_input.session_id[:8]}",
            session_id=chat_input.session_id,
            user_id=chat_input.user_id,
            tags=conversation.stages,
            input=chat_input.message,
        )

        langfuse_context.update_current_observation(
            name="Process Stream Message",
            input=chat_input.message,  # Just the message string
            output=None,  # Will be set later
            metadata={"type": "chat_processing", "is_streaming": True},
        )

        conversation.add_message(chat_input.message, "user")
        stage = await determine_stage_async(chat_input.message, conversation)

        history = conversation.get_history_as_string()
        prompt_template = SYSTEM_PROMPT_TEMPLATES[stage]
        response_agent.system_prompt = prompt_template
        full_prompt = f"\n\nConversation history:\n{history}"

        full_response = ""
        final_usage = {}
        async for chunk, chunk_usage in response_agent.generate_stream(full_prompt):
            if chunk:
                full_response += chunk
                yield f"data: {json.dumps({'content': chunk, 'stages': conversation.stages})}\n\n"
            if chunk_usage:
                final_usage = chunk_usage

        conversation.add_message(full_response, "assistant", stage)

        # Update trace output at the end
        langfuse_context.update_current_trace(output=full_response)
        langfuse_context.update_current_observation(
            output=full_response, usage=final_usage
        )

        yield "data: [DONE]\n\n"

    except Exception as e:
        logger.error(f"Streaming error: {str(e)}")
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


@observe(
    name="determine_stage",
    as_type="generation",
    capture_input=False,
    capture_output=False,
)
async def determine_stage_async(user_input: str, conversation: Conversation) -> str:
    """Async version of determine_stage"""
    langfuse_context.update_current_observation(
        name="Stage Determination",
        input=user_input,
        output=None,  # Will be set later
        metadata={"type": "stage_determination"},
    )

    history = conversation.get_history_as_string()
    prompt = (
        f"{STAGE_PROMPT}\n\n<transcript>\n{history}\n</transcript>\n\nClassification:"
    )

    stage_response, usage = await routing_agent.generate(
        prompt
    )  # Unpack both content and usage
    stage_str = stage_response.strip()
    logger.info(f"Stage output: {stage_str}")

    try:
        stage = Stage(stage_str)
    except ValueError:
        print(f"Invalid stage {stage_str}, defaulting to last stage")
        stage = Stage(conversation.stages[-1])

    if stage == Stage.FINAL:
        previous_stages = set(conversation.stages)
        if not previous_stages or Stage.SUMMARY.value not in previous_stages:
            print("Redirecting to summary stage as no summary has been generated yet")
            stage = Stage.SUMMARY

    conversation.stages.append(stage.value)

    langfuse_context.update_current_observation(
        output=stage.value,
        metadata={"stage": stage.value},
        usage=usage,  # Add usage data to the observation
    )

    return stage.value


@observe(
    name="get_response", as_type="generation", capture_input=False, capture_output=False
)
async def get_response_async(
    stage: str, user_input: str, conversation: Conversation
) -> Tuple[str, dict]:
    """Async version of get_response"""
    langfuse_context.update_current_observation(
        name="Response Generation",
        input=user_input,
        output=None,  # Will be set later
        metadata={"type": "response_generation", "stage": stage},
    )

    history = conversation.get_history_as_string()
    prompt_template = SYSTEM_PROMPT_TEMPLATES[stage]
    full_prompt = f"\n\nConversation history:\n{history}"

    response_agent.system_prompt = prompt_template
    response, usage = await response_agent.generate(full_prompt)

    langfuse_context.update_current_observation(output=response, usage=usage)

    return response, usage
