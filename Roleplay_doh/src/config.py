import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the project root (two levels up from this file)
project_root = Path(__file__).resolve().parents[2]
env_path = project_root / '.env'
load_dotenv(env_path)

ROOT = Path(__file__).resolve().parents[1]  # Roleplay_doh directory
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"
OUTPUTS_PERSONAS = OUTPUTS / "personas"
OUTPUTS_PROMPTS = OUTPUTS / "prompts"
OUTPUTS_EVAL = OUTPUTS / "eval"
LOCAL_EXPORT_DIR = DATA_RAW / "roleplay_doh_export"

HF_TOKEN = os.getenv("HF_TOKEN")
LANGUAGE = os.getenv("LANGUAGE", "en")

for d in [DATA_RAW, DATA_PROCESSED, OUTPUTS_PERSONAS, OUTPUTS_PROMPTS, OUTPUTS_EVAL, LOCAL_EXPORT_DIR]:
    d.mkdir(parents=True, exist_ok=True)
