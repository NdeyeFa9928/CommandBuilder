"""
Tests pour la fonctionnalité de sélection des commandes via checkboxes.
"""

import pytest
from PySide6.QtWidgets import QApplication, QCheckBox

from command_builder.components.command_form import CommandForm
from command_builder.models.command import Command
from command_builder.models.task import Task
from command_builder.models.arguments import Argument, TaskArgument


@pytest.fixture
def app():
    """Fixture pour l'application Qt."""
    return QApplication.instance() or QApplication([])


@pytest.fixture
def sample_task():
    """Crée une tâche avec 3 commandes pour les tests."""
    cmd1 = Command(
        name="command1",
        description="First command",
        command="cmd1 {ARG1}",
        arguments=[
            Argument(code="ARG1", name="Argument 1", type="string", required=1)
        ],
    )
    cmd2 = Command(
        name="command2",
        description="Second command",
        command="cmd2 {ARG2}",
        arguments=[
            Argument(code="ARG2", name="Argument 2", type="string", required=1)
        ],
    )
    cmd3 = Command(
        name="command3",
        description="Third command",
        command="cmd3 {ARG3}",
        arguments=[
            Argument(code="ARG3", name="Argument 3", type="string", required=1)
        ],
    )

    task = Task(
        name="Test Task",
        description="Task with 3 commands",
        commands=[cmd1, cmd2, cmd3],
    )
    return task


def test_checkboxes_created_for_each_command(app, sample_task):
    """Vérifie qu'une checkbox est créée pour chaque commande."""
    form = CommandForm()
    form.set_task(sample_task)

    # Vérifier qu'il y a 3 checkboxes (une par commande)
    assert len(form.command_checkboxes) == 3
    assert all(isinstance(cb, QCheckBox) for cb in form.command_checkboxes)


def test_checkboxes_checked_by_default(app, sample_task):
    """Vérifie que toutes les checkboxes sont cochées par défaut."""
    form = CommandForm()
    form.set_task(sample_task)

    # Toutes les checkboxes doivent être cochées
    assert all(cb.isChecked() for cb in form.command_checkboxes)


def test_checkboxes_have_tooltip(app, sample_task):
    """Vérifie que les checkboxes ont un tooltip explicatif."""
    form = CommandForm()
    form.set_task(sample_task)

    # Vérifier que chaque checkbox a un tooltip
    for cb in form.command_checkboxes:
        assert cb.toolTip() != ""
        assert "ignorer" in cb.toolTip().lower() or "décochez" in cb.toolTip().lower()


def test_only_checked_commands_validated(app, sample_task, monkeypatch):
    """Vérifie que seules les commandes cochées sont validées."""
    form = CommandForm()
    form.set_task(sample_task)

    # Décocher la deuxième commande
    form.command_checkboxes[1].setChecked(False)

    # Remplir les arguments de la première et troisième commande
    form.command_components[0].argument_components["ARG1"]["component"].set_value("value1")
    form.command_components[2].argument_components["ARG3"]["component"].set_value("value3")
    # Ne pas remplir ARG2 (commande décochée)

    # Capturer les commandes émises
    emitted_commands = []

    def capture_commands(commands):
        emitted_commands.extend(commands)

    form.commands_to_execute.connect(capture_commands)

    # Exécuter
    form._on_execute_clicked()

    # Vérifier que seules 2 commandes sont émises (pas la décochée)
    assert len(emitted_commands) == 2
    assert emitted_commands[0]["name"] == "command1"
    assert emitted_commands[1]["name"] == "command3"


def test_error_if_no_command_checked(app, sample_task):
    """Vérifie qu'une erreur est affichée si aucune commande n'est cochée."""
    form = CommandForm()
    form.set_task(sample_task)

    # Décocher toutes les commandes
    for cb in form.command_checkboxes:
        cb.setChecked(False)

    # Capturer les commandes émises
    emitted_commands = []

    def capture_commands(commands):
        emitted_commands.extend(commands)

    form.commands_to_execute.connect(capture_commands)

    # Exécuter
    form._on_execute_clicked()

    # Vérifier qu'aucune commande n'est émise
    assert len(emitted_commands) == 0


