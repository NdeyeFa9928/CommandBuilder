"""
Tests étendus pour le composant CommandForm.
Améliore la couverture de command_form.py
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from PySide6.QtWidgets import QApplication, QLabel, QMessageBox

from command_builder.components.command_form import CommandForm
from command_builder.models.arguments import Argument, TaskArgument, ArgumentValue
from command_builder.models.command import Command
from command_builder.models.task import Task


@pytest.fixture(scope="module")
def qapp():
    """Fixture pour créer une instance de QApplication."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def sample_command():
    """Fixture pour créer une commande de test."""
    return Command(
        name="TestCommand",
        description="A test command",
        command="echo {MESSAGE}",
        arguments=[
            Argument(
                code="MESSAGE",
                name="Message",
                description="Message to echo",
                type="string",
                required=1,
            )
        ],
    )


@pytest.fixture
def sample_task(sample_command):
    """Fixture pour créer une tâche de test."""
    return Task(
        name="TestTask",
        description="A test task",
        commands=[sample_command],
        arguments=[],
    )


@pytest.fixture
def task_with_shared_args():
    """Fixture pour créer une tâche avec arguments partagés."""
    cmd1 = Command(
        name="Command1",
        description="First command",
        command="cmd1 {INPUT}",
        arguments=[
            Argument(
                code="INPUT",
                name="Input File",
                type="file",
                required=1,
            )
        ],
    )
    cmd2 = Command(
        name="Command2",
        description="Second command",
        command="cmd2 {INPUT}",
        arguments=[
            Argument(
                code="INPUT",
                name="Input File",
                type="file",
                required=1,
            )
        ],
    )
    
    return Task(
        name="SharedTask",
        description="Task with shared arguments",
        commands=[cmd1, cmd2],
        arguments=[
            TaskArgument(
                code="SHARED_INPUT",
                name="Shared Input",
                type="file",
                required=1,
                values=[
                    ArgumentValue(command="Command1", argument="INPUT"),
                    ArgumentValue(command="Command2", argument="INPUT"),
                ],
            )
        ],
    )


class TestCommandFormInitialization:
    """Tests pour l'initialisation de CommandForm."""

    @patch.object(CommandForm, "_load_ui")
    @patch.object(CommandForm, "_load_stylesheet")
    def test_initialization_default_state(self, mock_style, mock_ui, qapp):
        """Teste l'état initial du formulaire."""
        form = CommandForm()
        
        assert form.current_command is None
        assert form.current_commands == []
        assert form.current_task is None
        assert form.command_components == []
        assert form.command_checkboxes == []
        assert form.task_argument_components == []
        assert form.shared_argument_values == {}

    @patch.object(CommandForm, "_load_ui")
    @patch.object(CommandForm, "_load_stylesheet")
    def test_initialization_with_custom_factory(self, mock_style, mock_ui, qapp):
        """Teste l'initialisation avec une factory personnalisée."""
        custom_factory = Mock()
        form = CommandForm(command_widget_factory=custom_factory)
        
        assert form._command_widget_factory is custom_factory


class TestCommandFormDefaultFactory:
    """Tests pour la factory par défaut."""

    @patch.object(CommandForm, "_load_ui")
    @patch.object(CommandForm, "_load_stylesheet")
    def test_default_factory_creates_command_component(
        self, mock_style, mock_ui, qapp, sample_command
    ):
        """Teste que la factory par défaut crée un CommandComponent."""
        form = CommandForm()
        
        # Appeler la factory par défaut
        with patch(
            "command_builder.components.command_form.command_form.CommandComponent"
        ) as mock_cc:
            mock_cc.return_value = Mock()
            widget = form._default_command_widget_factory(sample_command, form, True)
            
            mock_cc.assert_called_once_with(sample_command, form, True)


