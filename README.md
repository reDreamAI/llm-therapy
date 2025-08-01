# LLM Dialogue 🤖

A powerful tool for creating conversations between different AI language models. Watch as two LLMs engage in thoughtful dialogue, responding to each other for multiple rounds.

## Features

- **Multi-LLM Support**: Works with Kimi K2 (Groq), Qwen 3 (Groq), GPT-4o, and Claude 3.5 Sonnet
- **Configurable Rounds**: Set the number of dialogue rounds (default: 10)
- **Beautiful UI**: Rich terminal interface with color-coded messages
- **Conversation Saving**: Save dialogues to files for later review
- **Interactive Mode**: Easy setup with guided prompts
- **API Key Management**: Secure handling of API credentials

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd llm-dialogue

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup API Keys

You'll need API keys for the LLM providers you want to use:

- **OpenAI**: Get your key from [OpenAI Platform](https://platform.openai.com/api-keys)
- **Anthropic**: Get your key from [Anthropic Console](https://console.anthropic.com/)
- **Groq**: Get your key from [Groq Console](https://console.groq.com/)

Set them as environment variables:
```bash
export GROQ_API_KEY="your_groq_key_here"
export OPENAI_API_KEY="your_openai_key_here"
export ANTHROPIC_API_KEY="your_anthropic_key_here"
```

Or create a `.env` file (copy from `env.example`):
```bash
cp env.example .env
# Edit .env with your actual API keys
```

### 3. Run a Dialogue

#### Interactive Mode (Recommended)
```bash
python main.py start --interactive
```

#### Direct Mode
```bash
python main.py start --llm1 kimi-k2 --llm2 gpt-4o --rounds 10 --message "Let's discuss the future of AI"
```

#### Save Conversation
```bash
python main.py start --llm1 kimi-k2 --llm2 gpt-4o --save
```

## Usage Examples

### Basic Dialogue
```bash
# Start a 10-round conversation between GPT-4 and Claude-3
python main.py start --llm1 kimi-k2 --llm2 gpt-4o
```

### Custom Topic
```bash
# Discuss a specific topic
python main.py start \
  --llm1 kimi-k2 \
  --llm2 gpt-4o \
  --message "What are the ethical implications of artificial general intelligence?" \
  --rounds 15
```

### Save to File
```bash
# Save the conversation for later review
python main.py start --llm1 kimi-k2 --llm2 gpt-4o --save
```

## Available Commands

```bash
# Start a dialogue
python main.py start [OPTIONS]

# List available LLM models
python main.py list-llms

# Show setup instructions
python main.py setup
```

## Available LLMs

| Name | Model | Provider |
|------|-------|----------|
| kimi-k2 | moonshotai/kimi-k2-instruct | Groq |
| qwen3-32b | Qwen/Qwen3-32B | Groq |
| gpt-4o | gpt-4o | OpenAI |
| claude-3.5-sonnet | anthropic.claude-3-5-sonnet-20241022-v2 | Anthropic |

## Configuration

You can customize the dialogue behavior by modifying `config.py`:

- **Temperature**: Control response creativity (0.0-1.0)
- **Max Tokens**: Limit response length
- **System Prompts**: Set conversation context
- **Default Rounds**: Change default number of rounds

## Project Structure

```
llm-dialogue/
├── main.py              # CLI application
├── dialogue_manager.py  # Core dialogue orchestration
├── llm_providers.py     # LLM API integrations
├── config.py           # Configuration management
├── requirements.txt    # Python dependencies
├── env.example        # API key template
└── README.md          # This file
```

## Example Output

```
🤖 LLM Dialogue
Starting dialogue between GPT-4 and Claude-3
Rounds: 10

User: Hello! Let's have an interesting conversation about artificial intelligence and its future.

🔄 Round 1

┌─ Round 1 - GPT-4 ──────────────────────────────────────────────┐
│ I'd be happy to discuss AI and its future! This is a fascinating│
│ topic that touches on technology, philosophy, economics, and   │
│ society. What specific aspect would you like to explore?       │
└─────────────────────────────────────────────────────────────────┘

┌─ Round 1 - Claude-3 ───────────────────────────────────────────┐
│ That's a great topic! I think the most interesting aspect is   │
│ how AI will transform human work and creativity. What are your │
│ thoughts on AI augmentation vs replacement?                    │
└─────────────────────────────────────────────────────────────────┘
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.
