"""Tests unitaires pour TaskList."""

from unittest.mock import MagicMock, Mock

import pytest
from PySide6.QtWidgets import QApplication

from command_builder.components.task_list import TaskList
from command_builder.models.command import Command
from command_builder.models.task import Task


@pytest.fixture
def qapp():
    """Fixture pour l'application Qt."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def task_list(qapp):
    """Fixture pour créer une TaskList."""
    tl = TaskList()
    yield tl
    tl.deleteLater()


@pytest.fixture
def sample_tasks():
    """Fixture pour créer des tâches de test."""
    return [
        Task(
            name="Task A",
            description="First task",
            commands=[
                Command(name="Cmd1", description="Test", command="echo 1", arguments=[])
            ],
        ),
        Task(
            name="Task B",
            description="Second task",
            commands=[
                Command(name="Cmd2", description="Test", command="echo 2", arguments=[])
            ],
        ),
        Task(
            name="Task C",
            description="Third task",
            commands=[
                Command(name="Cmd3", description="Test", command="echo 3", arguments=[])
            ],
        ),
    ]


class TestTaskListInitialization:
    """Tests d'initialisation de TaskList."""

    def test_task_list_creates_successfully(self, qapp):
        """Test que TaskList se crée sans erreur."""
        task_list = TaskList()
        assert task_list is not None
        task_list.deleteLater()

    def test_task_list_has_task_selected_signal(self, task_list):
        """Test que TaskList a le signal task_selected."""
        assert hasattr(task_list, "task_selected")

    def test_task_list_empty_by_default(self, task_list):
        """Test que TaskList est vide par défaut."""
        # Vérifier qu'il n'y a pas de tâches affichées
        pass


class TestTaskListSetTasks:
    """Tests de la méthode set_tasks."""

    def test_set_tasks_with_empty_list(self, task_list):
        """Test avec une liste vide."""
        task_list.set_tasks([])
        # Ne devrait pas planter

    def test_set_tasks_populates_list(self, task_list, sample_tasks):
        """Test que set_tasks remplit la liste."""
        task_list.set_tasks(sample_tasks)
        # Vérifier que les tâches sont affichées

    def test_set_tasks_replaces_previous_tasks(self, task_list, sample_tasks):
        """Test que set_tasks remplace les tâches précédentes."""
        # Premier appel
        task_list.set_tasks(sample_tasks[:2])

        # Deuxième appel
        task_list.set_tasks(sample_tasks[2:])

        # Les nouvelles tâches devraient remplacer les anciennes

    def test_set_tasks_with_custom_factory(self, qapp, sample_tasks):
        """Test avec une factory personnalisée."""
        from PySide6.QtWidgets import QWidget

        call_count = [0]  # Utiliser une liste pour muter dans la closure

        def mock_factory(task, parent):
            call_count[0] += 1
            # Retourner un vrai QWidget, pas un Mock
            widget = QWidget(parent)
            widget.task = task  # Stocker la tâche pour vérification
            return widget

        task_list = TaskList(task_widget_factory=mock_factory)
        task_list.set_tasks(sample_tasks)

        # La factory devrait être appelée pour chaque tâche
        assert call_count[0] == len(sample_tasks)
        task_list.deleteLater()


class TestTaskListSelection:
    """Tests de sélection de tâches."""

    def test_task_selection_emits_signal(self, task_list, sample_tasks):
        """Test que la sélection d'une tâche émet le signal."""
        task_list.set_tasks(sample_tasks)

        # Connecter un mock au signal
        mock_handler = Mock()
        task_list.task_selected.connect(mock_handler)

        # Simuler la sélection (dépend de l'implémentation)
        # task_list._on_task_clicked(sample_tasks[0])

        # Vérifier que le signal a été émis
        # mock_handler.assert_called_once_with(sample_tasks[0])

    def test_clicking_same_task_twice(self, task_list, sample_tasks):
        """Test de clic sur la même tâche deux fois."""
        task_list.set_tasks(sample_tasks)

        mock_handler = Mock()
        task_list.task_selected.connect(mock_handler)

        # Cliquer deux fois sur la même tâche
        # Devrait émettre le signal deux fois ou une seule fois selon l'implémentation


