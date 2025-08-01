#!/usr/bin/env python3
"""
LLM Dialogue - A tool for creating conversations between different AI models
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import print as rprint

from config import DEFAULT_LLMS, DialogueConfig
from dialogue_manager import DialogueManager

app = typer.Typer()
console = Console()

@app.command()
def start(
    llm1: str = typer.Option("kimi-k2", "--llm1", "-1", help="First LLM (kimi-k2, qwen3-32b, llama-3.3-70b, gpt-4o, claude-3.5-sonnet)"),
    llm2: str = typer.Option("qwen3-32b", "--llm2", "-2", help="Second LLM (kimi-k2, qwen3-32b, llama-3.3-70b, gpt-4o, claude-3.5-sonnet)"),
    rounds: int = typer.Option(10, "--rounds", "-r", help="Number of dialogue rounds"),
    message: str = typer.Option(None, "--message", "-m", help="Initial message to start the conversation"),
    save: bool = typer.Option(False, "--save", "-s", help="Save conversation to file"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Interactive mode")
):
    """Start a dialogue between two LLMs"""
    
    if interactive:
        run_interactive_mode()
    else:
        run_direct_mode(llm1, llm2, rounds, message, save)

def run_interactive_mode():
    """Run in interactive mode with prompts"""
    console.print(Panel(
        "🤖 Welcome to LLM Dialogue!\n"
        "Let's set up a conversation between two AI models.",
        title="Interactive Setup",
        border_style="bold blue"
    ))
    
    # Show available LLMs
    show_available_llms()
    
    # Get LLM choices
    llm1 = Prompt.ask(
        "Choose first LLM",
        choices=["kimi-k2", "qwen3-32b", "llama-3.3-70b", "gpt-4o", "claude-3.5-sonnet"],
        default="kimi-k2"
    )
    
    llm2 = Prompt.ask(
        "Choose second LLM",
        choices=["kimi-k2", "qwen3-32b", "llama-3.3-70b", "gpt-4o", "claude-3.5-sonnet"],
        default="qwen3-32b"
    )
    
    # Get number of rounds
    rounds = int(Prompt.ask(
        "Number of dialogue rounds",
        default="10"
    ))
    
    # Get initial message
    message = Prompt.ask(
        "Enter the initial message to start the conversation",
        default="Hello! Let's have an interesting conversation about artificial intelligence and its future."
    )
    
    # Ask about saving
    save = Confirm.ask("Save conversation to file?")
    
    # Run the dialogue
    run_dialogue(llm1, llm2, rounds, message, save)

def run_direct_mode(llm1: str, llm2: str, rounds: int, message: str, save: bool):
    """Run in direct mode with provided parameters"""
    if not llm1 or not llm2:
        console.print("[red]Error: Both --llm1 and --llm2 are required in direct mode[/red]")
        raise typer.Exit(1)
    
    if not message:
        message = "Hello! Let's have an interesting conversation about artificial intelligence and its future."
    
    run_dialogue(llm1, llm2, rounds, message, save)

def run_dialogue(llm1: str, llm2: str, rounds: int, message: str, save: bool):
    """Run the actual dialogue"""
    try:
        # Create dialogue manager
        config = DialogueConfig(rounds=rounds)
        manager = DialogueManager(llm1, llm2, config)
        
        # Run the dialogue
        conversation = manager.run_dialogue(message, rounds)
        
        # Save if requested
        if save:
            manager.save_conversation()
        
        # Show summary
        summary = manager.get_conversation_summary()
        show_summary(summary)
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)

def show_available_llms():
    """Display available LLMs in a table"""
    table = Table(title="Available LLM Models")
    table.add_column("Name", style="cyan")
    table.add_column("Model", style="magenta")
    table.add_column("Provider", style="green")
    
    for key, config in DEFAULT_LLMS.items():
        if key == "kimi-k2":
            provider = "Groq"
        elif key == "llama-3.3-70b":
            provider = "Groq"
        elif key == "qwen3-32b":
            provider = "Groq"
        elif key == "gpt-4o":
            provider = "OpenAI"
        elif key == "claude-3.5-sonnet":
            provider = "Anthropic"
        else:
            provider = "Unknown"
        table.add_row(key, config.model, provider)
    
    console.print(table)
    console.print()

def show_summary(summary: dict):
    """Display conversation summary"""
    table = Table(title="Conversation Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("LLM 1", summary["llm1"])
    table.add_row("LLM 2", summary["llm2"])
    table.add_row("Total Messages", str(summary["total_messages"]))
    table.add_row("Rounds Completed", str(summary["rounds"]))
    
    console.print(table)

@app.command()
def list_llms():
    """List all available LLM models"""
    show_available_llms()

@app.command()
def setup():
    """Interactive setup for API keys"""
    console.print(Panel(
        "🔑 API Key Setup\n\n"
        "You'll need API keys for the LLM providers you want to use:\n"
        "• OpenAI: https://platform.openai.com/api-keys\n"
        "• Anthropic: https://console.anthropic.com/\n\n"
        "Set these as environment variables:\n"
        "• OPENAI_API_KEY\n"
        "• ANTHROPIC_API_KEY\n\n"
        "Or create a .env file in this directory.",
        title="Setup Instructions",
        border_style="bold yellow"
    ))

if __name__ == "__main__":
    app() 