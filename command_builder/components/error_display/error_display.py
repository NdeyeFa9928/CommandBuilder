"""Composant pour afficher les erreurs YAML."""

from pathlib import Path

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from command_builder.models.yaml_error import YamlError


class ErrorDisplay(QWidget):
    """Widget pour afficher une erreur YAML de manière lisible."""

    def __init__(self, error: YamlError, parent=None):
        """
        Initialise le widget d'affichage d'erreur.

        Args:
            error: L'erreur YAML à afficher
            parent: Widget parent
        """
        super().__init__(parent)
        self.error = error
        self._load_ui()
        self._load_stylesheet()
        self._populate_data()

    def _load_ui(self):
        """Charge le fichier UI."""
        current_dir = Path(__file__).parent
        ui_file = current_dir / "error_display.ui"

        loader = QUiLoader()
        ui = loader.load(str(ui_file))

        # Copier les widgets de l'UI chargée
        self.titleLabel = ui.findChild(QLabel, "titleLabel")
        self.fileLabel = ui.findChild(QLabel, "fileLabel")
        self.messageLabel = ui.findChild(QLabel, "messageLabel")
        self.suggestionLabel = ui.findChild(QLabel, "suggestionLabel")

        # Utiliser le layout de l'UI
        self.setLayout(ui.layout())

    def _load_stylesheet(self):
        """Charge le fichier QSS."""
        current_dir = Path(__file__).parent
        qss_file = current_dir / "error_display.qss"

        if qss_file.exists():
            with open(qss_file, "r", encoding="utf-8") as f:
                stylesheet = f.read()
                self.setStyleSheet(stylesheet)

    def _populate_data(self):
        """Remplit les labels avec les données de l'erreur."""
        # Titre
        title_text = f"❌ {self.error.error_type}"
        if self.error.line_number:
            title_text += f" (ligne {self.error.line_number})"
        self.titleLabel.setText(title_text)

        # Fichier
        self.fileLabel.setText(f"📄 Fichier: {self.error.file_name}")

        # Message
        self.messageLabel.setText(self.error.error_message)

        # Suggestion (si disponible)
        if self.error.suggestion:
            self.suggestionLabel.setText(f"💡 {self.error.suggestion}")
            self.suggestionLabel.setVisible(True)
        else:
            self.suggestionLabel.setVisible(False)


class ErrorsPanel(QWidget):
    """Panel pour afficher plusieurs erreurs YAML."""

    def __init__(self, errors: list, parent=None):
        """
        Initialise le panel d'erreurs.

        Args:
            errors: Liste des erreurs YamlError à afficher
            parent: Widget parent
        """
        super().__init__(parent)
        self.errors = errors
        self._setup_ui()
        self._load_stylesheet()

    def _setup_ui(self):
        """Configure l'interface utilisateur."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Titre du panel
        title_label = QLabel(f"⚠️ {len(self.errors)} erreur(s) détectée(s)")
        title_label.setObjectName("titleLabel")
        layout.addWidget(title_label)

        # Scroll area pour les erreurs
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("scrollArea")

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_layout.setSpacing(8)
        scroll_layout.setContentsMargins(8, 8, 8, 8)

        # Ajouter chaque erreur
        for error in self.errors:
            error_display = ErrorDisplay(error)
            scroll_layout.addWidget(error_display)

        scroll_layout.addStretch()
        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)

        layout.addWidget(scroll)
        self.setLayout(layout)

    def _load_stylesheet(self):
        """Charge le fichier QSS."""
        current_dir = Path(__file__).parent
        qss_file = current_dir / "error_display.qss"

        if qss_file.exists():
            with open(qss_file, "r", encoding="utf-8") as f:
                stylesheet = f.read()
                self.setStyleSheet(stylesheet)
