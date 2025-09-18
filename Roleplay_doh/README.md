# Roleplay-doh Data Processing Pipeline

This module extracts, processes, and organizes therapeutic principles from the Roleplay-doh dataset. The pipeline is now principles-only (no constitutions or vignettes) and is designed to support the development of AI-assisted therapy applications.

## Features

- **Data Extraction**: Pull data from Hugging Face (private dataset supported via token) or use local exports
- **Field Extraction**: Identify and extract principles (principles-only)
- **Data Cleaning**: Deduplicate and tag therapeutic principles
- **Persona Generation**: Create therapist personas for different therapeutic approaches (IRT, CBT, DBT)
- **Prompt Templates**: Generate ready-to-use prompt templates
- **Evaluation**: Assess model responses using therapeutic quality metrics

## Installation

1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables (read from the repository root `.env`):
   ```bash
   # At the repository root (not inside Roleplay_doh/)
   cp .env.example .env
   # Edit .env and add your Hugging Face token if needed
   ```

## Usage

### Full Pipeline

Run the entire data processing pipeline:

```bash
python3 -m src.main all
```

### Individual Commands

1. **Pull data** (from Hugging Face or local):
   ```bash
   python3 -m src.main pull --mode hf  # or --mode local
   ```

2. **Extract fields**:
   ```bash
   python3 -m src.main extract
   ```

3. **Clean and transform data**:
   ```bash
   python3 -m src.main clean
   ```

4. **Build personas** (with optional prompt templates):
   ```bash
   python3 -m src.main personas --prompts
   ```

5. **Evaluate model runs**:
   ```bash
   python3 -m src.main eval --runs path/to/runs.jsonl
   ```

## Project Structure

```
Roleplay_doh/
├── data/
│   ├── raw/                   # Raw data files
│   └── processed/             # Processed data files
├── outputs/
│   ├── personas/              # Generated therapist personas
│   ├── prompts/               # Prompt templates
│   └── eval/                  # Evaluation results
└── src/                       # Source code
    ├── config.py              # Configuration and paths
    ├── data_pull.py           # Data downloading
    ├── extract_fields.py      # Field extraction
    ├── clean_transform.py     # Data cleaning
    ├── build_personas.py      # Persona generation
    ├── eval_metrics.py        # Response evaluation
    └── main.py                # Command-line interface
```

## Output Files (Principles-only)

- **Principles**: `data/processed/principles.tsv`
- **Tagged Principles**: `data/processed/principles_tagged.tsv`
- **Personas**: `outputs/personas/persona_*.txt`
- **Prompts**: `outputs/prompts/` (when `--prompts` is used)
- **Evaluation Results**: `outputs/eval/eval_results.json` (if evaluation is run)

Note: The pipeline intentionally does not produce constitutions or vignettes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
