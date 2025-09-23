"""
Modèles Pydantic pour les pipelines et tâches.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from .command import Command, CommandInstance


class Task(BaseModel):
    """Définition d'une tâche dans une pipeline."""
    name: str = Field(..., description="Nom de la tâche")
    description: Optional[str] = Field(None, description="Description de la tâche")
    commands: List[str] = Field(..., description="Noms des commandes à exécuter")
    dependencies: List[str] = Field(default_factory=list, description="Tâches prérequises")
    parallel: bool = Field(default=False, description="Exécution parallèle des commandes")


class Pipeline(BaseModel):
    """Définition complète d'une pipeline."""
    name: str = Field(..., description="Nom de la pipeline")
    description: str = Field(..., description="Description de la pipeline")
    icon: Optional[str] = Field(None, description="Icône pour l'interface")
    tasks: List[Task] = Field(..., description="Liste des tâches")

    def get_task_by_name(self, name: str) -> Optional[Task]:
        """Trouve une tâche par son nom."""
        for task in self.tasks:
            if task.name == name:
                return task
        return None

    def get_execution_order(self) -> List[List[str]]:
        """
        Retourne l'ordre d'exécution des tâches en tenant compte des dépendances.
        Retourne une liste de listes, chaque sous-liste contient les tâches
        qui peuvent être exécutées en parallèle.
        """
        executed = set()
        execution_order = []
        
        while len(executed) < len(self.tasks):
            # Trouver les tâches qui peuvent être exécutées maintenant
            ready_tasks = []
            for task in self.tasks:
                if task.name not in executed:
                    # Vérifier si toutes les dépendances sont satisfaites
                    if all(dep in executed for dep in task.dependencies):
                        ready_tasks.append(task.name)
            
            if not ready_tasks:
                # Détection de dépendances circulaires
                remaining = [t.name for t in self.tasks if t.name not in executed]
                raise ValueError(f"Dépendances circulaires détectées dans les tâches: {remaining}")
            
            execution_order.append(ready_tasks)
            executed.update(ready_tasks)
        
        return execution_order

    def validate_dependencies(self) -> List[str]:
        """Valide que toutes les dépendances existent."""
        errors = []
        task_names = {task.name for task in self.tasks}
        
        for task in self.tasks:
            for dep in task.dependencies:
                if dep not in task_names:
                    errors.append(f"Tâche '{task.name}' dépend de '{dep}' qui n'existe pas")
        
        return errors


class PipelineInstance(BaseModel):
    """Instance d'une pipeline avec des commandes configurées."""
    pipeline: Pipeline
    command_instances: Dict[str, CommandInstance] = Field(default_factory=dict)
    
    def add_command_instance(self, command_name: str, instance: CommandInstance):
        """Ajoute une instance de commande configurée."""
        self.command_instances[command_name] = instance
    
    def get_command_instance(self, command_name: str) -> Optional[CommandInstance]:
        """Récupère une instance de commande."""
        return self.command_instances.get(command_name)
    
    def validate_all_commands_configured(self) -> List[str]:
        """Valide que toutes les commandes nécessaires sont configurées."""
        errors = []
        required_commands = set()
        
        # Collecter toutes les commandes requises
        for task in self.pipeline.tasks:
            required_commands.update(task.commands)
        
        # Vérifier que chaque commande est configurée
        for cmd_name in required_commands:
            if cmd_name not in self.command_instances:
                errors.append(f"Commande '{cmd_name}' non configurée")
            else:
                # Valider la configuration de la commande
                instance = self.command_instances[cmd_name]
                cmd_errors = instance.validate_values()
                if cmd_errors:
                    errors.extend([f"Commande '{cmd_name}': {err}" for err in cmd_errors])
        
        return errors
    
    def generate_execution_plan(self) -> List[Dict[str, Any]]:
        """
        Génère un plan d'exécution détaillé avec les lignes de commande.
        """
        execution_plan = []
        execution_order = self.pipeline.get_execution_order()
        
        for step_num, task_names in enumerate(execution_order, 1):
            step = {
                "step": step_num,
                "tasks": []
            }
            
            for task_name in task_names:
                task = self.pipeline.get_task_by_name(task_name)
                task_info = {
                    "name": task_name,
                    "description": task.description,
                    "commands": [],
                    "parallel": task.parallel
                }
                
                for cmd_name in task.commands:
                    if cmd_name in self.command_instances:
                        instance = self.command_instances[cmd_name]
                        cmd_line = instance.to_command_line()
                        task_info["commands"].append({
                            "name": cmd_name,
                            "command_line": cmd_line,
                            "command_string": " ".join(cmd_line)
                        })
                
                step["tasks"].append(task_info)
            
            execution_plan.append(step)
        
        return execution_plan