class TestCommandFormSetTask:
    """Tests pour la méthode set_task."""

    @patch.object(CommandForm, "_load_ui")
    @patch.object(CommandForm, "_load_stylesheet")
    def test_set_task_updates_current_task(
        self, mock_style, mock_ui, qapp, sample_task
    ):
        """Teste que set_task met à jour la tâche courante."""
        form = CommandForm()
        form.commands_layout = Mock()
        form.commands_layout.count.return_value = 0
        form._clear_form = Mock()
        form._restore_cached_values = Mock()
        form.task_loaded = Mock()
        
        form.set_task(sample_task)
        
        assert form.current_task is sample_task
        assert form.current_commands == sample_task.commands
        form._clear_form.assert_called_once()

    @patch.object(CommandForm, "_load_ui")
    @patch.object(CommandForm, "_load_stylesheet")
    def test_set_task_emits_task_loaded_signal(
        self, mock_style, mock_ui, qapp, sample_task
    ):
        """Teste que set_task émet le signal task_loaded."""
        form = CommandForm()
        form.commands_layout = Mock()
        form.commands_layout.count.return_value = 0
        form._clear_form = Mock()
        form._restore_cached_values = Mock()
        
        signal_spy = Mock()
        form.task_loaded.connect(signal_spy)
        
        form.set_task(sample_task)
        
        signal_spy.assert_called_once()

    @patch.object(CommandForm, "_load_ui")
    @patch.object(CommandForm, "_load_stylesheet")
    def test_set_task_with_empty_commands(self, mock_style, mock_ui, qapp):
        """Teste set_task avec une tâche sans commandes."""
        empty_task = Task(
            name="EmptyTask",
            description="Task without commands",
            commands=[],
            arguments=[],
        )
        
        form = CommandForm()
        form.commands_layout = Mock()
        form._clear_form = Mock()
        form._save_current_values = Mock()
        
        form.set_task(empty_task)
        
        assert form.current_task is empty_task
        assert form.current_commands == []


class TestCommandFormSetCommands:
    """Tests pour la méthode set_commands."""

    @patch.object(CommandForm, "_load_ui")
    @patch.object(CommandForm, "_load_stylesheet")
    def test_set_commands_updates_list(
        self, mock_style, mock_ui, qapp, sample_command
    ):
        """Teste que set_commands met à jour la liste des commandes."""
        form = CommandForm()
        form.commands_layout = Mock()
        form.commands_layout.count.return_value = 0
        form._clear_form = Mock()
        
        commands = [sample_command]
        form.set_commands(commands, "TestTask")
        
        assert form.current_commands == commands
        assert form.current_task is None

    @patch.object(CommandForm, "_load_ui")
    @patch.object(CommandForm, "_load_stylesheet")
    def test_set_commands_with_empty_list(self, mock_style, mock_ui, qapp):
        """Teste set_commands avec une liste vide."""
        form = CommandForm()
        form.commands_layout = Mock()
        form._clear_form = Mock()
        
        form.set_commands([], "EmptyTask")
        
        assert form.current_commands == []


class TestCommandFormClearForm:
    """Tests pour la méthode _clear_form."""

    @patch.object(CommandForm, "_load_ui")
    @patch.object(CommandForm, "_load_stylesheet")
    def test_clear_form_removes_all_widgets(self, mock_style, mock_ui, qapp):
        """Teste que _clear_form supprime tous les widgets."""
        form = CommandForm()
        
        # Créer un mock layout
        mock_layout = Mock()
        mock_layout.count.side_effect = [2, 1, 0]  # Simule 2 items puis 1 puis 0
        
        mock_widget = Mock()
        mock_item = Mock()
        mock_item.widget.return_value = mock_widget
        mock_item.layout.return_value = None
        mock_item.spacerItem.return_value = None
        mock_layout.takeAt.return_value = mock_item
        
        form.commands_layout = mock_layout
        form.command_components = [Mock()]
        form.command_checkboxes = [Mock()]
        form.task_argument_components = [Mock()]
        
        form._clear_form()
        
        assert form.command_components == []
        assert form.command_checkboxes == []
        assert form.task_argument_components == []


