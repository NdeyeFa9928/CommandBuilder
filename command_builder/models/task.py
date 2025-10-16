from pydantic import BaseModel
from typing import List, Optional, Dict
from command_builder.models.command import Command
from command_builder.models.arguments import TaskArgument
from command_builder.models.with_interface import WithArguments


class Task(BaseModel, WithArguments):
    name: str
    description: str
    arguments: Optional[List[TaskArgument]] = []  # Arguments partagés
    commands: List[Command]

    def apply_shared_arguments(self, shared_values: Dict[str, str]) -> None:
        """
        Applique les valeurs des arguments partagés aux commandes concernées.
        Priorité : valeur de tâche > valeur par défaut de commande.

        Args:
            shared_values: Dictionnaire {code_argument_tache: valeur}
        """
        if not self.arguments:
            return

        # Pour chaque argument de tâche
        for task_arg in self.arguments:
            # Récupère la valeur saisie ou la valeur par défaut de la tâche
            value = shared_values.get(task_arg.code, task_arg.default or "")
            if not value:
                continue

            # Propage la valeur vers les commandes/arguments cibles
            for target in task_arg.values:
                # Trouve la commande concernée
                for command in self.commands:
                    if command.name == target.command:
                        # Utilise la méthode héritée de WithArguments
                        arg = command.get_argument_by_code(target.argument)
                        if arg:
                            # Applique la valeur par défaut (priorité tâche > commande)
                            arg.default = value
