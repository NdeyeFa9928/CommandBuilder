"""
Service pour charger les définitions de commandes à partir des fichiers JSON.
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
import logging

from command_builder.models.command import Command


class CommandLoader:
    """
    Service pour charger et gérer les définitions de commandes.
    """
    
    def __init__(self, base_dir: Path):
        """
        Initialise le chargeur de commandes.
        
        Args:
            base_dir: Répertoire de base de l'application
        """
        self.base_dir = base_dir
        self.commands_dir = base_dir / "command_builder" / "data" / "commands"
        self.commands: Dict[str, Command] = {}
        self.logger = logging.getLogger(__name__)
    
    def load_all_commands(self) -> Dict[str, Command]:
        """
        Charge toutes les définitions de commandes depuis le répertoire des commandes.
        
        Returns:
            Dict[str, Command]: Dictionnaire des commandes chargées
        """
        self.commands = {}
        
        if not self.commands_dir.exists():
            self.logger.warning(f"Répertoire de commandes non trouvé: {self.commands_dir}")
            return self.commands
        
        # Parcourir tous les fichiers JSON dans le répertoire des commandes
        for file_path in self.commands_dir.glob("**/*.json"):
            try:
                command = self._load_command_from_file(file_path)
                if command:
                    self.commands[command.name] = command
            except Exception as e:
                self.logger.error(f"Erreur lors du chargement de la commande {file_path}: {str(e)}")
        
        self.logger.info(f"Chargement de {len(self.commands)} définitions de commandes")
        return self.commands
    
    def _load_command_from_file(self, file_path: Path) -> Optional[Command]:
        """
        Charge une définition de commande depuis un fichier JSON.
        
        Args:
            file_path: Chemin vers le fichier JSON
            
        Returns:
            Optional[Command]: La commande chargée ou None en cas d'erreur
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Créer l'objet Command à partir des données JSON
            command = Command.parse_obj(data)
            return command
        
        except json.JSONDecodeError:
            self.logger.error(f"Erreur de décodage JSON dans le fichier {file_path}")
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement de la commande {file_path}: {str(e)}")
        
        return None
    
    def get_command(self, name: str) -> Optional[Command]:
        """
        Récupère une commande par son nom.
        
        Args:
            name: Nom de la commande
            
        Returns:
            Optional[Command]: La commande ou None si elle n'existe pas
        """
        return self.commands.get(name)
    
    def get_all_commands(self) -> List[Command]:
        """
        Récupère toutes les commandes chargées.
        
        Returns:
            List[Command]: Liste de toutes les commandes
        """
        return list(self.commands.values())