class TestCommandFormClearLayout:
    """Tests pour la méthode _clear_layout."""

    @patch.object(CommandForm, "_load_ui")
    @patch.object(CommandForm, "_load_stylesheet")
    def test_clear_layout_recursive(self, mock_style, mock_ui, qapp):
        """Teste le nettoyage récursif des layouts."""
        form = CommandForm()
        
        # Créer un mock layout avec un layout imbriqué
        inner_layout = Mock()
        inner_layout.count.side_effect = [1, 0]
        inner_widget = Mock()
        inner_item = Mock()
        inner_item.widget.return_value = inner_widget
        inner_item.layout.return_value = None
        inner_layout.takeAt.return_value = inner_item
        
        outer_layout = Mock()
        outer_layout.count.side_effect = [1, 0]
        outer_item = Mock()
        outer_item.widget.return_value = None
        outer_item.layout.return_value = inner_layout
        outer_layout.takeAt.return_value = outer_item
        
        form._clear_layout(outer_layout)
        
        inner_layout.deleteLater.assert_called_once()


class TestCommandFormGetFormValues:
    """Tests pour la méthode get_form_values."""

    @patch.object(CommandForm, "_load_ui")
    @patch.object(CommandForm, "_load_stylesheet")
    def test_get_form_values_empty(self, mock_style, mock_ui, qapp):
        """Teste get_form_values sans composants."""
        form = CommandForm()
        form.command_components = []
        
        values = form.get_form_values()
        
        assert values == {}

    @patch.object(CommandForm, "_load_ui")
    @patch.object(CommandForm, "_load_stylesheet")
    def test_get_form_values_with_components(self, mock_style, mock_ui, qapp):
        """Teste get_form_values avec des composants."""
        form = CommandForm()
        
        mock_component = Mock()
        mock_component.get_argument_values.return_value = {"ARG1": "value1"}
        form.command_components = [mock_component]
        
        values = form.get_form_values()
        
        assert values == {"ARG1": "value1"}

    @patch.object(CommandForm, "_load_ui")
    @patch.object(CommandForm, "_load_stylesheet")
    def test_get_form_values_without_method(self, mock_style, mock_ui, qapp):
        """Teste get_form_values avec un composant sans get_argument_values."""
        form = CommandForm()
        
        mock_component = Mock(spec=[])  # Pas de méthode get_argument_values
        form.command_components = [mock_component]
        
        values = form.get_form_values()
        
        assert values == {}


