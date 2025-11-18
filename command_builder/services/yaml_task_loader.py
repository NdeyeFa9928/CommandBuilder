"""Service de chargement des tâches au format YAML avec support d'inclusion."""

import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
from command_builder.models.task import Task
from command_builder.models.yaml_error import YamlError
from command_builder.services.yaml_loader import load_yaml_with_includes
from command_builder.services.yaml_error_handler import YamlErrorHandler


def get_yaml_tasks_directory() -> Path:
    """Retourne le chemin absolu vers le dossier contenant les fichiers YAML de tâches.

    Fonctionne aussi bien en mode développement qu'une fois bundlé par PyInstaller
    (un seul exécutable). Dans ce dernier cas, les fichiers de données sont
    extraits dans le répertoire temporaire `sys._MEIPASS`.
    """

    is_frozen = getattr(sys, "frozen", False)

    if is_frozen:
        # Mode exécutable PyInstaller
        # 1. Vérifier d'abord le dossier externe (one-dir mode)
        exe_dir = Path(sys.executable).parent
        external_tasks_dir = exe_dir / "data" / "tasks"
        if external_tasks_dir.exists():
            return external_tasks_dir.absolute()

        # 2. Sinon, utiliser le dossier interne (_MEIPASS pour one-file mode)
        if hasattr(sys, "_MEIPASS"):
            internal_base = Path(sys._MEIPASS)
            return (internal_base / "command_builder" / "data" / "tasks").absolute()
        else:
            # Fallback si _MEIPASS n'existe pas
            return (exe_dir / "command_builder" / "data" / "tasks").absolute()
    else:
        # Mode développement
        dev_base = Path(__file__).parent.parent
        return (dev_base / "data" / "tasks").absolute()


def list_yaml_task_files() -> List[Path]:
    """Liste tous les fichiers YAML de tâche disponibles."""
    tasks_dir = get_yaml_tasks_directory()
    return list(tasks_dir.glob("*.yaml")) + list(tasks_dir.glob("*.yml"))


def resolve_command_includes(command_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Résout les inclusions de commandes.

    Args:
        command_data: Données de la commande (peut être une inclusion ou une définition complète)

    Returns:
        Liste de commandes complètement résolues
    """
    # Si c'est une commande complètement définie, on la retourne dans une liste
    if isinstance(command_data, dict) and "name" in command_data:
        return [command_data]

    # Si c'est une inclusion qui a été résolue en liste de commandes
    if isinstance(command_data, list):
        # Retourner toutes les commandes de la liste
        return command_data

    # Sinon on retourne telle quelle dans une liste
    return [command_data] if command_data else []


def merge_task_metadata(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fusionne et normalise les métadonnées de la tâche.

    Args:
        task_data: Données brutes de la tâche

    Returns:
        Tâche avec métadonnées fusionnées et normalisées
    """
    # Traite chaque commande pour résoudre les inclusions
    if "commands" in task_data and isinstance(task_data["commands"], list):
        resolved_commands = []
        for cmd in task_data["commands"]:
            # Résoudre chaque commande et aplatir la liste
            cmd_list = resolve_command_includes(cmd)
            resolved_commands.extend(cmd_list)
        task_data["commands"] = resolved_commands

    return task_data


def convert_yaml_to_model(yaml_data: Dict[str, Any]) -> Task:
    """
    Convertit les données YAML en modèle Task.

    Args:
        yaml_data: Données YAML chargées

    Returns:
        Un objet Task
    """
    # Fusionne les métadonnées et résout les inclusions
    processed_data = merge_task_metadata(yaml_data)

    return Task(**processed_data)


def load_yaml_task(file_path: str) -> Task:
    """
    Charge une tâche à partir d'un fichier YAML.

    Args:
        file_path: Chemin vers le fichier YAML de la tâche

    Returns:
        Un objet Task
    """
    try:
        # Charger le YAML avec support des inclusions
        yaml_data = load_yaml_with_includes(file_path)

        # Convertir en modèle Task
        return convert_yaml_to_model(yaml_data)
    except Exception as e:
        print(f"Erreur lors du chargement de la tâche YAML {file_path}: {str(e)}")
        raise


def load_yaml_tasks() -> Tuple[List[Task], List[YamlError]]:
    """
    Charge toutes les tâches YAML disponibles et collecte les erreurs.

    Les tâches avec erreurs ne sont pas chargées, mais les erreurs sont
    collectées et retournées pour affichage à l'utilisateur.

    Returns:
        Tuple (liste des tâches chargées, liste des erreurs)
    """
    task_files = list_yaml_task_files()
    task_files.sort(key=lambda x: x.name)

    if not task_files:
        print("Aucun fichier tâche YAML trouvé")
        return [], []

    # Utiliser le gestionnaire d'erreurs pour charger les tâches
    error_handler = YamlErrorHandler()
    tasks, errors = error_handler.load_all_tasks(task_files)

    # Afficher les résultats
    print(f"Tâches chargées: {len(tasks)}/{len(task_files)}")
    if errors:
        print(f"Erreurs détectées: {len(errors)}")
        for error in errors:
            print(f"  - {error.file_name}: {error.error_type}")

    return tasks, errors
