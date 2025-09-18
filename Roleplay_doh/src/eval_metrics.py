"""Evaluation metrics for therapist responses."""
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import argparse
import pandas as pd
from dataclasses import dataclass
from src.config import OUTPUTS_EVAL

@dataclass
class EvalResult:
    response: str
    metrics: Dict[str, float]
    errors: List[str]

def validate_json_structure(response: str) -> bool:
    """Check if response is valid JSON."""
    try:
        data = json.loads(response)
        return isinstance(data, dict)
    except json.JSONDecodeError:
        return False

def check_empathy(response: str) -> float:
    """Score response for empathy indicators."""
    empathy_phrases = [
        r'i hear', r'i understand', r'that sounds', r'that must be',
        r'it makes sense', r'i can imagine', r'it seems like', r'that sounds',
        r'that sounds difficult', r'i appreciate', r'thank you for sharing'
    ]
    response_lower = response.lower()
    matches = sum(1 for phrase in empathy_phrases if re.search(phrase, response_lower))
    return min(1.0, matches / 3)  # Cap at 1.0

def check_validation(response: str) -> float:
    """Score response for validation indicators."""
    validation_phrases = [
        r'valid', r'normal', r'understandable', r'makes sense',
        r'that\'s okay', r'it\'s okay to', r'that\'s normal',
        r'many people', r'common to', r'natural to'
    ]
    response_lower = response.lower()
    matches = sum(1 for phrase in validation_phrases if re.search(phrase, response_lower))
    return min(1.0, matches / 2)  # Cap at 1.0

def check_question_ratio(response: str) -> float:
    """Check ratio of questions to statements."""
    sentences = re.split(r'[.!?]+', response)
    if len(sentences) < 2:
        return 0.5  # Neutral score for very short responses
    questions = sum(1 for s in sentences if s.strip().endswith('?'))
    ratio = questions / len(sentences)
    # Ideal ratio is around 0.3-0.5 questions per statement
    if 0.2 <= ratio <= 0.6:
        return 1.0
    elif ratio < 0.2 or ratio > 0.8:
        return 0.3
    return 0.7

def check_response_length(response: str) -> float:
    """Check if response length is appropriate."""
    words = response.split()
    if 10 <= len(words) <= 100:  # Ideal length
        return 1.0
    elif 5 <= len(words) < 10 or 100 < len(words) <= 150:
        return 0.7
    return 0.3

def evaluate_response(response: str) -> EvalResult:
    """Evaluate a single therapist response."""
    errors = []
    
    # Basic validation
    if not response or len(response.strip()) < 5:
        return EvalResult(response, {}, ["Empty or too short response"])
    
    # Initialize metrics
    metrics = {
        'empathy': check_empathy(response),
        'validation': check_validation(response),
        'question_ratio': check_question_ratio(response),
        'length': check_response_length(response),
        'is_json': 1.0 if validate_json_structure(response) else 0.0
    }
    
    # Calculate overall score (weighted average)
    weights = {
        'empathy': 0.4,
        'validation': 0.3,
        'question_ratio': 0.15,
        'length': 0.1,
        'is_json': 0.05
    }
    
    metrics['overall'] = sum(metrics[k] * weights[k] for k in weights)
    
    # Generate feedback
    if metrics['empathy'] < 0.3:
        errors.append("Consider showing more empathy and understanding.")
    if metrics['validation'] < 0.3:
        errors.append("Try validating the client's feelings more explicitly.")
    if metrics['question_ratio'] < 0.3:
        errors.append("Consider asking more questions to explore the client's experience.")
    elif metrics['question_ratio'] > 0.7:
        errors.append("The response may contain too many questions.")
    if metrics['length'] < 0.5:
        errors.append("The response may be too brief to be helpful.")
    
    return EvalResult(response, metrics, errors)

def evaluate_runs(runs_path: Path) -> Dict[str, Any]:
    """Evaluate multiple runs from a JSONL file."""
    results = []
    with open(runs_path, 'r') as f:
        for line in f:
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                result = evaluate_response(data.get('response', ''))
                results.append({
                    'input': data.get('input', ''),
                    'response': result.response,
                    'metrics': result.metrics,
                    'errors': result.errors
                })
            except json.JSONDecodeError:
                print(f"Warning: Could not parse line: {line[:100]}...")
    
    if not results:
        return {"error": "No valid responses found in the input file"}
    
    # Calculate aggregate metrics
    metrics = [r['metrics'] for r in results]
    avg_metrics = {k: sum(m.get(k, 0) for m in metrics) / len(metrics) for k in metrics[0]}
    
    return {
        'num_responses': len(results),
        'avg_metrics': avg_metrics,
        'responses': results
    }

def main():
    parser = argparse.ArgumentParser(description='Evaluate therapist responses.')
    parser.add_argument('--runs', type=str, required=True,
                       help='Path to JSONL file containing model runs')
    parser.add_argument('--output', type=str, default=None,
                       help='Output file path (default: eval_results.json in outputs/eval)')
    
    args = parser.parse_args()
    runs_path = Path(args.runs)
    
    if not runs_path.exists():
        print(f"Error: File not found: {runs_path}")
        return
    
    results = evaluate_runs(runs_path)
    
    # Save results
    output_path = Path(args.output) if args.output else OUTPUTS_EVAL / 'eval_results.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    if 'error' in results:
        print(f"Error: {results['error']}")
    else:
        print(f"Evaluated {results['num_responses']} responses")
        print("Average metrics:")
        for k, v in results['avg_metrics'].items():
            print(f"  {k}: {v:.2f}")
        print(f"\nFull results saved to: {output_path}")

if __name__ == "__main__":
    main()
