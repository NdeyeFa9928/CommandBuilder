"""
Tests pour le timer de progression de la console.
Vérifie que le message "[INFO] Commande en cours d'exécution..." s'affiche
périodiquement lorsqu'une commande ne produit pas de sortie.
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


class TestProgressTimer:
    """Tests pour le timer de progression."""

    def test_progress_timer_initialized_to_none(self, console_output):
        """Vérifie que le timer est initialisé à None."""
        assert console_output._progress_timer is None
        assert console_output._last_output_time is None

    def test_start_progress_timer_creates_timer(self, console_output):
        """Vérifie que _start_progress_timer crée un QTimer."""
        console_output._start_progress_timer()

        assert console_output._progress_timer is not None
        assert isinstance(console_output._progress_timer, QTimer)
        assert console_output._progress_timer.isActive()

        # Nettoyer
        console_output._stop_progress_timer()

    def test_stop_progress_timer_stops_and_clears(self, console_output):
        """Vérifie que _stop_progress_timer arrête et supprime le timer."""
        console_output._start_progress_timer()
        console_output._stop_progress_timer()

        assert console_output._progress_timer is None

    def test_check_progress_shows_message_after_delay(self, console_output):
        """Vérifie que le message de progression s'affiche après le délai (3s)."""
        # Simuler un temps passé depuis la dernière sortie (>3 secondes)
        console_output._last_output_time = datetime.datetime.now() - datetime.timedelta(
            seconds=4
        )

        # Appeler _check_progress
        console_output._check_progress()

        # Vérifier que le message a été affiché
        text = console_output.text_edit_console.toPlainText()
        assert "[INFO] Commande en cours d'exécution..." in text

    def test_check_progress_repeats_message_periodically(self, console_output):
        """Vérifie que le message s'affiche plusieurs fois périodiquement."""
        # Premier appel après 4 secondes
        console_output._last_output_time = datetime.datetime.now() - datetime.timedelta(
            seconds=4
        )
        console_output._check_progress()

        # Simuler 3 secondes de plus (le timestamp a été réinitialisé)
        console_output._last_output_time = datetime.datetime.now() - datetime.timedelta(
            seconds=4
        )
        console_output._check_progress()

        # Vérifier que le message apparaît 2 fois
        text = console_output.text_edit_console.toPlainText()
        assert text.count("[INFO] Commande en cours d'exécution...") == 2

    def test_check_progress_resets_timestamp(self, console_output):
        """Vérifie que le timestamp est réinitialisé après affichage du message."""
        old_time = datetime.datetime.now() - datetime.timedelta(seconds=10)
        console_output._last_output_time = old_time

        console_output._check_progress()

        # Le timestamp doit être récent (réinitialisé)
        assert console_output._last_output_time > old_time

    def test_check_progress_does_nothing_if_recent_output(self, console_output):
        """Vérifie qu'aucun message n'est affiché si la sortie est récente."""
        console_output._last_output_time = datetime.datetime.now()

        console_output._check_progress()

        text = console_output.text_edit_console.toPlainText()
        assert "[INFO] Commande en cours d'exécution..." not in text

    def test_on_command_output_updates_last_output_time(self, console_output):
        """Vérifie que _on_command_output met à jour le timestamp."""
        old_time = datetime.datetime.now() - datetime.timedelta(seconds=10)
        console_output._last_output_time = old_time

        console_output._on_command_output("test output")

        assert console_output._last_output_time > old_time
        assert "test output" in console_output.text_edit_console.toPlainText()

    def test_timer_stopped_on_command_finished(self, console_output):
        """Vérifie que le timer est arrêté quand une commande se termine."""
        console_output._start_progress_timer()
        console_output.command_start_time = datetime.datetime.now()

        # Simuler la fin d'une commande
        console_output._on_single_command_finished(0)

        assert console_output._progress_timer is None

    def test_timer_stopped_on_user_stop(self, console_output):
        """Vérifie que le timer est arrêté lors d'un arrêt utilisateur."""
        console_output._start_progress_timer()

        # Simuler un arrêt utilisateur
        console_output._on_execution_stopped_by_user()

        assert console_output._progress_timer is None

    def test_timer_stopped_on_stop_clicked(self, console_output):
        """Vérifie que le timer est arrêté lors du clic sur Stop."""
        console_output._start_progress_timer()

        # Simuler un clic sur Stop
        with patch.object(console_output.executor_service, "request_stop"):
            console_output._on_stop_clicked()

        assert console_output._progress_timer is None

    def test_progress_reset_on_new_command(self, console_output):
        """Vérifie que la progression est réinitialisée pour chaque commande."""
        # Simuler un ancien timestamp
        console_output._last_output_time = datetime.datetime.now() - datetime.timedelta(
            seconds=10
        )

        # Préparer une nouvelle commande
        console_output.commands_queue = [{"name": "Test", "command": "echo test"}]
        console_output.current_command_index = 0

        # Mock l'exécuteur pour éviter l'exécution réelle
        with patch.object(console_output.executor_service, "execute_command"):
            console_output._execute_next_command()

        # Vérifier la réinitialisation (timestamp récent)
        elapsed = (datetime.datetime.now() - console_output._last_output_time).total_seconds()
        assert elapsed < 1  # Moins d'une seconde
