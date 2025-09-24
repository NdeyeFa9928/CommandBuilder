import json
from pathlib import Path
from command_builder.models.pipeline import Pipeline

def load_pipeline(file_path: str) -> Pipeline:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return Pipeline(**data)
