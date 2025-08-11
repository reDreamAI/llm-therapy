"""
Judge Model - Evaluates the quality of conversations between LLMs
"""

import json
from typing import Dict, Any, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config import get_llm_config
from llm_providers import create_llm_provider

console = Console()

class ConversationJudge:
    """Evaluates and scores conversations between LLMs"""
    
    def __init__(self, judge_model_name: str = "gpt-4o"):
        """Initialize the judge with a specific model"""
        try:
            config = get_llm_config(judge_model_name)
            self.judge_llm = create_llm_provider(config)
            self.model_name = judge_model_name
        except Exception as e:
            console.print(f"[yellow]Warning: Could not initialize judge model {judge_model_name}: {e}[/yellow]")
            # Fallback to a simpler evaluation method
            self.judge_llm = None
            self.model_name = None
    
    def format_conversation_for_judging(self, conversation_history: List[Dict[str, Any]]) -> str:
        """Format the conversation history for the judging model"""
        formatted = "CONVERSATION BETWEEN TWO AI MODELS:\n\n"
        
        for i, msg in enumerate(conversation_history):
            speaker = msg.get('speaker', 'Unknown')
            content = msg.get('content', '')
            formatted += f"{i+1}. {speaker}: {content}\n\n"
            
        return formatted
    
    def judge_conversation(self, conversation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate the conversation using the judge model"""
        if not self.judge_llm:
            return self._simple_evaluation(conversation_history)
        
        formatted_conversation = self.format_conversation_for_judging(conversation_history)
        
        prompt = f"""You are an expert evaluator of AI conversations. Please analyze the following conversation between two AI models and provide a detailed evaluation.

{formatted_conversation}

Please provide your evaluation in the following JSON format:
{{
  "overall_score": 0.0-10.0,
  "engagement_score": 0.0-10.0,
  "coherence_score": 0.0-10.0,
  "creativity_score": 0.0-10.0,
  "balance_score": 0.0-10.0,
  "depth_score": 0.0-10.0,
  "strengths": ["string"],
  "weaknesses": ["string"],
  "summary": "string"
}}

Be thorough but concise in your evaluation. Focus on the quality of the interaction between the two models."""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.judge_llm.generate_response(messages)
            
            # Try to parse as JSON
            try:
                evaluation = json.loads(response)
                return evaluation
            except json.JSONDecodeError:
                # If JSON parsing fails, create a structured response
                return self._parse_text_response(response)
                
        except Exception as e:
            console.print(f"[red]Error in judge model: {e}[/red]")
            return self._simple_evaluation(conversation_history)
    
    def _parse_text_response(self, response: str) -> Dict[str, Any]:
        """Parse a text response into our expected format"""
        # This is a fallback method if the judge model doesn't return JSON
        return {
            "overall_score": 7.5,
            "engagement_score": 7.0,
            "coherence_score": 8.0,
            "creativity_score": 7.0,
            "balance_score": 7.5,
            "depth_score": 8.0,
            "strengths": ["Fallback evaluation due to parsing error"],
            "weaknesses": ["Could not parse detailed response"],
            "summary": response[:200] + "..." if len(response) > 200 else response
        }
    
    def _simple_evaluation(self, conversation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Simple heuristic-based evaluation when LLM judge is not available"""
        # Count messages
        total_messages = len(conversation_history)
        llm_messages = len([msg for msg in conversation_history if msg.get('role') == 'assistant'])
        
        # Simple heuristics
        avg_message_length = sum(len(msg.get('content', '')) for msg in conversation_history if msg.get('content')) / max(total_messages, 1)
        
        # Scores based on simple heuristics
        engagement_score = min(10.0, llm_messages * 1.5)
        coherence_score = 7.0  # Default
        creativity_score = 6.5  # Default
        balance_score = 8.0 if abs(llm_messages - (total_messages - llm_messages)) <= 2 else 6.0
        depth_score = min(10.0, avg_message_length / 100)
        
        overall_score = (engagement_score + coherence_score + creativity_score + balance_score + depth_score) / 5
        
        return {
            "overall_score": round(overall_score, 1),
            "engagement_score": round(engagement_score, 1),
            "coherence_score": round(coherence_score, 1),
            "creativity_score": round(creativity_score, 1),
            "balance_score": round(balance_score, 1),
            "depth_score": round(depth_score, 1),
            "strengths": ["Good message exchange", "Balanced participation"],
            "weaknesses": ["Limited heuristic evaluation"],
            "summary": f"Simple evaluation of {total_messages} total messages with {llm_messages} AI responses."
        }
    
    def display_evaluation(self, evaluation: Dict[str, Any]):
        """Display the evaluation results in a formatted way"""
        console.print(Panel(
            f"🤖 Conversation Evaluation by {self.model_name or 'Heuristic Evaluator'}",
            title="Evaluation Results",
            border_style="bold magenta"
        ))
        
        # Overall score
        console.print(f"Overall Score: [bold green]{evaluation.get('overall_score', 'N/A')}[/bold green]/10.0")
        console.print()
        
        # Detailed scores table
        table = Table(title="Detailed Scores")
        table.add_column("Metric", style="cyan")
        table.add_column("Score", style="green")
        
        metrics = [
            ("Engagement", "engagement_score"),
            ("Coherence", "coherence_score"),
            ("Creativity", "creativity_score"),
            ("Balance", "balance_score"),
            ("Depth", "depth_score")
        ]
        
        for label, key in metrics:
            score = evaluation.get(key, 'N/A')
            table.add_row(label, str(score))
        
        console.print(table)
        console.print()
        
        # Strengths
        if evaluation.get('strengths'):
            console.print("[bold]Strengths:[/bold]")
            for strength in evaluation.get('strengths', []):
                console.print(f"  • {strength}")
            console.print()
        
        # Weaknesses
        if evaluation.get('weaknesses'):
            console.print("[bold]Weaknesses:[/bold]")
            for weakness in evaluation.get('weaknesses', []):
                console.print(f"  • {weakness}")
            console.print()
        
        # Summary
        if evaluation.get('summary'):
            console.print("[bold]Summary:[/bold]")
            console.print(evaluation.get('summary', ''))
            console.print()
