import pytest
from datetime import datetime
from models import Message, Conversation, ChatInput, ChatResponse, Stage, StageResponse


def test_message_creation():
    # Test basic message creation
    message = Message(content="Hello", role="user")
    assert message.content == "Hello"
    assert message.role == "user"
    assert message.stage is None
    assert isinstance(message.timestamp, datetime)


def test_conversation():
    # Test conversation creation and methods
    conv = Conversation(session_id="test123")
    assert conv.session_id == "test123"
    assert conv.messages == []
    assert conv.stages == []

    # Test adding messages
    conv.add_message("Hello", "user", "recording")
    assert len(conv.messages) == 1
    assert conv.messages[0].content == "Hello"
    assert conv.messages[0].role == "user"
    assert conv.messages[0].stage == "recording"

    # Test get_history_as_string
    conv.add_message("Hi there!", "assistant", "recording")
    history = conv.get_history_as_string()
    assert "User: Hello" in history
    assert "Assistant: Hi there!" in history


def test_chat_input():
    # Test ChatInput creation and validation
    data = {"session_id": "abc123", "message": "Hello", "user_id": "user123"}
    chat_input = ChatInput.from_dict(data)
    assert chat_input.session_id == "abc123"
    assert chat_input.message == "Hello"
    assert chat_input.user_id == "user123"


def test_chat_response():
    # Test ChatResponse creation and to_dict
    response = ChatResponse(
        session_id="abc123",
        stage="recording",
        response="Hello there",
        stages=["recording"],
        usage={"tokens": 10},
    )

    response_dict = response.to_dict()
    assert response_dict["session_id"] == "abc123"
    assert response_dict["stage"] == "recording"
    assert response_dict["response"] == "Hello there"
    assert response_dict["stages"] == ["recording"]
    assert response_dict["usage"] == {"tokens": 10}


def test_invalid_data():
    # Test validation errors
    with pytest.raises(ValueError):
        Message(content=123, role="user")  # content should be str

    with pytest.raises(ValueError):
        ChatInput(session_id="123")  # missing required field 'message'


def test_stage_enum():
    # Test Stage enum
    assert Stage.RECORDING == "recording"
    assert Stage.REWRITING == "rewriting"
    assert Stage.SUMMARY == "summary"
    assert Stage.FINAL == "final"

    stage_response = StageResponse(stage=Stage.RECORDING)
    assert stage_response.to_dict() == {"stage": "recording"}
