from pydantic import BaseModel
from typing import List, Optional, Dict
from command_builder.models.command import Command
from command_builder.models.arguments import TaskArgument


class Task(BaseModel):
    name: str
    description: str
    arguments: Optional[List[TaskArgument]] = []  # Arguments partagés
    commands: List[Command]

    def apply_shared_arguments(self, shared_values: Dict[str, str]) -> None:
        """
        Applique les valeurs des arguments partagés aux commandes concernées.

        Args:
            shared_values: Dictionnaire {code_argument_tache: valeur}
        """
        if not self.arguments:
            return

        # Pour chaque argument de tâche
        for task_arg in self.arguments:
            # Récupère la valeur saisie
            value = shared_values.get(task_arg.code, "")
            if not value:
                continue

            # Propage la valeur vers les commandes/arguments cibles
            for target in task_arg.values:
                # Trouve la commande concernée
                for command in self.commands:
                    if command.name == target.command:
                        # Trouve l'argument dans la commande
                        for arg in command.arguments:
                            if arg.code == target.argument:
                                # Applique la valeur par défaut
                                arg.default = value
                                break

    def get_shared_argument_by_code(self, code: str) -> Optional[TaskArgument]:
        """Récupère un argument partagé par son code."""
        if not self.arguments:
            return None
        for arg in self.arguments:
            if arg.code == code:
                return arg
        return None
