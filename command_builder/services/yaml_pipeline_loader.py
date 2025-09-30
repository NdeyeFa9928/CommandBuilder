"""
Service de chargement des pipelines au format YAML avec support d'inclusion.
"""
from pathlib import Path
from typing import List, Dict, Any
from command_builder.models.pipeline import Pipeline
from command_builder.models.task import Task
from command_builder.models.command import Command
from command_builder.services.yaml_loader import load_yaml_with_includes


def get_yaml_pipelines_directory() -> Path:
    """Retourne le chemin vers le répertoire des pipelines YAML."""
    pipelines_dir = Path("command_builder/datas/pipelines").absolute()
    return pipelines_dir


def list_yaml_pipeline_files() -> List[Path]:
    """Liste tous les fichiers YAML de pipeline disponibles."""
    pipelines_dir = get_yaml_pipelines_directory()
    return list(pipelines_dir.glob("*.yaml")) + list(pipelines_dir.glob("*.yml"))


def convert_yaml_to_model(yaml_data: Dict[str, Any]) -> Pipeline:
    """
    Convertit les données YAML en modèle Pipeline.
    
    Args:
        yaml_data: Données YAML chargées
        
    Returns:
        Un objet Pipeline
    """
    return Pipeline(**yaml_data)


def load_yaml_pipeline(file_path: str) -> Pipeline:
    """
    Charge un pipeline à partir d'un fichier YAML.
    
    Args:
        file_path: Chemin vers le fichier YAML du pipeline
        
    Returns:
        Un objet Pipeline
    """
    try:
        # Charger le YAML avec support des inclusions
        yaml_data = load_yaml_with_includes(file_path)
        
        # Convertir en modèle Pipeline
        return convert_yaml_to_model(yaml_data)
    except Exception as e:
        print(f"Erreur lors du chargement du pipeline YAML {file_path}: {str(e)}")
        raise


def load_yaml_pipelines() -> List[Pipeline]:
    """
    Charge tous les pipelines YAML disponibles.
    
    Returns:
        Liste des objets Pipeline
    """
    pipeline_files = list_yaml_pipeline_files()
    pipeline_files.sort(key=lambda x: x.name)

    if not pipeline_files:
        print("Aucun fichier pipeline YAML trouvé")
        return []

    pipelines = []
    for file in pipeline_files:
        try:
            pipeline = load_yaml_pipeline(str(file))
            pipelines.append(pipeline)
            print(f"Pipeline YAML chargé: {pipeline.name}")
        except Exception as e:
            print(f"Erreur lors du chargement du pipeline YAML {file.name}: {str(e)}")

    return pipelines