def test_unchecked_command_not_validated(app, sample_task):
    """Vérifie qu'une commande décochée n'est pas validée (même si arguments manquants)."""
    form = CommandForm()
    form.set_task(sample_task)

    # Décocher la première commande
    form.command_checkboxes[0].setChecked(False)

    # Remplir seulement les commandes 2 et 3
    form.command_components[1].argument_components["ARG2"]["component"].set_value("value2")
    form.command_components[2].argument_components["ARG3"]["component"].set_value("value3")
    # Ne pas remplir ARG1 (mais commande décochée donc pas d'erreur)

    # Capturer les commandes émises
    emitted_commands = []

    def capture_commands(commands):
        emitted_commands.extend(commands)

    form.commands_to_execute.connect(capture_commands)

    # Exécuter - ne doit pas afficher d'erreur pour ARG1
    form._on_execute_clicked()

    # Vérifier que 2 commandes sont émises
    assert len(emitted_commands) == 2
    assert emitted_commands[0]["name"] == "command2"
    assert emitted_commands[1]["name"] == "command3"


def test_checkboxes_cleared_on_task_change(app, sample_task):
    """Vérifie que les checkboxes sont nettoyées lors du changement de tâche."""
    form = CommandForm()
    form.set_task(sample_task)

    # Vérifier qu'il y a 3 checkboxes
    assert len(form.command_checkboxes) == 3

    # Créer une nouvelle tâche avec 2 commandes
    cmd1 = Command(
        name="new_cmd1",
        description="New command 1",
        command="newcmd1",
        arguments=[],
    )
    cmd2 = Command(
        name="new_cmd2",
        description="New command 2",
        command="newcmd2",
        arguments=[],
    )
    new_task = Task(
        name="New Task",
        description="Task with 2 commands",
        commands=[cmd1, cmd2],
    )

    # Charger la nouvelle tâche
    form.set_task(new_task)

    # Vérifier qu'il y a maintenant 2 checkboxes
    assert len(form.command_checkboxes) == 2


def test_partial_execution_scenario(app, sample_task):
    """
    Scénario réel : Une tâche avec 3 commandes plante à la commande 2.
    L'utilisateur décoche la commande 1 (déjà réussie) et relance.
    """
    form = CommandForm()
    form.set_task(sample_task)

    # Remplir tous les arguments
    form.command_components[0].argument_components["ARG1"]["component"].set_value("value1")
    form.command_components[1].argument_components["ARG2"]["component"].set_value("value2")
    form.command_components[2].argument_components["ARG3"]["component"].set_value("value3")

    # Simuler que la commande 1 a déjà été exécutée avec succès
    # L'utilisateur décoche la commande 1
    form.command_checkboxes[0].setChecked(False)

    # Capturer les commandes émises
    emitted_commands = []

    def capture_commands(commands):
        emitted_commands.extend(commands)

    form.commands_to_execute.connect(capture_commands)

    # Exécuter
    form._on_execute_clicked()

    # Vérifier que seules les commandes 2 et 3 sont exécutées
    assert len(emitted_commands) == 2
    assert emitted_commands[0]["name"] == "command2"
    assert emitted_commands[1]["name"] == "command3"
    # La commande 1 ne doit pas être dans la liste
    assert not any(cmd["name"] == "command1" for cmd in emitted_commands)


def test_checkbox_state_independent_per_command(app, sample_task):
    """Vérifie que l'état de chaque checkbox est indépendant."""
    form = CommandForm()
    form.set_task(sample_task)

    # Décocher seulement la commande du milieu
    form.command_checkboxes[0].setChecked(True)
    form.command_checkboxes[1].setChecked(False)
    form.command_checkboxes[2].setChecked(True)

    # Vérifier les états
    assert form.command_checkboxes[0].isChecked() is True
    assert form.command_checkboxes[1].isChecked() is False
    assert form.command_checkboxes[2].isChecked() is True
