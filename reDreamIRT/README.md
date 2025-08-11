# DreamMend IRT Therapy Chatbot

An Imagery Rescripting Therapy (IRT) chatbot implemented in Python, featuring both streaming and non-streaming response capabilities. This therapeutic chatbot helps users work through their experiences using IRT techniques.

## Setup

1. Install requirements:
pip install -r requirements.txt

2. Set up environment variables:
   - Create a `.env` file
   - Add your API key: `GROQ_API_KEY=your_key_here`

## Starting the API Server

Start the FastAPI server:
uvicorn api:app --reload

The API will run on http://localhost:8000

## Running the Client

### Non-Streaming Version
python chat_client.py

### Streaming Version
python chat_client.py --stream

## Usage
- Type your messages and press Enter
- Type 'quit' to exit the chat
- The bot will guide you through IRT therapy stages
- Responses include conversation stage tracking