"""Clean, deduplicate, and tag principles (principles-only pipeline)."""
import json
import pandas as pd
from pathlib import Path
from src.config import DATA_RAW, DATA_PROCESSED
from src.utils import unique_by_fuzzy

def read_tsv(p):
    try:
        return pd.read_csv(p, sep=",", engine="python")  # if someone saved as CSV
    except Exception:
        return pd.read_csv(p, sep="\t")

def tag_principles(principles: list[str]) -> list[tuple[str, list[str]]]:
    tags = []
    for p in principles:
        tl = []
        pl = p.lower()
        if any(w in pl for w in ["empath", "validate", "non-judg", "supportive"]):
            tl.append("empathy")
        if any(w in pl for w in ["boundar", "avoid diagnosis", "no medical", "scope"]):
            tl.append("boundaries")
        if any(w in pl for w in ["step", "phase", "stages", "confirm", "consent"]):
            tl.append("step-control")
        if any(w in pl for w in ["safety", "harm", "crisis", "hotline", "emergency"]):
            tl.append("safety")
        if any(w in pl for w in ["brief", "concise", "short"]):
            tl.append("brevity")
        if any(w in pl for w in ["disclose", "privacy", "confidential"]):
            tl.append("disclosure")
        tags.append((p, tl))
    return tags

# Vignettes and constitutions are intentionally not used in this principles-only setup.

def read_principles_from_jsonl():
    """Read principles directly from the raw JSONL file."""
    principles = []
    jsonl_path = DATA_RAW / "roleplaydoh_train.jsonl"
    if not jsonl_path.exists():
        print(f"Warning: {jsonl_path} not found")
        return []
        
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                if 'Principles' in data and data['Principles'].strip():
                    principles.append(data['Principles'].strip())
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")
    return principles

def main():
    # Read the raw data
    print("Reading principles from JSONL file...")
    pr = read_principles_from_jsonl()
    
    # Fall back to TSV if no principles were found in JSONL
    if not pr:
        print("No principles found in JSONL, falling back to TSV...")
        pr = read_tsv(DATA_PROCESSED / "principles.tsv")["text"].dropna().tolist()
    
    # Principles-only pipeline
    print(f"Found {len(pr)} principles")
    
    # Clean and deduplicate
    print("Cleaning and deduplicating principles...")
    pr_clean = unique_by_fuzzy(pr, 92)

    # Tag principles
    tagged = tag_principles(pr_clean)

    # Ensure output directory exists
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    
    # Save processed data
    pd.DataFrame({"text": pr_clean}).to_csv(DATA_PROCESSED / "principles.tsv", sep="\t", index=False)
    
    # Save tagged principles
    pd.DataFrame({"principle": [p for p, _ in tagged], "tags": [",".join(t) for _, t in tagged]}) \
        .to_csv(DATA_PROCESSED / "principles_tagged.tsv", sep="\t", index=False)
    
    print(f"Processed {len(pr_clean)} principles.")

if __name__ == "__main__":
    main()
