"""Fenêtre d'aide avec documentation complète YAML.

La documentation est écrite en Markdown et convertie en HTML pour l'affichage.
"""

import sys
from pathlib import Path

import markdown
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


# CSS pour le rendu du Markdown en HTML
MARKDOWN_CSS = """
<style>
body {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
    line-height: 1.6;
    color: #333;
    padding: 10px;
}
h1 {
    color: #1565c0;
    font-size: 22px;
    border-bottom: 2px solid #1565c0;
    padding-bottom: 8px;
    margin-top: 0;
}
h2 {
    color: #2e7d32;
    font-size: 18px;
    margin-top: 25px;
    border-bottom: 1px solid #e0e0e0;
    padding-bottom: 5px;
}
h3 {
    color: #d84315;
    font-size: 15px;
    margin-top: 20px;
}
code {
    background-color: #f5f5f5;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 13px;
    color: #c62828;
}
pre {
    background-color: #f5f5f5;
    padding: 12px;
    border-radius: 6px;
    border-left: 4px solid #4caf50;
    overflow-x: auto;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    line-height: 1.4;
}
pre code {
    background-color: transparent;
    padding: 0;
    color: inherit;
}
blockquote {
    background-color: #e3f2fd;
    border-left: 4px solid #2196F3;
    margin: 15px 0;
    padding: 12px 15px;
    border-radius: 0 6px 6px 0;
}
blockquote p {
    margin: 5px 0;
}
table {
    border-collapse: collapse;
    width: 100%;
    margin: 15px 0;
}
th {
    background-color: #e3f2fd;
    padding: 10px;
    text-align: left;
    border: 1px solid #ddd;
    font-weight: bold;
}
td {
    padding: 8px 10px;
    border: 1px solid #ddd;
}
tr:nth-child(even) {
    background-color: #fafafa;
}
ul, ol {
    margin: 10px 0;
    padding-left: 25px;
}
li {
    margin: 5px 0;
}
hr {
    border: none;
    border-top: 2px solid #e0e0e0;
    margin: 20px 0;
}
strong {
    color: #1565c0;
}
em {
    color: #666;
}
</style>
"""


class HelpWindow(QDialog):
    """Fenêtre d'aide affichant la documentation YAML complète.

    La documentation est écrite en Markdown pour faciliter la maintenance
    et convertie en HTML pour l'affichage dans QTextBrowser.
    """

    # Chemin vers les fichiers Markdown de documentation
    HELP_DOCS_DIR = get_help_docs_dir()

    # Instance du convertisseur Markdown
    _md_converter = markdown.Markdown(
        extensions=["tables", "fenced_code", "nl2br"]
    )

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

    def _load_markdown_file(self, filename: str) -> str:
        """Charge un fichier Markdown et le convertit en HTML.

        Args:
            filename: Nom du fichier Markdown (ex: 'intro.md')

        Returns:
            Contenu HTML avec CSS intégré, ou chaîne vide si non trouvé
        """
        md_path = self.HELP_DOCS_DIR / filename
        if md_path.exists():
            with open(md_path, "r", encoding="utf-8") as f:
                md_content = f.read()

            # Reset le convertisseur pour éviter les problèmes de cache
            self._md_converter.reset()

            # Convertir le Markdown en HTML
            html_body = self._md_converter.convert(md_content)

            # Retourner le HTML complet avec le CSS
            return f"{MARKDOWN_CSS}<body>{html_body}</body>"
        return ""

    def _populate_intro(self):
        """Remplit l'onglet Introduction."""
        content = self._load_markdown_file("intro.md")
        self.intro_text.setHtml(content)

    def _populate_structure(self):
        """Remplit l'onglet Structure."""
        content = self._load_markdown_file("structure.md")
        self.structure_text.setHtml(content)

    def _populate_arguments(self):
        """Remplit l'onglet Arguments."""
        content = self._load_markdown_file("arguments.md")
        self.arguments_text.setHtml(content)

    def _populate_shared(self):
        """Remplit l'onglet Arguments Partagés."""
        content = self._load_markdown_file("shared.md")
        self.shared_text.setHtml(content)

    def _populate_examples(self):
        """Remplit l'onglet Exemples Complets."""
        content = self._load_markdown_file("examples.md")
        self.examples_text.setHtml(content)
