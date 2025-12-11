"""
Service de construction des commandes.

Ce service centralise la logique de construction de la liste des commandes
à exécuter à partir des widgets de commande.
"""

from typing import Dict, List

from PySide6.QtWidgets import QCheckBox


class CommandBuilderService:
    """
    Service responsable de la construction de la liste des commandes à exécuter.
    
    Extrait de CommandForm pour réduire la complexité cyclomatique
    et améliorer la testabilité.
    """

    @staticmethod
    def build_commands_list(
        command_components: List,
        command_checkboxes: List[QCheckBox],
    ) -> List[Dict[str, str]]:
        """
        Construit la liste des commandes cochées avec leurs noms.

        Args:
            command_components: Liste des widgets de commande
            command_checkboxes: Liste des checkboxes associées

        Returns:
            Liste de dictionnaires {"name": str, "command": str}
        """
        commands_list = []

        for i, command_widget in enumerate(command_components):
            # Vérifier si la commande est cochée
            if command_checkboxes and i < len(command_checkboxes):
                if not command_checkboxes[i].isChecked():
                    continue  # Ignorer les commandes décochées

            command_info = CommandBuilderService._build_single_command(command_widget)
            if command_info:
                commands_list.append(command_info)

        return commands_list

    @staticmethod
    def _build_single_command(command_widget) -> Dict[str, str]:
        """
        Construit les informations d'une seule commande.

        Args:
            command_widget: Le widget de commande

        Returns:
            Dictionnaire {"name": str, "command": str} ou None si invalide
        """
        if not hasattr(command_widget, "_build_full_command"):
            return None

        full_command = command_widget._build_full_command()
        command_name = (
            command_widget.command.name
            if hasattr(command_widget, "command")
            else "Commande"
        )

        return {"name": command_name, "command": full_command}
