"""Fenêtre d'aide avec documentation complète YAML."""

import sys
from pathlib import Path

from PySide6 import QtUiTools
from PySide6.QtWidgets import QDialog


def get_help_docs_dir() -> Path:
    """Retourne le chemin vers le dossier docs/help.

    Fonctionne en mode développement et en mode bundlé (PyInstaller).
    """
    if getattr(sys, "frozen", False):
        # Mode bundlé (PyInstaller)
        if hasattr(sys, "_MEIPASS"):
            return Path(sys._MEIPASS) / "docs" / "help"
        else:
            return Path(sys.executable).parent / "docs" / "help"
    else:
        # Mode développement
        return Path(__file__).parent.parent.parent.parent / "docs" / "help"


class HelpWindow(QDialog):
    """Fenêtre d'aide affichant la documentation YAML complète."""

    # Chemin vers les fichiers HTML de documentation
    HELP_DOCS_DIR = get_help_docs_dir()

    def __init__(self, parent=None):
        """Initialise la fenêtre d'aide.

        Args:
            parent: Widget parent
        """
        super().__init__(parent)
        self._load_ui()
        self._load_stylesheet()
        self._connect_signals()
        self._populate_content()

    def _load_ui(self):
        """Charge l'interface depuis le fichier .ui."""
        from PySide6.QtWidgets import QPushButton, QTabWidget, QTextBrowser

        ui_file = Path(__file__).parent / "help_window.ui"
        loader = QtUiTools.QUiLoader()
        ui = loader.load(str(ui_file))

        # Copier les propriétés
        self.setWindowTitle(ui.windowTitle())
        self.resize(ui.size())

        # Récupérer le layout de l'UI chargée et l'appliquer à ce dialog
        ui_layout = ui.layout()
        self.setLayout(ui_layout)

        # Récupérer les widgets
        self.tab_widget = self.findChild(QTabWidget, "tabWidget")
        self.intro_text = self.findChild(QTextBrowser, "introText")
        self.structure_text = self.findChild(QTextBrowser, "structureText")
        self.arguments_text = self.findChild(QTextBrowser, "argumentsText")
        self.shared_text = self.findChild(QTextBrowser, "sharedText")
        self.examples_text = self.findChild(QTextBrowser, "examplesText")
        self.close_button = self.findChild(QPushButton, "closeButton")

    def _load_stylesheet(self):
        """Charge la feuille de style depuis le fichier .qss."""
        qss_file = Path(__file__).parent / "help_window.qss"
        if qss_file.exists():
            with open(qss_file, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def _connect_signals(self):
        """Connecte les signaux des widgets."""
        if self.close_button:
            self.close_button.clicked.connect(self.accept)

    def _populate_content(self):
        """Remplit le contenu de chaque onglet."""
        self._populate_intro()
        self._populate_structure()
        self._populate_arguments()
        self._populate_shared()
        self._populate_examples()

    def _load_html_file(self, filename: str) -> str:
        """Charge un fichier HTML depuis le dossier docs/help.

        Args:
            filename: Nom du fichier HTML (ex: 'intro.html')

        Returns:
            Contenu HTML du fichier ou chaîne vide si non trouvé
        """
        html_path = self.HELP_DOCS_DIR / filename
        if html_path.exists():
            with open(html_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def _populate_intro(self):
        """Remplit l'onglet Introduction."""
        content = self._load_html_file("intro.html")
        self.intro_text.setHtml(content)

    def _populate_structure(self):
        """Remplit l'onglet Structure."""
        content = self._load_html_file("structure.html")
        self.structure_text.setHtml(content)

    def _populate_arguments(self):
        """Remplit l'onglet Arguments."""
        content = self._load_html_file("arguments.html")
        self.arguments_text.setHtml(content)

    def _populate_shared(self):
        """Remplit l'onglet Arguments Partagés."""
        content = self._load_html_file("shared.html")
        self.shared_text.setHtml(content)

    def _populate_examples(self):
        """Remplit l'onglet Exemples Complets."""
        content = self._load_html_file("examples.html")
        self.examples_text.setHtml(content)
