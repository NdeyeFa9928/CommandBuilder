"""
Loader YAML avec support de l'inclusion de fichiers (!include)
"""

import yaml
from pathlib import Path
from typing import Any, Dict


class IncludeLoader(yaml.SafeLoader):
    """Loader YAML personnalisé avec support de !include"""

    def __init__(self, stream):
        self._root = Path(stream.name).parent if hasattr(stream, "name") else Path.cwd()
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
    with open(file_path, "r", encoding="utf-8") as include_file:
        return yaml.load(include_file, IncludeLoader)


# Enregistre le constructeur pour !include
IncludeLoader.add_constructor("!include", include_constructor)


def load_yaml_with_includes(file_path: str) -> Dict[str, Any]:
    """
    Charge un fichier YAML avec support des inclusions

    Args:
        file_path: Chemin vers le fichier YAML

    Returns:
        Dict contenant les données parsées
    """
    with open(file_path, "r", encoding="utf-8") as file:
        return yaml.load(file, IncludeLoader)


def load_task(task_name: str, data_root: str = None) -> Dict[str, Any]:
    """
    Charge une tâche par son nom

    Args:
        task_name: Nom de la tâche (sans extension)
        data_root: Racine du dossier data (optionnel)

    Returns:
        Dict contenant la tâche complète avec inclusions résolues
    """
    if data_root is None:
        current_dir = Path(__file__).parent
        data_root = current_dir

    task_path = Path(data_root) / "tasks" / f"{task_name}.yaml"

    if not task_path.exists():
        raise FileNotFoundError(f"Tâche non trouvée: {task_path}")

    return load_yaml_with_includes(str(task_path))
