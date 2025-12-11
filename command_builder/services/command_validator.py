"""
Service de validation des arguments de commandes.

Ce service centralise la logique de validation des arguments obligatoires
avant l'exécution des commandes.
"""

from typing import Dict, List, Tuple

from PySide6.QtWidgets import QCheckBox


class CommandValidator:
    """
    Service responsable de la validation des arguments des commandes.
    
    Extrait de CommandForm pour réduire la complexité cyclomatique
    et améliorer la testabilité.
    """

    @staticmethod
    def validate_commands(
        command_components: List,
        command_checkboxes: List[QCheckBox],
    ) -> Tuple[bool, List[str]]:
        """
        Valide tous les arguments obligatoires des commandes cochées.

        Args:
            command_components: Liste des widgets de commande
            command_checkboxes: Liste des checkboxes associées

        Returns:
            Tuple (is_valid, errors) où:
            - is_valid: True si toutes les commandes sont valides
            - errors: Liste des messages d'erreur formatés
        """
        all_errors = []

        for i, command_widget in enumerate(command_components):
            # Vérifier si la commande est cochée
            if command_checkboxes and i < len(command_checkboxes):
                if not command_checkboxes[i].isChecked():
                    continue  # Ignorer les commandes décochées

            errors = CommandValidator._validate_single_command(command_widget)
            all_errors.extend(errors)

        return len(all_errors) == 0, all_errors

    @staticmethod
    def _validate_single_command(command_widget) -> List[str]:
        """
        Valide les arguments d'une seule commande.

        Args:
            command_widget: Le widget de commande à valider

        Returns:
            Liste des messages d'erreur (vide si valide)
        """
        errors = []

        if not hasattr(command_widget, "command") or not hasattr(
            command_widget, "get_argument_values"
        ):
            return errors

        command = command_widget.command
        argument_values = command_widget.get_argument_values()

        # Utiliser la méthode de validation du modèle Command
        is_valid, validation_errors = command.validate_arguments(argument_values)

        if not is_valid:
            # Ajouter le nom de la commande aux erreurs
            for error in validation_errors:
                errors.append(f"[{command.name}] {error}")

        return errors

    @staticmethod
    def has_checked_commands(
        command_components: List,
        command_checkboxes: List[QCheckBox],
    ) -> bool:
        """
        Vérifie qu'au moins une commande est cochée.

        Args:
            command_components: Liste des widgets de commande
            command_checkboxes: Liste des checkboxes associées

        Returns:
            True si au moins une commande est cochée
        """
        if not command_components:
            return False

        if not command_checkboxes:
            # Pas de checkboxes = toutes les commandes sont actives
            return len(command_components) > 0

        return any(cb.isChecked() for cb in command_checkboxes)
