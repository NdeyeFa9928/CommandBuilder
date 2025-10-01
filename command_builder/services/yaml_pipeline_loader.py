"""Service de chargement des pipelines au format YAML avec support d'inclusion."""
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


def resolve_command_includes(command_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Résout les inclusions de commandes.
    
    Args:
        command_data: Données de la commande (peut être une inclusion ou une définition complète)
        
    Returns:
        Liste de commandes complètement résolues
    """
    # Si c'est une commande complètement définie, on la retourne dans une liste
    if isinstance(command_data, dict) and 'name' in command_data:
        return [command_data]
    
    # Si c'est une inclusion qui a été résolue en liste de commandes
    if isinstance(command_data, list):
        # Retourner toutes les commandes de la liste
        return command_data
    
    # Sinon on retourne telle quelle dans une liste
    return [command_data] if command_data else []


def resolve_task_includes(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Résout les inclusions de tâches et fusionne intelligemment les métadonnées.
    
    Args:
        task_data: Données de la tâche (peut être une inclusion ou une définition complète)
        
    Returns:
        Tâche complètement résolue avec toutes les commandes incluses
    """
    # Si c'est une tâche complètement définie avec des commandes
    if isinstance(task_data, dict):
        if 'name' in task_data:
            # Si la tâche contient des commandes qui sont des inclusions
            if 'commands' in task_data and isinstance(task_data['commands'], list):
                resolved_commands = []
                for cmd in task_data['commands']:
                    # Résoudre chaque commande et aplatir la liste
                    cmd_list = resolve_command_includes(cmd)
                    resolved_commands.extend(cmd_list)
                task_data['commands'] = resolved_commands
            return task_data
    
    # Si c'est une inclusion qui a déjà été résolue en une tâche
    if isinstance(task_data, dict) and 'commands' in task_data:
        # Résoudre récursivement les commandes incluses
        resolved_commands = []
        for cmd in task_data['commands']:
            # Résoudre chaque commande et aplatir la liste
            cmd_list = resolve_command_includes(cmd)
            resolved_commands.extend(cmd_list)
        task_data['commands'] = resolved_commands
        return task_data
    
    # Si c'est une autre forme d'inclusion
    return task_data

def add_automatic_dependencies(pipeline_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ajoute automatiquement des dépendances séquentielles entre les tâches si aucune n'est définie.
    
    Args:
        pipeline_data: Données du pipeline
        
    Returns:
        Pipeline avec dépendances automatiques
    """
    if 'tasks' not in pipeline_data or len(pipeline_data['tasks']) <= 1:
        return pipeline_data
    
    tasks = pipeline_data['tasks']
    
    # Ajoute des dépendances séquentielles automatiques
    for i in range(1, len(tasks)):
        current_task = tasks[i]
        previous_task = tasks[i-1]
        
        # Si la tâche courante n'a pas de dépendances définies
        if isinstance(current_task, dict) and 'dependencies' not in current_task:
            # Récupère le nom de la tâche précédente
            if isinstance(previous_task, dict) and 'name' in previous_task:
                previous_task_name = previous_task['name']
            else:
                # Si c'est une inclusion, on utilise un nom par défaut basé sur l'index
                previous_task_name = f"Task_{i-1}"
            
            current_task['dependencies'] = [previous_task_name]
    
    return pipeline_data


def merge_pipeline_metadata(pipeline_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fusionne et normalise les métadonnées du pipeline.
    
    Args:
        pipeline_data: Données brutes du pipeline
        
    Returns:
        Pipeline avec métadonnées fusionnées et normalisées
    """
    # Traite chaque tâche pour résoudre les inclusions
    if 'tasks' in pipeline_data:
        resolved_tasks = []
        for task in pipeline_data['tasks']:
            resolved_task = resolve_task_includes(task)
            resolved_tasks.append(resolved_task)
        pipeline_data['tasks'] = resolved_tasks
    
    # Ajoute des dépendances automatiques si nécessaire
    pipeline_data = add_automatic_dependencies(pipeline_data)
    
    return pipeline_data


def convert_yaml_to_model(yaml_data: Dict[str, Any]) -> Pipeline:
    """
    Convertit les données YAML en modèle Pipeline.
    
    Args:
        yaml_data: Données YAML chargées
        
    Returns:
        Un objet Pipeline
    """
    # Fusionne les métadonnées et résout les inclusions
    processed_data = merge_pipeline_metadata(yaml_data)
    
    return Pipeline(**processed_data)


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
