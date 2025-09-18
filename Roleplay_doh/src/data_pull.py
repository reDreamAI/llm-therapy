"""Pull Roleplay-doh principles dataset either from HF or local export."""
import argparse
from pathlib import Path
from datasets import load_dataset
from src.config import HF_TOKEN, LOCAL_EXPORT_DIR, DATA_RAW

import json

def pull_hf():
    ds = load_dataset("SALT-NLP/roleplay-doh_principles", token=HF_TOKEN)
    # save as arrow cache is fine, but also persist a JSONL snapshot for reproducibility
    out = DATA_RAW / "roleplaydoh_train.jsonl"
    with open(out, "w", encoding="utf-8") as f:
        for ex in ds["train"]:
            # Convert the example to a JSON string and write it to the file
            f.write(json.dumps(ex) + "\n")
    print(f"Saved {len(ds['train'])} examples to {out}")
    print(f"Sample record: {json.dumps(ds['train'][0], indent=2)}")

def pull_local():
    # Nothing to do as long as user places files in LOCAL_EXPORT_DIR
    assert LOCAL_EXPORT_DIR.exists(), f"Place your export files in {LOCAL_EXPORT_DIR}"
    print(f"Using local export at {LOCAL_EXPORT_DIR}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["hf", "local"], default="hf")
    args = ap.parse_args()
    if args.mode == "hf":
        pull_hf()
    else:
        pull_local()
