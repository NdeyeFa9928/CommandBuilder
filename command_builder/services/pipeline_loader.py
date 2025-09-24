"""
Service pour charger les définitions de pipelines à partir des fichiers JSON.
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
import logging

from command_builder.models.pipeline import Pipeline


class PipelineLoader:
    """
    Service pour charger et gérer les définitions de pipelines.
    """
    
    def __init__(self, base_dir: Path):
        """
        Initialise le chargeur de pipelines.
        
        Args:
            base_dir: Répertoire de base de l'application
        """
        self.base_dir = base_dir
        self.pipelines_dir = base_dir / "command_builder" / "data" / "pipelines"
        self.pipelines: Dict[str, Pipeline] = {}
        self.logger = logging.getLogger(__name__)
    
    def load_all_pipelines(self) -> Dict[str, Pipeline]:
        """
        Charge toutes les définitions de pipelines depuis le répertoire des pipelines.
        
        Returns:
            Dict[str, Pipeline]: Dictionnaire des pipelines chargés
        """
        self.pipelines = {}
        
        if not self.pipelines_dir.exists():
            self.logger.warning(f"Répertoire de pipelines non trouvé: {self.pipelines_dir}")
            return self.pipelines
        
        # Parcourir tous les fichiers JSON dans le répertoire des pipelines
        for file_path in self.pipelines_dir.glob("**/*.json"):
            try:
                pipeline = self._load_pipeline_from_file(file_path)
                if pipeline:
                    self.pipelines[pipeline.name] = pipeline
            except Exception as e:
                self.logger.error(f"Erreur lors du chargement du pipeline {file_path}: {str(e)}")
        
        self.logger.info(f"Chargement de {len(self.pipelines)} définitions de pipelines")
        return self.pipelines
    
    def _load_pipeline_from_file(self, file_path: Path) -> Optional[Pipeline]:
        """
        Charge une définition de pipeline depuis un fichier JSON.
        
        Args:
            file_path: Chemin vers le fichier JSON
            
        Returns:
            Optional[Pipeline]: Le pipeline chargé ou None en cas d'erreur
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Adapter le format du fichier JSON au modèle Pipeline
            if "tasks" in data:
                # Convertir les tâches au format attendu par le modèle Pipeline
                tasks = []
                for task_data in data["tasks"]:
                    # Si les commandes sont des objets détaillés, extraire juste les noms
                    if "commands" in task_data and isinstance(task_data["commands"], list):
                        if task_data["commands"] and isinstance(task_data["commands"][0], dict):
                            command_names = [cmd["name"] for cmd in task_data["commands"] if "name" in cmd]
                            task_data["commands"] = command_names
                    
                    tasks.append(task_data)
                
                data["tasks"] = tasks
            
            # Créer l'objet Pipeline à partir des données JSON
            pipeline = Pipeline.parse_obj(data)
            
            # Valider les dépendances
            errors = pipeline.validate_dependencies()
            if errors:
                for error in errors:
                    self.logger.warning(f"Problème dans le pipeline {file_path}: {error}")
            
            return pipeline
        
        except json.JSONDecodeError:
            self.logger.error(f"Erreur de décodage JSON dans le fichier {file_path}")
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement du pipeline {file_path}: {str(e)}")
        
        return None
    
    def get_pipeline(self, name: str) -> Optional[Pipeline]:
        """
        Récupère un pipeline par son nom.
        
        Args:
            name: Nom du pipeline
            
        Returns:
            Optional[Pipeline]: Le pipeline ou None s'il n'existe pas
        """
        return self.pipelines.get(name)
    
    def get_all_pipelines(self) -> List[Pipeline]:
        """
        Récupère tous les pipelines chargés.
        
        Returns:
            List[Pipeline]: Liste de tous les pipelines
        """
        return list(self.pipelines.values())
