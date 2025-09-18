.PHONY: all pull extract clean personas prompts eval local

all: pull extract clean personas

pull:
	python -m src.main pull --mode hf

extract:
	python -m src.main extract

clean:
	python -m src.main clean

personas:
	python -m src.main personas

prompts:
	python -m src.main personas --prompts

# Evaluate a sample JSONL of model runs against regex + JSON-parse metrics
# Put your model outputs at outputs/eval/sample_run.jsonl (one JSON per line)
eval:
	python -m src.main eval --runs outputs/eval/sample_run.jsonl

# Offline path using local export in data/raw/roleplay_doh_export
local:
	python -m src.main pull --mode local && \
	python -m src.main extract && \
	python -m src.main clean && \
	python -m src.main personas --prompts
