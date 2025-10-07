"""
Tests unitaires pour le composant ArgumentComponent.
"""

import pytest
from PySide6.QtWidgets import QApplication, QLineEdit, QPushButton
from unittest.mock import Mock, patch

from command_builder.models.arguments import Argument
from command_builder.components.argument_component import ArgumentComponent


@pytest.fixture(scope="module")
def qapp():
    """Fixture pour créer une instance de QApplication."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def sample_argument():
    """Fixture pour créer un argument de test."""
    return Argument(
        code="TEST_ARG",
        name="Test Argument",
        description="A test argument",
        type="string",
        required=True,
    )


@pytest.fixture
def optional_argument():
    """Fixture pour créer un argument optionnel."""
    return Argument(
        code="OPT_ARG",
        name="Optional Argument",
        description="An optional argument",
        type="string",
        required=False,
    )


class TestArgumentComponentInitialization:
    """Tests pour l'initialisation du composant ArgumentComponent."""

    @patch.object(ArgumentComponent, "_load_ui")
    @patch.object(ArgumentComponent, "_load_stylesheet")
    @patch.object(ArgumentComponent, "_setup_ui")
    def test_initialization_with_argument(
        self, mock_setup, mock_stylesheet, mock_ui, qapp, sample_argument
    ):
        """Test que le composant s'initialise correctement avec un argument."""
        component = ArgumentComponent(sample_argument)

        assert component.argument == sample_argument
        mock_ui.assert_called_once()
        mock_stylesheet.assert_called_once()
        mock_setup.assert_called_once()


class TestArgumentComponentGetValue:
    """Tests pour la méthode get_value()."""

    @patch.object(ArgumentComponent, "_load_ui")
    @patch.object(ArgumentComponent, "_load_stylesheet")
    @patch.object(ArgumentComponent, "_setup_ui")
    def test_get_value_returns_text(
        self, mock_setup, mock_stylesheet, mock_ui, qapp, sample_argument
    ):
        """Test que get_value retourne le texte du QLineEdit."""
        component = ArgumentComponent(sample_argument)
        component.line_edit = Mock(spec=QLineEdit)
        component.line_edit.text.return_value = "test_value"

        result = component.get_value()

        assert result == "test_value"
        component.line_edit.text.assert_called_once()

    @patch.object(ArgumentComponent, "_load_ui")
    @patch.object(ArgumentComponent, "_load_stylesheet")
    @patch.object(ArgumentComponent, "_setup_ui")
    def test_get_value_returns_empty_when_no_line_edit(
        self, mock_setup, mock_stylesheet, mock_ui, qapp, sample_argument
    ):
        """Test que get_value retourne une chaîne vide si line_edit n'existe pas."""
        component = ArgumentComponent(sample_argument)
        component.line_edit = None

        result = component.get_value()

        assert result == ""


class TestArgumentComponentSetValue:
    """Tests pour la méthode set_value()."""

    @patch.object(ArgumentComponent, "_load_ui")
    @patch.object(ArgumentComponent, "_load_stylesheet")
    @patch.object(ArgumentComponent, "_setup_ui")
    def test_set_value_updates_line_edit(
        self, mock_setup, mock_stylesheet, mock_ui, qapp, sample_argument
    ):
        """Test que set_value met à jour le texte du QLineEdit."""
        component = ArgumentComponent(sample_argument)
        component.line_edit = Mock(spec=QLineEdit)

        component.set_value("new_value")

        component.line_edit.setText.assert_called_once_with("new_value")

    @patch.object(ArgumentComponent, "_load_ui")
    @patch.object(ArgumentComponent, "_load_stylesheet")
    @patch.object(ArgumentComponent, "_setup_ui")
    def test_set_value_does_nothing_when_no_line_edit(
        self, mock_setup, mock_stylesheet, mock_ui, qapp, sample_argument
    ):
        """Test que set_value ne fait rien si line_edit n'existe pas."""
        component = ArgumentComponent(sample_argument)
        component.line_edit = None

        # Ne devrait pas lever d'exception
        component.set_value("new_value")


class TestArgumentComponentGetArgument:
    """Tests pour la méthode get_argument()."""

    @patch.object(ArgumentComponent, "_load_ui")
    @patch.object(ArgumentComponent, "_load_stylesheet")
    @patch.object(ArgumentComponent, "_setup_ui")
    def test_get_argument_returns_argument(
        self, mock_setup, mock_stylesheet, mock_ui, qapp, sample_argument
    ):
        """Test que get_argument retourne l'objet Argument."""
        component = ArgumentComponent(sample_argument)

        result = component.get_argument()

        assert result == sample_argument


