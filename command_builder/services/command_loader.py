"""
Service pour charger et gérer les commandes et pipelines depuis les fichiers JSON.
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from ..models.command import Command
from ..models.pipeline import Pipeline


class CommandLoader:
    """Gestionnaire pour charger les commandes et pipelines."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialise le loader avec le répertoire de données.
        
        Args:
            data_dir: Répertoire contenant les fichiers JSON. 
                     Si None, utilise le répertoire par défaut.
        """
        if data_dir is None:
            # Répertoire par défaut relatif à ce fichier
            current_dir = Path(__file__).parent.parent
            data_dir = current_dir / "data"
        
        self.data_dir = Path(data_dir)
        self.commands_dir = self.data_dir / "commands"
        self.pipelines_dir = self.data_dir / "pipelines"
        
        # Cache pour les commandes et pipelines chargées
        self._commands_cache: Dict[str, Command] = {}
        self._pipelines_cache: Dict[str, Pipeline] = {}
    
    def load_command(self, command_name: str) -> Optional[Command]:
        """
        Charge une commande depuis son fichier JSON.
        
        Args:
            command_name: Nom de la commande (sans extension .json)
            
        Returns:
            Instance Command ou None si non trouvée
        """
        # Vérifier le cache d'abord
        if command_name in self._commands_cache:
            return self._commands_cache[command_name]
        
        command_file = self.commands_dir / f"{command_name}.json"
        
        if not command_file.exists():
            return None
        
        try:
            with open(command_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            command = Command(**data)
            self._commands_cache[command_name] = command
            return command
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Erreur lors du chargement de la commande {command_name}: {e}")
            return None
    
    def load_all_commands(self) -> Dict[str, Command]:
        """
        Charge toutes les commandes disponibles.
        
        Returns:
            Dictionnaire {nom_commande: Command}
        """
        commands = {}
        
        if not self.commands_dir.exists():
            return commands
        
        for command_file in self.commands_dir.glob("*.json"):
            command_name = command_file.stem
            command = self.load_command(command_name)
            if command:
                commands[command_name] = command
        
        return commands
    
    def load_pipeline(self, pipeline_name: str) -> Optional[Pipeline]:
        """
        Charge une pipeline depuis son fichier JSON.
        
        Args:
            pipeline_name: Nom de la pipeline (sans extension .json)
            
        Returns:
            Instance Pipeline ou None si non trouvée
        """
        # Vérifier le cache d'abord
        if pipeline_name in self._pipelines_cache:
            return self._pipelines_cache[pipeline_name]
        
        pipeline_file = self.pipelines_dir / f"{pipeline_name}.json"
        
        if not pipeline_file.exists():
            return None
        
        try:
            with open(pipeline_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            pipeline = Pipeline(**data)
            
            # Valider les dépendances
            errors = pipeline.validate_dependencies()
            if errors:
                print(f"Erreurs dans la pipeline {pipeline_name}: {errors}")
                return None
            
            self._pipelines_cache[pipeline_name] = pipeline
            return pipeline
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Erreur lors du chargement de la pipeline {pipeline_name}: {e}")
            return None
    
    def load_all_pipelines(self) -> Dict[str, Pipeline]:
        """
        Charge toutes les pipelines disponibles.
        
        Returns:
            Dictionnaire {nom_pipeline: Pipeline}
        """
        pipelines = {}
        
        if not self.pipelines_dir.exists():
            return pipelines
        
        for pipeline_file in self.pipelines_dir.glob("*.json"):
            pipeline_name = pipeline_file.stem
            pipeline = self.load_pipeline(pipeline_name)
            if pipeline:
                pipelines[pipeline_name] = pipeline
        
        return pipelines
    
    def get_commands_by_category(self, category: str) -> Dict[str, Command]:
        """
        Retourne toutes les commandes d'une catégorie donnée.
        
        Args:
            category: Catégorie à filtrer (import, export, analysis, utility)
            
        Returns:
            Dictionnaire des commandes filtrées
        """
        all_commands = self.load_all_commands()
        return {
            name: cmd for name, cmd in all_commands.items() 
            if cmd.category == category
        }
    
    def search_commands(self, query: str) -> Dict[str, Command]:
        """
        Recherche des commandes par nom ou description.
        
        Args:
            query: Terme de recherche
            
        Returns:
            Dictionnaire des commandes correspondantes
        """
        all_commands = self.load_all_commands()
        query_lower = query.lower()
        
        return {
            name: cmd for name, cmd in all_commands.items()
            if (query_lower in name.lower() or 
                query_lower in cmd.description.lower())
        }
    
    def validate_pipeline_commands(self, pipeline: Pipeline) -> List[str]:
        """
        Valide qu'une pipeline référence des commandes existantes.
        
        Args:
            pipeline: Pipeline à valider
            
        Returns:
            Liste des erreurs trouvées
        """
        errors = []
        available_commands = set(self.load_all_commands().keys())
        
        for task in pipeline.tasks:
            for command_name in task.commands:
                if command_name not in available_commands:
                    errors.append(
                        f"Tâche '{task.name}': commande '{command_name}' introuvable"
                    )
        
        return errors
    
    def clear_cache(self):
        """Vide le cache des commandes et pipelines."""
        self._commands_cache.clear()
        self._pipelines_cache.clear()
    
    def reload_command(self, command_name: str) -> Optional[Command]:
        """
        Recharge une commande en ignorant le cache.
        
        Args:
            command_name: Nom de la commande à recharger
            
        Returns:
            Instance Command rechargée ou None
        """
        if command_name in self._commands_cache:
            del self._commands_cache[command_name]
        return self.load_command(command_name)
    
    def reload_pipeline(self, pipeline_name: str) -> Optional[Pipeline]:
        """
        Recharge une pipeline en ignorant le cache.
        
        Args:
            pipeline_name: Nom de la pipeline à recharger
            
        Returns:
            Instance Pipeline rechargée ou None
        """
        if pipeline_name in self._pipelines_cache:
            del self._pipelines_cache[pipeline_name]
        return self.load_pipeline(pipeline_name)
