"""Heuristic field extractor for principles, constitutions (system prompts), and vignettes."""
import os
from pathlib import Path
import json
from src.config import DATA_RAW, DATA_PROCESSED, LOCAL_EXPORT_DIR
from src.utils import write_tsv

CAND_KEYS = {
    "principles": ["principles", "principle", "rule", "guideline"],
    # We'll leave these empty since they're not in the data (principles-only pipeline)
    "constitutions": [],
    "vignettes": [],
}

def iter_records():
    print("\n=== Starting iter_records() ===")
    
    # Prefer the HF snapshot
    snap = DATA_RAW / "roleplaydoh_train.jsonl"
    print(f"Checking for HF snapshot at: {snap}")
    
    if snap.exists():
        print(f"Found HF snapshot: {snap}")
        with open(snap, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                if line.strip():
                    try:
                        data = json.loads(line)
                        print(f"  - Record {i}: {type(data)}")
                        yield data
                    except json.JSONDecodeError as e:
                        print(f"  - Error in record {i}: {e}")
        print("Finished processing HF snapshot")
        return
    
    # Else try local export (supports JSON/JSONL/CSV minimal)
    print("No HF snapshot found, checking local exports...")
    print(f"Looking in: {LOCAL_EXPORT_DIR}")
    
    found_files = False
    for p in LOCAL_EXPORT_DIR.glob("**/*"):
        if p.is_file() and p.suffix.lower() in {".jsonl", ".json"}:
            found_files = True
            print(f"\nProcessing file: {p}")
            try:
                with open(p, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if not content:
                        print(f"  - File is empty")
                        continue
                        
                    # Try to parse as JSONL first
                    records = []
                    try:
                        for i, line in enumerate(content.splitlines(), 1):
                            line = line.strip()
                            if line:
                                try:
                                    record = json.loads(line)
                                    print(f"  - Line {i}: JSONL record: {type(record)}")
                                    records.append(record)
                                except json.JSONDecodeError as e:
                                    print(f"  - Line {i}: Invalid JSON: {e}")
                        
                        if records:
                            print(f"  - Successfully parsed {len(records)} records as JSONL")
                            for record in records:
                                yield record
                            continue
                                
                    except Exception as e:
                        print(f"  - Error processing as JSONL: {e}")
                    
                    # If JSONL parsing failed, try as a single JSON object/array
                    try:
                        data = json.loads(content)
                        if isinstance(data, list):
                            print(f"  - Found JSON array with {len(data)} items")
                            for i, item in enumerate(data, 1):
                                print(f"    - Item {i}: {type(item)}")
                                yield item
                        else:
                            print(f"  - Found single JSON object")
                            yield data
                        continue
                            
                    except json.JSONDecodeError as e:
                        print(f"  - Error parsing as JSON: {e}")
                        
            except Exception as e:
                print(f"  - Error reading file {p}: {e}")
    
    if not found_files:
        print("No JSON/JSONL files found in local export directory")


def collect_texts():
    print("\n=== Starting collect_texts() ===")
    principles, constitutions, vignettes = [], [], []
    record_count = 0

    def pick(val, field_name):
        print(f"  - Processing field: {field_name}")
        if not val:
            print(f"    - Value is empty")
            return []
        if isinstance(val, str):
            print(f"    - Found string value: {val[:50]}...")
            return [val]
        if isinstance(val, list):
            print(f"    - Found list with {len(val)} items")
            return [v for v in val if isinstance(v, str)]
        print(f"    - Unhandled type {type(val)} for value: {val}")
        return []

    for i, ex in enumerate(iter_records(), 1):
        record_count += 1
        print(f"\nProcessing record {i}:")
        print(f"Record type: {type(ex)}")
        print(f"Record keys: {list(ex.keys())}")
        
        for key, val in ex.items():
            print(f"\n  Processing key: {key}")
            k = key.lower()
            print(f"  Normalized key: {k}")
            
            # Check if this key matches any of our target categories
            matched = False
            for tgt, needles in CAND_KEYS.items():
                if any(n in k for n in needles):
                    print(f"  Matched category: {tgt}")
                    picked = pick(val, key)
                    if tgt == "principles":
                        principles += picked
                    elif tgt == "constitutions":
                        constitutions += picked
                    elif tgt == "vignettes":
                        vignettes += picked
                    matched = True
                    break
            
            if not matched:
                print(f"  No category match for key: {key}")

    print("\n=== Collection Complete ===")
    print(f"Processed {record_count} records")
    print(f"Collected {len(principles)} principles")
    print(f"Collected {len(constitutions)} constitutions")
    print(f"Collected {len(vignettes)} vignettes")
    
    return principles, constitutions, vignettes

def main():
    print("Starting data extraction...")
    print(f"Working directory: {Path.cwd()}")
    print(f"DATA_RAW: {DATA_RAW}")
    print(f"DATA_PROCESSED: {DATA_PROCESSED}")
    print(f"LOCAL_EXPORT_DIR: {LOCAL_EXPORT_DIR}")
    
    # Check if raw data exists
    print("\n=== Checking for raw data files ===")
    if (DATA_RAW / "roleplaydoh_train.jsonl").exists():
        print(f"Found HF snapshot: {DATA_RAW / 'roleplaydoh_train.jsonl'}")
    else:
        print("No HF snapshot found, checking local exports...")
        local_files = list(LOCAL_EXPORT_DIR.glob("**/*"))
        print(f"Found {len(local_files)} files in local export directory:")
        for f in local_files:
            print(f"- {f}")
    
    # Collect texts
    print("\n=== Collecting texts ===")
    principles, constitutions, vignettes = collect_texts()
    
    # Ensure output directory exists
    print(f"\n=== Preparing output directory ===")
    print(f"Output directory: {DATA_PROCESSED}")
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    print(f"Directory exists: {DATA_PROCESSED.exists()}")
    print(f"Is directory writable: {os.access(DATA_PROCESSED, os.W_OK)}")
    
    # Save the extracted data (principles only)
    print("\n=== Saving extracted data (principles only) ===")
    output_files = [
        ("principles.tsv", principles, "principles"),
    ]
    
    all_success = True
    for filename, data, data_type in output_files:
        output_path = DATA_PROCESSED / filename
        print(f"\nSaving {len(data)} {data_type} to {output_path}")
        
        try:
            # Ensure data is clean and non-empty
            clean_data = []
            for item in data:
                if item and str(item).strip():
                    clean_item = str(item).strip()
                    clean_data.append(clean_item)
            
            print(f"  - After cleaning: {len(clean_data)} items")
            
            if not clean_data:
                print(f"  WARNING: No {data_type} to save! Skipping.")
                continue
            
            # Write the data
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("text\n")
                for item in clean_data:
                    f.write(f"{item}\n")
            
            # Verify the file was written
            if output_path.exists():
                file_size = output_path.stat().st_size
                print(f"  - Successfully wrote {file_size} bytes to {output_path}")
                
                # Verify content
                with open(output_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    print(f"  - File has {len(lines)} lines (including header)")
                    if len(lines) > 1:  # More than just header
                        print(f"  - First data line: {lines[1].strip()}")
                    if len(lines) > 2:  # More than one data line
                        print(f"  - Last data line: {lines[-1].strip()}")
            else:
                print(f"  ERROR: Failed to write {output_path}")
                all_success = False
                
        except Exception as e:
            print(f"  ERROR writing {output_path}: {str(e)}")
            all_success = False
    
    print("\n=== Extraction complete! ===")
    # In principles-only mode, success is defined by writing principles
    if all_success:
        print("✓ Principles saved successfully!")
    
    return all_success

if __name__ == "__main__":
    main()
