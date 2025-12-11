"""
Tests pour le service CommandValidator.
"""

import pytest
from unittest.mock import MagicMock, patch

from PySide6.QtWidgets import QApplication, QCheckBox

from command_builder.services.command_validator import CommandValidator


@pytest.fixture
def app():
    """Fixture pour l'application Qt."""
    return QApplication.instance() or QApplication([])


@pytest.fixture
def mock_command_widget():
    """Crée un mock de widget de commande."""
    widget = MagicMock()
    widget.command = MagicMock()
    widget.command.name = "TestCommand"
    widget.command.validate_arguments = MagicMock(return_value=(True, []))
    widget.get_argument_values = MagicMock(return_value={"ARG1": "value1"})
    return widget


@pytest.fixture
def mock_invalid_command_widget():
    """Crée un mock de widget de commande invalide."""
    widget = MagicMock()
    widget.command = MagicMock()
    widget.command.name = "InvalidCommand"
    widget.command.validate_arguments = MagicMock(
        return_value=(False, ["Le champ 'Fichier' est obligatoire"])
    )
    widget.get_argument_values = MagicMock(return_value={"ARG1": ""})
    return widget


class TestCommandValidatorValidation:
    """Tests pour la validation des commandes."""

    def test_validate_empty_components(self, app):
        """Valide une liste vide de composants."""
        is_valid, errors = CommandValidator.validate_commands([], [])
        assert is_valid is True
        assert errors == []

    def test_validate_single_valid_command(self, app, mock_command_widget):
        """Valide une seule commande valide."""
        checkbox = QCheckBox()
        checkbox.setChecked(True)

        is_valid, errors = CommandValidator.validate_commands(
            [mock_command_widget], [checkbox]
        )

        assert is_valid is True
        assert errors == []

    def test_validate_single_invalid_command(self, app, mock_invalid_command_widget):
        """Valide une seule commande invalide."""
        checkbox = QCheckBox()
        checkbox.setChecked(True)

        is_valid, errors = CommandValidator.validate_commands(
            [mock_invalid_command_widget], [checkbox]
        )

        assert is_valid is False
        assert len(errors) == 1
        assert "[InvalidCommand]" in errors[0]

    def test_unchecked_command_not_validated(self, app, mock_invalid_command_widget):
        """Une commande décochée n'est pas validée."""
        checkbox = QCheckBox()
        checkbox.setChecked(False)

        is_valid, errors = CommandValidator.validate_commands(
            [mock_invalid_command_widget], [checkbox]
        )

        assert is_valid is True
        assert errors == []

    def test_validate_multiple_commands_mixed(
        self, app, mock_command_widget, mock_invalid_command_widget
    ):
        """Valide plusieurs commandes avec des résultats mixtes."""
        checkbox1 = QCheckBox()
        checkbox1.setChecked(True)
        checkbox2 = QCheckBox()
        checkbox2.setChecked(True)

        is_valid, errors = CommandValidator.validate_commands(
            [mock_command_widget, mock_invalid_command_widget],
            [checkbox1, checkbox2],
        )

        assert is_valid is False
        assert len(errors) == 1

    def test_validate_without_checkboxes(self, app, mock_command_widget):
        """Valide sans checkboxes (toutes les commandes actives)."""
        is_valid, errors = CommandValidator.validate_commands(
            [mock_command_widget], []
        )

        assert is_valid is True
        assert errors == []


class TestCommandValidatorHasCheckedCommands:
    """Tests pour la vérification des commandes cochées."""

    def test_has_checked_commands_empty(self, app):
        """Liste vide = pas de commandes cochées."""
        assert CommandValidator.has_checked_commands([], []) is False

    def test_has_checked_commands_all_checked(self, app, mock_command_widget):
        """Toutes les commandes cochées."""
        checkbox = QCheckBox()
        checkbox.setChecked(True)

        assert CommandValidator.has_checked_commands(
            [mock_command_widget], [checkbox]
        ) is True

    def test_has_checked_commands_none_checked(self, app, mock_command_widget):
        """Aucune commande cochée."""
        checkbox = QCheckBox()
        checkbox.setChecked(False)

        assert CommandValidator.has_checked_commands(
            [mock_command_widget], [checkbox]
        ) is False

    def test_has_checked_commands_no_checkboxes(self, app, mock_command_widget):
        """Sans checkboxes = toutes actives."""
        assert CommandValidator.has_checked_commands(
            [mock_command_widget], []
        ) is True
