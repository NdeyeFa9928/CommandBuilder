"""
Tests unitaires pour le composant CommandComponent.
"""

import pytest
from PySide6.QtWidgets import QApplication, QLabel
from unittest.mock import Mock, patch

from command_builder.models.command import Command
from command_builder.models.arguments import Argument
from command_builder.components.command_component import CommandComponent


@pytest.fixture(scope="module")
def qapp():
    """Fixture pour créer une instance de QApplication."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def sample_command_with_args():
    """Fixture pour créer une commande avec plusieurs arguments."""
    return Command(
        name="Test Command",
        description="A test command",
        command="myapp --input {INPUT_FILE} --output {OUTPUT_FILE} --mode {MODE}",
        arguments=[
            Argument(
                code="INPUT_FILE",
                name="Input File",
                description="The input file path",
                type="string",
                required=True,
            ),
            Argument(
                code="OUTPUT_FILE",
                name="Output File",
                description="The output file path",
                type="string",
                required=True,
            ),
            Argument(
                code="MODE",
                name="Mode",
                description="Processing mode",
                type="string",
                required=False,
            ),
        ],
    )


@pytest.fixture
def sample_command_no_args():
    """Fixture pour créer une commande sans arguments."""
    return Command(
        name="Simple Command",
        description="A simple command without arguments",
        command="myapp --version",
        arguments=[],
    )


class TestCommandComponentBuildFullCommand:
    """Tests pour la méthode _build_full_command()."""

    @patch.object(CommandComponent, "_load_ui")
    @patch.object(CommandComponent, "_load_stylesheet")
    @patch.object(CommandComponent, "_setup_ui")
    def test_build_full_command_no_arguments(
        self, mock_setup, mock_stylesheet, mock_ui, qapp, sample_command_no_args
    ):
        """Test que _build_full_command retourne la commande de base sans arguments."""
        component = CommandComponent(sample_command_no_args)

        result = component._build_full_command()

        assert result == "myapp --version"

    @patch.object(CommandComponent, "_load_ui")
    @patch.object(CommandComponent, "_load_stylesheet")
    @patch.object(CommandComponent, "_setup_ui")
    def test_build_full_command_with_empty_arguments(
        self, mock_setup, mock_stylesheet, mock_ui, qapp, sample_command_with_args
    ):
        """Test que _build_full_command affiche les placeholders quand les arguments sont vides."""
        component = CommandComponent(sample_command_with_args)
        component.argument_components = {}

        result = component._build_full_command()

        # Les placeholders doivent être remplacés par les noms des arguments
        assert "{Input File}" in result
        assert "{Output File}" in result
        assert "{Mode}" in result
        assert "myapp --input" in result

    @patch.object(CommandComponent, "_load_ui")
    @patch.object(CommandComponent, "_load_stylesheet")
    @patch.object(CommandComponent, "_setup_ui")
    def test_build_full_command_with_filled_arguments(
        self, mock_setup, mock_stylesheet, mock_ui, qapp, sample_command_with_args
    ):
        """Test que _build_full_command remplace correctement les placeholders avec les valeurs."""
        component = CommandComponent(sample_command_with_args)

        # Simuler des composants d'arguments avec des valeurs
        mock_input_component = Mock()
        mock_input_component.get_value.return_value = "input.txt"

        mock_output_component = Mock()
        mock_output_component.get_value.return_value = "output.txt"

        mock_mode_component = Mock()
        mock_mode_component.get_value.return_value = "fast"

        component.argument_components = {
            "INPUT_FILE": mock_input_component,
            "OUTPUT_FILE": mock_output_component,
            "MODE": mock_mode_component,
        }

        result = component._build_full_command()

        assert result == "myapp --input input.txt --output output.txt --mode fast"

    @patch.object(CommandComponent, "_load_ui")
    @patch.object(CommandComponent, "_load_stylesheet")
    @patch.object(CommandComponent, "_setup_ui")
    def test_build_full_command_with_partial_arguments(
        self, mock_setup, mock_stylesheet, mock_ui, qapp, sample_command_with_args
    ):
        """Test que _build_full_command gère correctement les arguments partiellement remplis."""
        component = CommandComponent(sample_command_with_args)

        # Simuler des composants d'arguments avec seulement certaines valeurs
        mock_input_component = Mock()
        mock_input_component.get_value.return_value = "input.txt"

        mock_output_component = Mock()
        mock_output_component.get_value.return_value = ""  # Vide

        mock_mode_component = Mock()
        mock_mode_component.get_value.return_value = "fast"

        component.argument_components = {
            "INPUT_FILE": mock_input_component,
            "OUTPUT_FILE": mock_output_component,
            "MODE": mock_mode_component,
        }

        result = component._build_full_command()

        assert "input.txt" in result
        assert "{Output File}" in result  # Placeholder pour l'argument vide
        assert "fast" in result


class TestCommandComponentUpdateCommandDisplay:
    """Tests pour la méthode _update_command_display()."""

    @patch.object(CommandComponent, "_load_ui")
    @patch.object(CommandComponent, "_load_stylesheet")
    @patch.object(CommandComponent, "_setup_ui")
    def test_update_command_display_no_label(
        self, mock_setup, mock_stylesheet, mock_ui, qapp, sample_command_no_args
    ):
        """Test que _update_command_display ne fait rien si le label n'existe pas."""
        component = CommandComponent(sample_command_no_args)
        component.label_command_cli = None

        # Ne devrait pas lever d'exception
        component._update_command_display()

    @patch.object(CommandComponent, "_load_ui")
    @patch.object(CommandComponent, "_load_stylesheet")
    @patch.object(CommandComponent, "_setup_ui")
    def test_update_command_display_simple_mode(
        self, mock_setup, mock_stylesheet, mock_ui, qapp, sample_command_no_args
    ):
        """Test que _update_command_display affiche correctement en mode simple."""
        component = CommandComponent(sample_command_no_args, simple_mode=True)
        component.label_command_cli = Mock(spec=QLabel)

        component._update_command_display()

        # En mode simple, le texte ne doit pas avoir le préfixe "Commande: "
        component.label_command_cli.setText.assert_called_once()
        call_args = component.label_command_cli.setText.call_args[0][0]
        assert not call_args.startswith("Commande: ")
        assert "myapp --version" in call_args

    @patch.object(CommandComponent, "_load_ui")
    @patch.object(CommandComponent, "_load_stylesheet")
    @patch.object(CommandComponent, "_setup_ui")
    def test_update_command_display_full_mode(
        self, mock_setup, mock_stylesheet, mock_ui, qapp, sample_command_no_args
    ):
        """Test que _update_command_display affiche correctement en mode complet."""
        component = CommandComponent(sample_command_no_args, simple_mode=False)
        component.label_command_cli = Mock(spec=QLabel)

        component._update_command_display()

        # En mode complet, le texte doit avoir le préfixe "Commande: "
        component.label_command_cli.setText.assert_called_once()
        call_args = component.label_command_cli.setText.call_args[0][0]
        assert call_args.startswith("Commande: ")
        assert "myapp --version" in call_args


