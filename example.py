#!/usr/bin/env python3
"""
Example script demonstrating LLM Dialogue usage
"""

from dialogue_manager import DialogueManager
from config import DialogueConfig

def main():
    """Run a simple example dialogue"""
    
    # Create a dialogue manager with GPT-4 and Claude-3
    config = DialogueConfig(rounds=5)  # Shorter for demo
    manager = DialogueManager("kimi-k2", "llama-3.3-70b", config)
    
    # Set a custom system prompt
    manager.add_system_message(
        "You are engaging in a friendly debate about the future of technology. "
        "Be thoughtful, respectful, and provide interesting perspectives."
    )
    
    # Start the conversation
    initial_message = "What do you think will be the most transformative technology of the next decade?"
    
    print("🤖 Starting LLM Dialogue Example")
    print("=" * 50)
    
    # Run the dialogue
    conversation = manager.run_dialogue(initial_message, rounds=5)
    
    # Save the conversation
    manager.save_conversation("example_dialogue.txt")
    
    # Show summary
    summary = manager.get_conversation_summary()
    print(f"\n📊 Summary:")
    print(f"   LLM 1: {summary['llm1']}")
    print(f"   LLM 2: {summary['llm2']}")
    print(f"   Total Messages: {summary['total_messages']}")
    print(f"   Rounds: {summary['rounds']}")

if __name__ == "__main__":
    main() 