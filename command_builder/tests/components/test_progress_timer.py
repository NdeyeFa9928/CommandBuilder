"""
Tests pour le chronomètre visuel de la console.
Vérifie que le sablier animé et le temps écoulé s'affichent correctement
pendant l'exécution des commandes.
"""

import datetime
from unittest.mock import patch

import pytest
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from command_builder.components.console_output import ConsoleOutput


@pytest.fixture
def qapp():
    """Fixture pour l'application Qt."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def console_output(qapp):
    """Fixture pour créer un ConsoleOutput."""
    return ConsoleOutput()


class TestElapsedTimer:
    """Tests pour le chronomètre visuel."""

    def test_elapsed_timer_initialized_to_none(self, console_output):
        """Vérifie que le timer est initialisé à None."""
        assert console_output._elapsed_timer is None
        assert console_output._execution_start_time is None

    def test_start_elapsed_timer_creates_timer(self, console_output):
        """Vérifie que _start_elapsed_timer crée un QTimer."""
        console_output._start_elapsed_timer()

        assert console_output._elapsed_timer is not None
        assert isinstance(console_output._elapsed_timer, QTimer)
        assert console_output._elapsed_timer.isActive()
        assert console_output._execution_start_time is not None

        # Nettoyer
        console_output._stop_elapsed_timer()

    def test_stop_elapsed_timer_stops_and_clears(self, console_output):
        """Vérifie que _stop_elapsed_timer arrête et supprime le timer."""
        console_output._start_elapsed_timer()
        console_output._stop_elapsed_timer()

        assert console_output._elapsed_timer is None

    def test_stop_elapsed_timer_resets_label(self, console_output):
        """Vérifie que le label est réinitialisé à 00:00 à l'arrêt du timer."""
        console_output._start_elapsed_timer()
        # Le label devrait contenir quelque chose
        assert console_output.label_timer.text() != ""

        console_output._stop_elapsed_timer()
        # Le label devrait être réinitialisé à 00:00
        assert "00:00" in console_output.label_timer.text()

    def test_update_elapsed_display_shows_time(self, console_output):
        """Vérifie que l'affichage montre le temps écoulé."""
        console_output._execution_start_time = datetime.datetime.now() - datetime.timedelta(
            seconds=65  # 1 minute et 5 secondes
        )

        console_output._update_elapsed_display()

        text = console_output.label_timer.text()
        # Devrait afficher quelque chose comme "⏳ 01:05" ou "⌛ 01:05"
        assert "01:05" in text

    def test_update_elapsed_display_alternates_hourglass(self, console_output):
        """Vérifie que le sablier alterne entre ⏳ et ⌛."""
        console_output._execution_start_time = datetime.datetime.now()
        console_output._hourglass_index = 0

        # Premier appel
        console_output._update_elapsed_display()
        text1 = console_output.label_timer.text()

        # Deuxième appel
        console_output._update_elapsed_display()
        text2 = console_output.label_timer.text()

        # Les deux textes devraient avoir des sabliers différents
        assert text1[0] != text2[0]  # Premier caractère (sablier) différent

    def test_timer_stopped_on_all_commands_finished(self, console_output):
        """Vérifie que le timer est arrêté quand toutes les commandes sont terminées."""
        console_output._start_elapsed_timer()

        # Simuler la fin de toutes les commandes
        console_output._on_all_commands_finished()

        assert console_output._elapsed_timer is None
        assert "00:00" in console_output.label_timer.text()

    def test_timer_stopped_on_user_stop(self, console_output):
        """Vérifie que le timer est arrêté lors d'un arrêt utilisateur."""
        console_output._start_elapsed_timer()

        # Simuler un arrêt utilisateur
        console_output._on_execution_stopped_by_user()

        assert console_output._elapsed_timer is None
        assert "00:00" in console_output.label_timer.text()

    def test_timer_stopped_on_error(self, console_output):
        """Vérifie que le timer est arrêté en cas d'erreur."""
        console_output._start_elapsed_timer()

        # Simuler une erreur
        console_output._on_execution_stopped_with_error()

        assert console_output._elapsed_timer is None
        assert "00:00" in console_output.label_timer.text()

    def test_timer_started_on_execute_commands(self, console_output):
        """Vérifie que le timer démarre lors de l'exécution des commandes."""
        commands = [{"name": "Test", "command": "echo test"}]

        # Mock l'exécuteur pour éviter l'exécution réelle
        with patch.object(console_output.executor_service, "execute_command"):
            console_output.execute_commands(commands)

        assert console_output._elapsed_timer is not None
        assert console_output._execution_start_time is not None

        # Nettoyer
        console_output._stop_elapsed_timer()

    def test_on_command_output_appends_text(self, console_output):
        """Vérifie que _on_command_output ajoute le texte à la console."""
        console_output._on_command_output("test output")

        assert "test output" in console_output.text_edit_console.toPlainText()