class TestCommandComponentIntegration:
    """Tests d'intégration pour le remplacement des placeholders."""

    @patch.object(CommandComponent, "_load_ui")
    @patch.object(CommandComponent, "_load_stylesheet")
    @patch.object(CommandComponent, "_setup_ui")
    def test_argument_change_updates_display(
        self, mock_setup, mock_stylesheet, mock_ui, qapp, sample_command_with_args
    ):
        """Test que le changement d'un argument met à jour l'affichage de la commande."""
        component = CommandComponent(sample_command_with_args)
        component.label_command_cli = Mock(spec=QLabel)

        # Simuler des composants d'arguments
        mock_input_component = Mock()
        mock_input_component.get_value.return_value = "test.txt"

        component.argument_components = {"INPUT_FILE": mock_input_component}

        # Appeler _on_argument_changed pour simuler un changement
        component._on_argument_changed("INPUT_FILE", "test.txt")

        # Vérifier que setText a été appelé
        assert component.label_command_cli.setText.called

    @patch.object(CommandComponent, "_load_ui")
    @patch.object(CommandComponent, "_load_stylesheet")
    @patch.object(CommandComponent, "_setup_ui")
    def test_clear_arguments_resets_display(
        self, mock_setup, mock_stylesheet, mock_ui, qapp, sample_command_with_args
    ):
        """Test que clear_arguments réinitialise l'affichage avec des placeholders."""
        component = CommandComponent(sample_command_with_args)
        component.label_command_cli = Mock(spec=QLabel)

        # Simuler des composants d'arguments avec des valeurs
        mock_input_component = Mock()
        mock_input_component.get_value.return_value = "test.txt"
        mock_input_component.set_value = Mock()

        component.argument_components = {"INPUT_FILE": mock_input_component}

        # Effacer les arguments
        component.clear_arguments()

        # Vérifier que set_value("") a été appelé
        mock_input_component.set_value.assert_called_once_with("")

    @patch.object(CommandComponent, "_load_ui")
    @patch.object(CommandComponent, "_load_stylesheet")
    @patch.object(CommandComponent, "_setup_ui")
    def test_get_argument_values_returns_all_values(
        self, mock_setup, mock_stylesheet, mock_ui, qapp, sample_command_with_args
    ):
        """Test que get_argument_values retourne toutes les valeurs des arguments."""
        component = CommandComponent(sample_command_with_args)

        # Simuler des composants d'arguments
        mock_input_component = Mock()
        mock_input_component.get_value.return_value = "input.txt"

        mock_output_component = Mock()
        mock_output_component.get_value.return_value = "output.txt"

        component.argument_components = {
            "INPUT_FILE": mock_input_component,
            "OUTPUT_FILE": mock_output_component,
        }

        result = component.get_argument_values()

        assert result == {"INPUT_FILE": "input.txt", "OUTPUT_FILE": "output.txt"}

    @patch.object(CommandComponent, "_load_ui")
    @patch.object(CommandComponent, "_load_stylesheet")
    @patch.object(CommandComponent, "_setup_ui")
    def test_set_argument_value_updates_component(
        self, mock_setup, mock_stylesheet, mock_ui, qapp, sample_command_with_args
    ):
        """Test que set_argument_value met à jour le composant d'argument."""
        component = CommandComponent(sample_command_with_args)

        # Simuler un composant d'argument
        mock_input_component = Mock()
        mock_input_component.set_value = Mock()

        component.argument_components = {"INPUT_FILE": mock_input_component}

        # Définir une valeur
        component.set_argument_value("INPUT_FILE", "new_value.txt")

        # Vérifier que set_value a été appelé
        mock_input_component.set_value.assert_called_once_with("new_value.txt")
