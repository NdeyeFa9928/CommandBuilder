"""
Tests pour le service FormStateManager.
"""

import pytest
from unittest.mock import MagicMock

from PySide6.QtWidgets import QApplication, QCheckBox

from command_builder.services.form_state_manager import FormStateManager


@pytest.fixture
def app():
    """Fixture pour l'application Qt."""
    return QApplication.instance() or QApplication([])


@pytest.fixture
def state_manager():
    """Crée une instance de FormStateManager."""
    return FormStateManager()


@pytest.fixture
def mock_task_argument_component():
    """Crée un mock de composant d'argument de tâche."""
    component = MagicMock()
    arg = MagicMock()
    arg.code = "SHARED_ARG"
    component.get_argument = MagicMock(return_value=arg)
    component.get_value = MagicMock(return_value="shared_value")
    component.set_value = MagicMock()
    return {"component": component, "label": MagicMock()}


@pytest.fixture
def mock_command_component():
    """Crée un mock de composant de commande."""
    widget = MagicMock()
    widget.command = MagicMock()
    widget.command.name = "TestCommand"

    arg_component = MagicMock()
    arg_component.get_value = MagicMock(return_value="cmd_value")
    arg_component.set_value = MagicMock()

    widget.argument_components = {
        "CMD_ARG": {"component": arg_component}
    }
    return widget


class TestFormStateManagerSaveRestore:
    """Tests pour la sauvegarde et restauration d'état."""

    def test_save_and_restore_shared_arguments(
        self, app, state_manager, mock_task_argument_component
    ):
        """Sauvegarde et restaure les arguments partagés."""
        checkbox = QCheckBox()
        checkbox.setChecked(True)

        # Sauvegarder
        state_manager.save_state(
            task_name="TestTask",
            task_argument_components=[mock_task_argument_component],
            command_components=[],
            command_checkboxes=[checkbox],
        )

        # Vérifier que l'état est en cache
        assert state_manager.has_cached_state("TestTask")

        # Restaurer
        restored = state_manager.restore_state(
            task_name="TestTask",
            task_argument_components=[mock_task_argument_component],
            command_components=[],
            command_checkboxes=[checkbox],
        )

        # Vérifier que set_value a été appelé
        mock_task_argument_component["component"].set_value.assert_called_with(
            "shared_value"
        )
        assert "SHARED_ARG" in restored

    def test_save_and_restore_command_arguments(
        self, app, state_manager, mock_command_component
    ):
        """Sauvegarde et restaure les arguments de commande."""
        checkbox = QCheckBox()
        checkbox.setChecked(True)

        # Sauvegarder
        state_manager.save_state(
            task_name="TestTask",
            task_argument_components=[],
            command_components=[mock_command_component],
            command_checkboxes=[checkbox],
        )

        # Restaurer
        state_manager.restore_state(
            task_name="TestTask",
            task_argument_components=[],
            command_components=[mock_command_component],
            command_checkboxes=[checkbox],
        )

        # Vérifier que set_value a été appelé sur le composant d'argument
        arg_component = mock_command_component.argument_components["CMD_ARG"]["component"]
        arg_component.set_value.assert_called_with("cmd_value")

    def test_save_and_restore_checkbox_states(self, app, state_manager):
        """Sauvegarde et restaure l'état des checkboxes."""
        checkbox1 = QCheckBox()
        checkbox1.setChecked(True)
        checkbox2 = QCheckBox()
        checkbox2.setChecked(False)

        # Sauvegarder
        state_manager.save_state(
            task_name="TestTask",
            task_argument_components=[],
            command_components=[],
            command_checkboxes=[checkbox1, checkbox2],
        )

        # Modifier les états
        checkbox1.setChecked(False)
        checkbox2.setChecked(True)

        # Restaurer
        state_manager.restore_state(
            task_name="TestTask",
            task_argument_components=[],
            command_components=[],
            command_checkboxes=[checkbox1, checkbox2],
        )

        # Vérifier les états restaurés
        assert checkbox1.isChecked() is True
        assert checkbox2.isChecked() is False

    def test_restore_nonexistent_task(self, app, state_manager):
        """Restaurer une tâche inexistante retourne un dict vide."""
        checkbox = QCheckBox()

        result = state_manager.restore_state(
            task_name="NonExistentTask",
            task_argument_components=[],
            command_components=[],
            command_checkboxes=[checkbox],
        )

        assert result == {}


class TestFormStateManagerCache:
    """Tests pour la gestion du cache."""

    def test_has_cached_state_false(self, state_manager):
        """Vérifie qu'une tâche non cachée retourne False."""
        assert state_manager.has_cached_state("UnknownTask") is False

    def test_has_cached_state_true(self, app, state_manager):
        """Vérifie qu'une tâche cachée retourne True."""
        state_manager.save_state(
            task_name="CachedTask",
            task_argument_components=[],
            command_components=[],
            command_checkboxes=[],
        )

        assert state_manager.has_cached_state("CachedTask") is True

    def test_clear_cache_specific_task(self, app, state_manager):
        """Efface le cache d'une tâche spécifique."""
        state_manager.save_state(
            task_name="Task1",
            task_argument_components=[],
            command_components=[],
            command_checkboxes=[],
        )
        state_manager.save_state(
            task_name="Task2",
            task_argument_components=[],
            command_components=[],
            command_checkboxes=[],
        )

        state_manager.clear_cache("Task1")

        assert state_manager.has_cached_state("Task1") is False
        assert state_manager.has_cached_state("Task2") is True

    def test_clear_cache_all(self, app, state_manager):
        """Efface tout le cache."""
        state_manager.save_state(
            task_name="Task1",
            task_argument_components=[],
            command_components=[],
            command_checkboxes=[],
        )
        state_manager.save_state(
            task_name="Task2",
            task_argument_components=[],
            command_components=[],
            command_checkboxes=[],
        )

        state_manager.clear_cache()

        assert state_manager.has_cached_state("Task1") is False
        assert state_manager.has_cached_state("Task2") is False

    def test_empty_values_not_saved(self, app, state_manager):
        """Les valeurs vides ne sont pas sauvegardées."""
        component = MagicMock()
        arg = MagicMock()
        arg.code = "EMPTY_ARG"
        component.get_argument = MagicMock(return_value=arg)
        component.get_value = MagicMock(return_value="")  # Valeur vide
        component.set_value = MagicMock()

        state_manager.save_state(
            task_name="TestTask",
            task_argument_components=[{"component": component, "label": MagicMock()}],
            command_components=[],
            command_checkboxes=[],
        )

        # Restaurer
        state_manager.restore_state(
            task_name="TestTask",
            task_argument_components=[{"component": component, "label": MagicMock()}],
            command_components=[],
            command_checkboxes=[],
        )

        # set_value ne devrait pas être appelé pour une valeur vide
        component.set_value.assert_not_called()