class TestCommandFormOnExecuteClicked:
    """Tests pour la méthode _on_execute_clicked."""

    @patch.object(CommandForm, "_load_ui")
    @patch.object(CommandForm, "_load_stylesheet")
    def test_on_execute_clicked_no_components(self, mock_style, mock_ui, qapp):
        """Teste _on_execute_clicked sans composants."""
        form = CommandForm()
        form.command_components = []
        
        # Ne doit pas lever d'exception
        form._on_execute_clicked()

    @patch.object(CommandForm, "_load_ui")
    @patch.object(CommandForm, "_load_stylesheet")
    @patch("command_builder.components.command_form.command_form.CommandValidator")
    def test_on_execute_clicked_validation_fails(
        self, mock_validator, mock_style, mock_ui, qapp
    ):
        """Teste _on_execute_clicked quand la validation échoue."""
        mock_validator.validate_commands.return_value = (
            False,
            ["Error 1", "Error 2"],
        )
        
        form = CommandForm()
        form.command_components = [Mock()]
        form.command_checkboxes = []
        form._show_validation_errors = Mock()
        
        form._on_execute_clicked()
        
        form._show_validation_errors.assert_called_once_with(["Error 1", "Error 2"])

    @patch.object(CommandForm, "_load_ui")
    @patch.object(CommandForm, "_load_stylesheet")
    @patch("command_builder.components.command_form.command_form.CommandValidator")
    @patch("command_builder.components.command_form.command_form.CommandBuilderService")
    def test_on_execute_clicked_no_commands_selected(
        self, mock_builder, mock_validator, mock_style, mock_ui, qapp
    ):
        """Teste _on_execute_clicked quand aucune commande n'est sélectionnée."""
        mock_validator.validate_commands.return_value = (True, [])
        mock_builder.build_commands_list.return_value = []
        
        form = CommandForm()
        form.command_components = [Mock()]
        form.command_checkboxes = []
        form._show_no_command_selected_error = Mock()
        
        form._on_execute_clicked()
        
        form._show_no_command_selected_error.assert_called_once()

    @patch.object(CommandForm, "_load_ui")
    @patch.object(CommandForm, "_load_stylesheet")
    @patch("command_builder.components.command_form.command_form.CommandValidator")
    @patch("command_builder.components.command_form.command_form.CommandBuilderService")
    def test_on_execute_clicked_success(
        self, mock_builder, mock_validator, mock_style, mock_ui, qapp
    ):
        """Teste _on_execute_clicked avec succès."""
        mock_validator.validate_commands.return_value = (True, [])
        mock_builder.build_commands_list.return_value = [
            {"name": "Cmd1", "command": "echo test"}
        ]
        
        form = CommandForm()
        form.command_components = [Mock()]
        form.command_checkboxes = []
        
        signal_spy = Mock()
        form.commands_to_execute.connect(signal_spy)
        
        form._on_execute_clicked()
        
        signal_spy.assert_called_once()


class TestCommandFormShowErrors:
    """Tests pour les méthodes d'affichage d'erreurs."""

    @patch.object(CommandForm, "_load_ui")
    @patch.object(CommandForm, "_load_stylesheet")
    @patch("command_builder.components.command_form.command_form.QMessageBox")
    def test_show_validation_errors(
        self, mock_msgbox_class, mock_style, mock_ui, qapp
    ):
        """Teste _show_validation_errors."""
        mock_msgbox = Mock()
        mock_msgbox_class.return_value = mock_msgbox
        mock_msgbox_class.Warning = QMessageBox.Warning
        
        form = CommandForm()
        form._stylesheet = ""
        
        form._show_validation_errors(["Error 1", "Error 2"])
        
        mock_msgbox.setIcon.assert_called_once()
        mock_msgbox.setWindowTitle.assert_called_once_with("Arguments manquants")
        mock_msgbox.exec.assert_called_once()

    @patch.object(CommandForm, "_load_ui")
    @patch.object(CommandForm, "_load_stylesheet")
    @patch("command_builder.components.command_form.command_form.QMessageBox")
    def test_show_no_command_selected_error(
        self, mock_msgbox_class, mock_style, mock_ui, qapp
    ):
        """Teste _show_no_command_selected_error."""
        mock_msgbox = Mock()
        mock_msgbox_class.return_value = mock_msgbox
        mock_msgbox_class.Warning = QMessageBox.Warning
        
        form = CommandForm()
        form._stylesheet = ""
        
        form._show_no_command_selected_error()
        
        mock_msgbox.setWindowTitle.assert_called_once_with("Aucune commande sélectionnée")
        mock_msgbox.exec.assert_called_once()


