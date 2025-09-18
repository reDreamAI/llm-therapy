import json
from pathlib import Path
from typing import Iterable, List
from rapidfuzz import fuzz

def normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())

def unique_by_fuzzy(items: Iterable[str], thresh: int = 92) -> List[str]:
    out = []
    for s in items:
        ns = normalize(s)
        if not ns:
            continue
        is_dup = False
        for t in out:
            if fuzz.ratio(ns, normalize(t)) >= thresh:
                is_dup = True
                break
        if not is_dup:
            out.append(s)
    return out

def write_tsv(path, rows: List[str]):
    # Ensure the directory exists
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, "w", encoding="utf-8") as f:
        f.write("text\n")
        for r in rows:
            if r:  # Only write non-empty rows
                r = str(r).replace("\n", " ").strip()
                if r:  # After cleaning, make sure it's still not empty
                    f.write(r + "\n")

def load_jsonl(path: str) -> List[dict]:
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data.append(json.loads(line))
    return data
