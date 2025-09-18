"""Main entry point for Roleplay-doh data processing pipeline."""
import argparse
import sys
from pathlib import Path
from typing import Optional

from src.config import DATA_RAW, DATA_PROCESSED, OUTPUTS, LOCAL_EXPORT_DIR


def print_header(msg: str):
    print("\n" + "=" * 80)
    print(f"{msg:^80}")
    print("=" * 80 + "\n")


def pull_data(mode: str = "hf"):
    """Pull data from Hugging Face or use local export."""
    print_header("PULLING DATA")
    from src.data_pull import pull_hf, pull_local
    
    if mode == "hf":
        print("Downloading data from Hugging Face...")
        pull_hf()
    else:
        print(f"Using local export from {LOCAL_EXPORT_DIR}...")
        pull_local()


def extract_fields():
    """Extract principles, constitutions, and vignettes from raw data."""
    print_header("EXTRACTING FIELDS")
    from src.extract_fields import collect_texts
    
    principles, constitutions, vignettes = collect_texts()
    # Principles-only pipeline: we only care about principles here.
    print(f"Extracted {len(principles)} principles.")


def clean_transform():
    """Clean and transform the extracted data."""
    print_header("CLEANING AND TRANSFORMING DATA")
    from src.clean_transform import read_tsv
    
    # This will process and save the cleaned data
    import src.clean_transform as ct
    ct.main()


def build_personas(make_prompts: bool = False):
    """Build therapist personas from the processed data."""
    print_header("BUILDING PERSONAS")
    from src.build_personas import main as build_personas_main
    import sys
    
    # Save current args
    original_argv = sys.argv
    
    try:
        # Set up the arguments for the personas script
        if make_prompts:
            sys.argv = [sys.argv[0], "--make-prompts"]
        else:
            sys.argv = [sys.argv[0]]
            
        build_personas_main()
    finally:
        # Restore original args
        sys.argv = original_argv


def evaluate(runs_path: Optional[str] = None):
    """Evaluate model runs."""
    print_header("EVALUATING MODEL RUNS")
    from src.eval_metrics import main as eval_main
    
    if runs_path:
        eval_main(["--runs", runs_path])
    else:
        default_path = OUTPUTS / "eval" / "sample_run.jsonl"
        if default_path.exists():
            eval_main(["--runs", str(default_path)])
        else:
            print(f"No runs file specified and default not found at {default_path}")
            print("Please specify a path to a JSONL file with model runs using --runs")


def main():
    """Main entry point for the Roleplay-doh data processing pipeline."""
    parser = argparse.ArgumentParser(description="Process Roleplay-doh data")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Pull command
    pull_parser = subparsers.add_parser("pull", help="Pull data from source")
    pull_parser.add_argument("--mode", choices=["hf", "local"], default="hf",
                           help="Data source: 'hf' for Hugging Face, 'local' for local export")
    
    # Extract command
    subparsers.add_parser("extract", help="Extract fields from raw data")
    
    # Clean command
    subparsers.add_parser("clean", help="Clean and transform extracted data")
    
    # Personas command
    personas_parser = subparsers.add_parser("personas", help="Build therapist personas")
    personas_parser.add_argument("--prompts", action="store_true", help="Also generate prompt templates")
    
    # Eval command
    eval_parser = subparsers.add_parser("eval", help="Evaluate model runs")
    eval_parser.add_argument("--runs", help="Path to JSONL file with model runs")
    
    # All-in-one command
    all_parser = subparsers.add_parser("all", help="Run full pipeline (pull → extract → clean → personas)")
    all_parser.add_argument("--mode", choices=["hf", "local"], default="hf",
                           help="Data source: 'hf' for Hugging Face, 'local' for local export")
    all_parser.add_argument("--prompts", action="store_true", help="Also generate prompt templates")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "pull":
        pull_data(args.mode)
    elif args.command == "extract":
        extract_fields()
    elif args.command == "clean":
        clean_transform()
    elif args.command == "personas":
        build_personas(args.prompts)
    elif args.command == "eval":
        evaluate(args.runs)
    elif args.command == "all":
        pull_data(args.mode)
        extract_fields()
        clean_transform()
        build_personas(args.prompts)
        print("\n" + "=" * 80)
        print("PIPELINE COMPLETE!")
        print("=" * 80)
        print("\nOutput files:")
        print(f"- Principles: {DATA_PROCESSED}/principles.tsv")
        print(f"- Personas: {OUTPUTS}/personas/")
        if args.prompts:
            print(f"- Prompts: {OUTPUTS}/prompts/")


if __name__ == "__main__":
    main()