class TestCommandFormDefaultStyles:
    """Tests pour les méthodes de style par défaut."""

    @patch.object(CommandForm, "_load_ui")
    @patch.object(CommandForm, "_load_stylesheet")
    def test_apply_default_style(self, mock_style, mock_ui, qapp):
        """Teste _apply_default_style."""
        form = CommandForm()
        
        mock_label = Mock(spec=QLabel)
        mock_style_obj = Mock()
        mock_label.style.return_value = mock_style_obj
        
        form._apply_default_style(mock_label)
        
        mock_label.setProperty.assert_called_once_with("hasDefault", True)
        mock_style_obj.unpolish.assert_called_once_with(mock_label)
        mock_style_obj.polish.assert_called_once_with(mock_label)

    @patch.object(CommandForm, "_load_ui")
    @patch.object(CommandForm, "_load_stylesheet")
    def test_remove_default_style(self, mock_style, mock_ui, qapp):
        """Teste _remove_default_style."""
        form = CommandForm()
        
        mock_label = Mock(spec=QLabel)
        mock_style_obj = Mock()
        mock_label.style.return_value = mock_style_obj
        
        form._remove_default_style(mock_label)
        
        mock_label.setProperty.assert_called_once_with("hasDefault", False)
        mock_style_obj.unpolish.assert_called_once_with(mock_label)
        mock_style_obj.polish.assert_called_once_with(mock_label)


class TestCommandFormValueCache:
    """Tests pour le cache des valeurs."""

    @patch.object(CommandForm, "_load_ui")
    @patch.object(CommandForm, "_load_stylesheet")
    def test_save_current_values_no_task(self, mock_style, mock_ui, qapp):
        """Teste _save_current_values sans tâche courante."""
        form = CommandForm()
        form.current_task = None
        
        # Ne doit pas lever d'exception
        form._save_current_values()

    @patch.object(CommandForm, "_load_ui")
    @patch.object(CommandForm, "_load_stylesheet")
    def test_restore_cached_values_no_task(self, mock_style, mock_ui, qapp):
        """Teste _restore_cached_values sans tâche courante."""
        form = CommandForm()
        form.current_task = None
        
        # Ne doit pas lever d'exception
        form._restore_cached_values()

    @patch.object(CommandForm, "_load_ui")
    @patch.object(CommandForm, "_load_stylesheet")
    def test_restore_cached_values_no_cache(
        self, mock_style, mock_ui, qapp, sample_task
    ):
        """Teste _restore_cached_values sans cache pour la tâche."""
        form = CommandForm()
        form.current_task = sample_task
        form._values_cache = {}
        
        # Ne doit pas lever d'exception
        form._restore_cached_values()


class TestCommandFormRefreshCommandDisplays:
    """Tests pour la méthode _refresh_command_displays."""

    @patch.object(CommandForm, "_load_ui")
    @patch.object(CommandForm, "_load_stylesheet")
    def test_refresh_command_displays_no_task(self, mock_style, mock_ui, qapp):
        """Teste _refresh_command_displays sans tâche courante."""
        form = CommandForm()
        form.current_task = None
        
        # Ne doit pas lever d'exception
        form._refresh_command_displays()

    @patch.object(CommandForm, "_load_ui")
    @patch.object(CommandForm, "_load_stylesheet")
    def test_refresh_command_displays_no_shared_values(
        self, mock_style, mock_ui, qapp, sample_task
    ):
        """Teste _refresh_command_displays sans valeurs partagées."""
        form = CommandForm()
        form.current_task = sample_task
        form.shared_argument_values = {}
        
        # Ne doit pas lever d'exception
        form._refresh_command_displays()


class TestCommandFormOnSharedArgumentChanged:
    """Tests pour la méthode _on_shared_argument_changed."""

    @patch.object(CommandForm, "_load_ui")
    @patch.object(CommandForm, "_load_stylesheet")
    def test_on_shared_argument_changed_stores_value(
        self, mock_style, mock_ui, qapp, task_with_shared_args
    ):
        """Teste que _on_shared_argument_changed stocke la valeur."""
        form = CommandForm()
        form.current_task = task_with_shared_args
        form.task_argument_components = []
        form._refresh_command_displays = Mock()
        
        mock_label = Mock()
        
        form._on_shared_argument_changed("SHARED_INPUT", "test_value", mock_label)
        
        assert form.shared_argument_values["SHARED_INPUT"] == "test_value"
        form._refresh_command_displays.assert_called_once()