class TestArgumentComponentBrowseButton:
    """Tests pour le bouton de parcours."""

    @patch.object(ArgumentComponent, "_load_ui")
    @patch.object(ArgumentComponent, "_load_stylesheet")
    @patch.object(ArgumentComponent, "_setup_ui")
    def test_enable_browse_button_shows_button(
        self, mock_setup, mock_stylesheet, mock_ui, qapp, sample_argument
    ):
        """Test que enable_browse_button affiche le bouton."""
        component = ArgumentComponent(sample_argument)
        component.browse_button = Mock(spec=QPushButton)

        component.enable_browse_button(True)

        component.browse_button.setVisible.assert_called_once_with(True)

    @patch.object(ArgumentComponent, "_load_ui")
    @patch.object(ArgumentComponent, "_load_stylesheet")
    @patch.object(ArgumentComponent, "_setup_ui")
    def test_enable_browse_button_hides_button(
        self, mock_setup, mock_stylesheet, mock_ui, qapp, sample_argument
    ):
        """Test que enable_browse_button masque le bouton."""
        component = ArgumentComponent(sample_argument)
        component.browse_button = Mock(spec=QPushButton)

        component.enable_browse_button(False)

        component.browse_button.setVisible.assert_called_once_with(False)

    @patch.object(ArgumentComponent, "_load_ui")
    @patch.object(ArgumentComponent, "_load_stylesheet")
    @patch.object(ArgumentComponent, "_setup_ui")
    def test_enable_browse_button_does_nothing_when_no_button(
        self, mock_setup, mock_stylesheet, mock_ui, qapp, sample_argument
    ):
        """Test que enable_browse_button ne fait rien si le bouton n'existe pas."""
        component = ArgumentComponent(sample_argument)
        component.browse_button = None

        # Ne devrait pas lever d'exception
        component.enable_browse_button(True)


class TestArgumentComponentSignals:
    """Tests pour les signaux émis par le composant."""

    @patch.object(ArgumentComponent, "_load_ui")
    @patch.object(ArgumentComponent, "_load_stylesheet")
    @patch.object(ArgumentComponent, "_setup_ui")
    def test_value_changed_signal_emitted(
        self, mock_setup, mock_stylesheet, mock_ui, qapp, sample_argument
    ):
        """Test que le signal value_changed est émis lors du changement de valeur."""
        component = ArgumentComponent(sample_argument)

        # Créer un mock pour capturer le signal
        signal_spy = Mock()
        component.value_changed.connect(signal_spy)

        # Simuler un changement de valeur
        component._on_value_changed("new_value")

        # Vérifier que le signal a été émis avec les bons arguments
        signal_spy.assert_called_once_with("TEST_ARG", "new_value")


class TestArgumentComponentBrowseDialog:
    """Tests pour la boîte de dialogue de parcours."""

    @patch.object(ArgumentComponent, "_load_ui")
    @patch.object(ArgumentComponent, "_load_stylesheet")
    @patch.object(ArgumentComponent, "_setup_ui")
    @patch(
        "command_builder.components.argument_component.argument_component.QFileDialog.getOpenFileName"
    )
    def test_browse_clicked_sets_file_path(
        self,
        mock_file_dialog,
        mock_setup,
        mock_stylesheet,
        mock_ui,
        qapp,
        sample_argument,
    ):
        """Test que _on_browse_clicked définit le chemin du fichier sélectionné."""
        component = ArgumentComponent(sample_argument)
        component.line_edit = Mock(spec=QLineEdit)

        # Simuler la sélection d'un fichier
        mock_file_dialog.return_value = ("C:/test/file.txt", "")

        component._on_browse_clicked()

        # Vérifier que le chemin a été défini
        component.line_edit.setText.assert_called_once_with("C:/test/file.txt")

    @patch.object(ArgumentComponent, "_load_ui")
    @patch.object(ArgumentComponent, "_load_stylesheet")
    @patch.object(ArgumentComponent, "_setup_ui")
    @patch(
        "command_builder.components.argument_component.argument_component.QFileDialog.getOpenFileName"
    )
    def test_browse_clicked_does_nothing_when_cancelled(
        self,
        mock_file_dialog,
        mock_setup,
        mock_stylesheet,
        mock_ui,
        qapp,
        sample_argument,
    ):
        """Test que _on_browse_clicked ne fait rien si l'utilisateur annule."""
        component = ArgumentComponent(sample_argument)
        component.line_edit = Mock(spec=QLineEdit)

        # Simuler l'annulation
        mock_file_dialog.return_value = ("", "")

        component._on_browse_clicked()

        # Vérifier que setText n'a pas été appelé
        component.line_edit.setText.assert_not_called()

    @patch.object(ArgumentComponent, "_load_ui")
    @patch.object(ArgumentComponent, "_load_stylesheet")
    @patch.object(ArgumentComponent, "_setup_ui")
    @patch(
        "command_builder.components.argument_component.argument_component.QFileDialog.getOpenFileName"
    )
    def test_browse_clicked_does_nothing_when_no_line_edit(
        self,
        mock_file_dialog,
        mock_setup,
        mock_stylesheet,
        mock_ui,
        qapp,
        sample_argument,
    ):
        """Test que _on_browse_clicked ne fait rien si line_edit n'existe pas."""
        component = ArgumentComponent(sample_argument)
        component.line_edit = None

        # Simuler la sélection d'un fichier
        mock_file_dialog.return_value = ("C:/test/file.txt", "")

        # Ne devrait pas lever d'exception
        component._on_browse_clicked()
