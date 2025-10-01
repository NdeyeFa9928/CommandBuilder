"""
Loader YAML avec support de l'inclusion de fichiers (!include)
"""
import os
import yaml
from pathlib import Path
from typing import Any, Dict


class IncludeLoader(yaml.SafeLoader):
    """Loader YAML personnalisé avec support de !include"""
    
    def __init__(self, stream):
        self._root = Path(stream.name).parent if hasattr(stream, 'name') else Path.cwd()
        super().__init__(stream)


def include_constructor(loader: IncludeLoader, node: yaml.ScalarNode) -> Any:
    """Constructeur pour la directive !include"""
    # Récupère le chemin du fichier à inclure
    include_path = loader.construct_scalar(node)
    
    # Résout le chemin relatif par rapport au fichier courant
    file_path = loader._root / include_path
    
    if not file_path.exists():
        raise FileNotFoundError(f"Fichier à inclure non trouvé: {file_path}")
    
    # Charge et parse le fichier inclus
    with open(file_path, 'r', encoding='utf-8') as include_file:
        return yaml.load(include_file, IncludeLoader)


# Enregistre le constructeur pour !include
IncludeLoader.add_constructor('!include', include_constructor)


def load_yaml_with_includes(file_path: str) -> Dict[str, Any]:
    """
    Charge un fichier YAML avec support des inclusions
    
    Args:
        file_path: Chemin vers le fichier YAML
        
    Returns:
        Dict contenant les données parsées
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.load(file, IncludeLoader)


def load_pipeline(pipeline_name: str, data_root: str = None) -> Dict[str, Any]:
    """
    Charge une pipeline par son nom
    
    Args:
        pipeline_name: Nom de la pipeline (sans extension)
        data_root: Racine du dossier data (optionnel)
        
    Returns:
        Dict contenant la pipeline complète avec inclusions résolues
    """
    if data_root is None:
        current_dir = Path(__file__).parent
        data_root = current_dir
    
    pipeline_path = Path(data_root) / "pipelines" / f"{pipeline_name}.yaml"
    
    if not pipeline_path.exists():
        raise FileNotFoundError(f"Pipeline non trouvée: {pipeline_path}")
    
    return load_yaml_with_includes(str(pipeline_path))

