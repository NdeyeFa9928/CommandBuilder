"""
Service de gestion de l'état du formulaire.

Ce service centralise la logique de sauvegarde et restauration
des valeurs du formulaire (cache par tâche).
"""

from typing import Any, Dict, List, Optional


class FormStateManager:
    """
    Service responsable de la gestion du cache des valeurs du formulaire.
    
    Extrait de CommandForm pour réduire la complexité cyclomatique
    et améliorer la testabilité.
    """

    def __init__(self):
        """Initialise le gestionnaire d'état."""
        self._values_cache: Dict[str, Dict[str, Any]] = {}

    def save_state(
        self,
        task_name: str,
        task_argument_components: List[Dict],
        command_components: List,
        command_checkboxes: List,
    ) -> None:
        """
        Sauvegarde les valeurs actuelles dans le cache.

        Args:
            task_name: Nom de la tâche
            task_argument_components: Liste des composants d'arguments partagés
            command_components: Liste des widgets de commande
            command_checkboxes: Liste des checkboxes
        """
        cached_values = {}

        # Sauvegarder les valeurs des arguments partagés
        cached_values.update(
            self._save_shared_arguments(task_argument_components)
        )

        # Sauvegarder les valeurs des arguments de chaque commande
        cached_values.update(
            self._save_command_arguments(command_components)
        )

        # Sauvegarder l'état des checkboxes
        cached_values.update(
            self._save_checkbox_states(command_checkboxes)
        )

        self._values_cache[task_name] = cached_values

    def restore_state(
        self,
        task_name: str,
        task_argument_components: List[Dict],
        command_components: List,
        command_checkboxes: List,
    ) -> Dict[str, str]:
        """
        Restaure les valeurs depuis le cache.

        Args:
            task_name: Nom de la tâche
            task_argument_components: Liste des composants d'arguments partagés
            command_components: Liste des widgets de commande
            command_checkboxes: Liste des checkboxes

        Returns:
            Dictionnaire des valeurs partagées restaurées
        """
        if task_name not in self._values_cache:
            return {}

        cached_values = self._values_cache[task_name]
        shared_values = {}

        # Restaurer les valeurs des arguments partagés
        shared_values = self._restore_shared_arguments(
            cached_values, task_argument_components
        )

        # Restaurer les valeurs des arguments de chaque commande
        self._restore_command_arguments(cached_values, command_components)

        # Restaurer l'état des checkboxes
        self._restore_checkbox_states(cached_values, command_checkboxes)

        return shared_values

    def has_cached_state(self, task_name: str) -> bool:
        """
        Vérifie si une tâche a un état en cache.

        Args:
            task_name: Nom de la tâche

        Returns:
            True si un état est en cache
        """
        return task_name in self._values_cache

    def clear_cache(self, task_name: Optional[str] = None) -> None:
        """
        Efface le cache.

        Args:
            task_name: Si fourni, efface uniquement cette tâche. Sinon, efface tout.
        """
        if task_name:
            self._values_cache.pop(task_name, None)
        else:
            self._values_cache.clear()

    def _save_shared_arguments(
        self, task_argument_components: List[Dict]
    ) -> Dict[str, Any]:
        """Sauvegarde les valeurs des arguments partagés."""
        cached = {}
        for arg_data in task_argument_components:
            component = arg_data["component"]
            if hasattr(component, "get_argument") and hasattr(component, "get_value"):
                arg = component.get_argument()
                value = component.get_value()
                if value:  # Ne sauvegarder que les valeurs non vides
                    cached[f"shared_{arg.code}"] = value
        return cached

    def _save_command_arguments(self, command_components: List) -> Dict[str, Any]:
        """Sauvegarde les valeurs des arguments de chaque commande."""
        cached = {}
        for command_widget in command_components:
            if hasattr(command_widget, "command") and hasattr(
                command_widget, "argument_components"
            ):
                cmd_name = command_widget.command.name
                for arg_code, arg_data in command_widget.argument_components.items():
                    component = arg_data["component"]
                    if hasattr(component, "get_value"):
                        value = component.get_value()
                        if value:  # Ne sauvegarder que les valeurs non vides
                            cached[f"cmd_{cmd_name}_{arg_code}"] = value
        return cached

    def _save_checkbox_states(self, command_checkboxes: List) -> Dict[str, bool]:
        """Sauvegarde l'état des checkboxes."""
        cached = {}
        for i, checkbox in enumerate(command_checkboxes):
            cached[f"checkbox_{i}"] = checkbox.isChecked()
        return cached

    def _restore_shared_arguments(
        self, cached_values: Dict[str, Any], task_argument_components: List[Dict]
    ) -> Dict[str, str]:
        """Restaure les valeurs des arguments partagés."""
        shared_values = {}
        for arg_data in task_argument_components:
            component = arg_data["component"]
            if hasattr(component, "get_argument") and hasattr(component, "set_value"):
                arg = component.get_argument()
                cache_key = f"shared_{arg.code}"
                if cache_key in cached_values:
                    component.set_value(cached_values[cache_key])
                    shared_values[arg.code] = cached_values[cache_key]
        return shared_values

    def _restore_command_arguments(
        self, cached_values: Dict[str, Any], command_components: List
    ) -> None:
        """Restaure les valeurs des arguments de chaque commande."""
        for command_widget in command_components:
            if hasattr(command_widget, "command") and hasattr(
                command_widget, "argument_components"
            ):
                cmd_name = command_widget.command.name
                for arg_code, arg_data in command_widget.argument_components.items():
                    component = arg_data["component"]
                    cache_key = f"cmd_{cmd_name}_{arg_code}"
                    if cache_key in cached_values and hasattr(component, "set_value"):
                        component.set_value(cached_values[cache_key])

    def _restore_checkbox_states(
        self, cached_values: Dict[str, Any], command_checkboxes: List
    ) -> None:
        """Restaure l'état des checkboxes."""
        for i, checkbox in enumerate(command_checkboxes):
            cache_key = f"checkbox_{i}"
            if cache_key in cached_values:
                checkbox.setChecked(cached_values[cache_key])