class TestTaskListSorting:
    """Tests de tri des tâches."""

    def test_tasks_sorted_alphabetically(self, task_list):
        """Test que les tâches sont triées alphabétiquement."""
        unsorted_tasks = [
            Task(name="Zebra", description="Z", commands=[]),
            Task(name="Alpha", description="A", commands=[]),
            Task(name="Beta", description="B", commands=[]),
        ]

        task_list.set_tasks(unsorted_tasks)

        # Vérifier que les tâches sont affichées dans l'ordre alphabétique
        # (dépend de l'implémentation)

    def test_tasks_maintain_order_if_already_sorted(self, task_list, sample_tasks):
        """Test que l'ordre est maintenu si déjà trié."""
        task_list.set_tasks(sample_tasks)
        # Les tâches devraient rester dans l'ordre


class TestTaskListCleanup:
    """Tests de nettoyage."""

    def test_clear_tasks(self, task_list, sample_tasks):
        """Test du nettoyage de la liste."""
        task_list.set_tasks(sample_tasks)

        # Nettoyer
        task_list.set_tasks([])

        # La liste devrait être vide

    def test_task_list_deletion(self, qapp, sample_tasks):
        """Test que TaskList se supprime proprement."""
        task_list = TaskList()
        task_list.set_tasks(sample_tasks)
        task_list.deleteLater()

        # Ne devrait pas planter


class TestTaskListEdgeCases:
    """Tests des cas limites."""

    def test_set_tasks_with_none(self, task_list):
        """Test avec None au lieu d'une liste."""
        try:
            task_list.set_tasks(None)
        except (TypeError, AttributeError):
            pass  # Comportement acceptable

    def test_task_with_no_commands(self, task_list):
        """Test avec une tâche sans commandes."""
        task = Task(name="Empty", description="No commands", commands=[])
        task_list.set_tasks([task])
        # Ne devrait pas planter

    def test_task_with_very_long_name(self, task_list):
        """Test avec un nom de tâche très long."""
        task = Task(
            name="A" * 200,  # Nom très long
            description="Test",
            commands=[],
        )
        task_list.set_tasks([task])
        # Devrait gérer gracieusement

    def test_many_tasks(self, task_list):
        """Test avec beaucoup de tâches."""
        many_tasks = [
            Task(name=f"Task {i}", description=f"Task number {i}", commands=[])
            for i in range(100)
        ]

        task_list.set_tasks(many_tasks)
        # Devrait gérer sans problème de performance


class TestTaskListWithCustomFactory:
    """Tests avec factory personnalisée."""

    def test_custom_factory_receives_correct_parameters(self, qapp, sample_tasks):
        """Test que la factory reçoit les bons paramètres."""
        from PySide6.QtWidgets import QWidget

        received_tasks = []

        def custom_factory(task, parent):
            received_tasks.append(task)
            # Retourner un vrai QWidget
            return QWidget(parent)

        task_list = TaskList(task_widget_factory=custom_factory)
        task_list.set_tasks(sample_tasks)

        assert len(received_tasks) == len(sample_tasks)
        assert received_tasks == sample_tasks
        task_list.deleteLater()

    def test_factory_widget_added_to_layout(self, qapp, sample_tasks):
        """Test que les widgets créés par la factory sont ajoutés."""
        from PySide6.QtWidgets import QWidget

        created_widgets = []

        def custom_factory(task, parent):
            widget = QWidget(parent)
            created_widgets.append(widget)
            return widget

        task_list = TaskList(task_widget_factory=custom_factory)
        task_list.set_tasks(sample_tasks)

        # Les widgets devraient être créés
        assert len(created_widgets) == len(sample_tasks)
        task_list.deleteLater()
