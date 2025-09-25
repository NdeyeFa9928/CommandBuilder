import json
from pathlib import Path
from typing import List
from command_builder.models.pipeline import Pipeline


def load_pipeline(file_path: str) -> Pipeline:
    """Charge un pipeline à partir d'un fichier JSON.

    Args:
        file_path: Chemin vers le fichier JSON du pipeline

    Returns:
        Un objet Pipeline
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return Pipeline(**data)


def get_pipelines_directory() -> Path:
    """Retourne le chemin vers le répertoire des pipelines."""
    pipelines_dir = Path("command_builder/data/pipelines").absolute()
    return pipelines_dir


def list_pipeline_files() -> List[Path]:
    """Liste tous les fichiers JSON de pipeline disponibles."""
    pipelines_dir = get_pipelines_directory()
    return list(pipelines_dir.glob("*.json"))


def load_pipelines() -> List[Pipeline]:
    """Charge tous les pipelines disponibles."""
    pipeline_files = list_pipeline_files()
    pipeline_files.sort(key=lambda x: x.name)

    if not pipeline_files:
        print("Aucun fichier pipeline trouvé")
        return []

    pipelines = []
    for file in pipeline_files :
        try:
            pipeline = load_pipeline(file)
            pipelines.append(pipeline)
            print(pipeline.name)
        except Exception as e:
            print(f"Erreur lors du chargement du pipeline {file.name}: {str(e)}")

    return pipelines
