"""
Tests pour le service CommandBuilderService.
"""

import pytest
from unittest.mock import MagicMock

from PySide6.QtWidgets import QApplication, QCheckBox

from command_builder.services.command_builder_service import CommandBuilderService


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
    widget._build_full_command = MagicMock(return_value="test.exe --arg value")
    return widget


class TestCommandBuilderServiceBuildList:
    """Tests pour la construction de la liste des commandes."""

    def test_build_empty_list(self, app):
        """Construit une liste vide."""
        result = CommandBuilderService.build_commands_list([], [])
        assert result == []

    def test_build_single_command(self, app, mock_command_widget):
        """Construit une liste avec une seule commande."""
        checkbox = QCheckBox()
        checkbox.setChecked(True)

        result = CommandBuilderService.build_commands_list(
            [mock_command_widget], [checkbox]
        )

        assert len(result) == 1
        assert result[0]["name"] == "TestCommand"
        assert result[0]["command"] == "test.exe --arg value"

    def test_build_unchecked_command_excluded(self, app, mock_command_widget):
        """Une commande décochée est exclue."""
        checkbox = QCheckBox()
        checkbox.setChecked(False)

        result = CommandBuilderService.build_commands_list(
            [mock_command_widget], [checkbox]
        )

        assert result == []

    def test_build_multiple_commands_partial_checked(self, app):
        """Construit avec plusieurs commandes partiellement cochées."""
        widget1 = MagicMock()
        widget1.command = MagicMock()
        widget1.command.name = "Command1"
        widget1._build_full_command = MagicMock(return_value="cmd1.exe")

        widget2 = MagicMock()
        widget2.command = MagicMock()
        widget2.command.name = "Command2"
        widget2._build_full_command = MagicMock(return_value="cmd2.exe")

        widget3 = MagicMock()
        widget3.command = MagicMock()
        widget3.command.name = "Command3"
        widget3._build_full_command = MagicMock(return_value="cmd3.exe")

        checkbox1 = QCheckBox()
        checkbox1.setChecked(True)
        checkbox2 = QCheckBox()
        checkbox2.setChecked(False)  # Décochée
        checkbox3 = QCheckBox()
        checkbox3.setChecked(True)

        result = CommandBuilderService.build_commands_list(
            [widget1, widget2, widget3],
            [checkbox1, checkbox2, checkbox3],
        )

        assert len(result) == 2
        assert result[0]["name"] == "Command1"
        assert result[1]["name"] == "Command3"

    def test_build_without_checkboxes(self, app, mock_command_widget):
        """Construit sans checkboxes (toutes les commandes incluses)."""
        result = CommandBuilderService.build_commands_list(
            [mock_command_widget], []
        )

        assert len(result) == 1
        assert result[0]["name"] == "TestCommand"

    def test_build_widget_without_build_method(self, app):
        """Widget sans méthode _build_full_command est ignoré."""
        widget = MagicMock(spec=[])  # Pas de méthode _build_full_command
        checkbox = QCheckBox()
        checkbox.setChecked(True)

        result = CommandBuilderService.build_commands_list(
            [widget], [checkbox]
        )

        assert result == []

    def test_build_preserves_order(self, app):
        """L'ordre des commandes est préservé."""
        widgets = []
        checkboxes = []
        for i in range(5):
            widget = MagicMock()
            widget.command = MagicMock()
            widget.command.name = f"Command{i}"
            widget._build_full_command = MagicMock(return_value=f"cmd{i}.exe")
            widgets.append(widget)

            checkbox = QCheckBox()
            checkbox.setChecked(True)
            checkboxes.append(checkbox)

        result = CommandBuilderService.build_commands_list(widgets, checkboxes)

        assert len(result) == 5
        for i, cmd in enumerate(result):
            assert cmd["name"] == f"Command{i}"
