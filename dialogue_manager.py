from typing import List, Dict, Any, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
import time
import os

from config import DialogueConfig, get_llm_config
from llm_providers import create_llm_provider

console = Console()

class DialogueManager:
    """Manages the dialogue between two LLMs"""
    
    def __init__(self, llm1_name: str, llm2_name: str, config: DialogueConfig = None):
        self.config = config or DialogueConfig()
        self.llm1 = create_llm_provider(get_llm_config(llm1_name))
        self.llm2 = create_llm_provider(get_llm_config(llm2_name))
        self.conversation_history: List[Dict[str, Any]] = []
        
    def add_system_message(self, message: str):
        """Add a system message to the conversation"""
        self.conversation_history.append({
            "role": "system",
            "content": message,
            "speaker": "System"
        })
        
    def add_user_message(self, message: str):
        """Add the initial user message"""
        self.conversation_history.append({
            "role": "user",
            "content": message,
            "speaker": "User"
        })
        
    def add_llm_response(self, message: str, speaker: str):
        """Add an LLM response to the conversation"""
        self.conversation_history.append({
            "role": "assistant",
            "content": message,
            "speaker": speaker
        })
        
    def get_messages_for_llm(self) -> List[Dict[str, str]]:
        """Get messages in the format expected by LLM APIs"""
        messages = []
        for msg in self.conversation_history:
            if msg["role"] != "system":  # Skip system messages for now
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        return messages
        
    def display_message(self, message: str, speaker: str, round_num: int = None):
        """Display a message with rich formatting"""
        if round_num:
            title = f"Round {round_num} - {speaker}"
        else:
            title = speaker
            
        # Color coding for different speakers
        if speaker == self.llm1.name:
            color = "blue"
        elif speaker == self.llm2.name:
            color = "green"
        else:
            color = "white"
            
        panel = Panel(
            Text(message, style=color),
            title=title,
            border_style=color,
            padding=(1, 2)
        )
        console.print(panel)
        console.print()  # Add spacing
        
    def run_dialogue(self, initial_message: str, rounds: int = None) -> List[Dict[str, Any]]:
        """Run the dialogue between the two LLMs"""
        rounds = rounds or self.config.rounds
        
        console.print(Panel(
            f"Starting dialogue between [blue]{self.llm1.name}[/blue] and [green]{self.llm2.name}[/green]\n"
            f"Rounds: {rounds}",
            title="🤖 LLM Dialogue",
            border_style="bold blue"
        ))
        console.print()
        
        # Add initial message
        self.add_user_message(initial_message)
        self.display_message(initial_message, "User")
        
        # Run the dialogue
        for round_num in range(1, rounds + 1):
            console.print(f"[bold]🔄 Round {round_num}[/bold]")
            console.print()
            
            # LLM 1 responds
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task(f"🤖 {self.llm1.name} is thinking...", total=None)
                
                messages = self.get_messages_for_llm()
                response1 = self.llm1.generate_response(messages)
                self.add_llm_response(response1, self.llm1.name)
                
            self.display_message(response1, self.llm1.name, round_num)
            
            # LLM 2 responds
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task(f"🤖 {self.llm2.name} is thinking...", total=None)
                
                messages = self.get_messages_for_llm()
                response2 = self.llm2.generate_response(messages)
                self.add_llm_response(response2, self.llm2.name)
                
            self.display_message(response2, self.llm2.name, round_num)
            
            # Add a separator between rounds
            if round_num < rounds:
                console.print("─" * 80)
                console.print()
                
        console.print(Panel(
            "✅ Dialogue completed!",
            title="🎉 Finished",
            border_style="bold green"
        ))
        
        return self.conversation_history
        
    def save_conversation(self, filename: str = None):
        """Save the conversation to a file in the 'dialogues' folder."""

        dialogues_folder = "dialogues"

        if not os.path.exists(dialogues_folder):
            os.makedirs(dialogues_folder)

        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"dialogue_{timestamp}.txt"

        full_path = os.path.join(dialogues_folder, filename)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(f"LLM Dialogue: {self.llm1.name} vs {self.llm2.name}\n")
            f.write("=" * 50 + "\n\n")
            
            for msg in self.conversation_history:
                f.write(f"{msg['speaker']}: {msg['content']}\n\n")
        
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the conversation"""
        return {
            "llm1": self.llm1.name,
            "llm2": self.llm2.name,
            "total_messages": len(self.conversation_history),
            "rounds": len([msg for msg in self.conversation_history if msg["role"] == "assistant"]) // 2
        } 