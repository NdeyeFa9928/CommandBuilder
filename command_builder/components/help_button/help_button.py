"""Composant bouton d'aide pour ouvrir la documentation YAML."""

from pathlib import Path

from PySide6 import QtUiTools
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QPushButton


class HelpButton(QPushButton):
    """Bouton pour ouvrir la fenêtre d'aide YAML."""

    help_clicked = Signal()

    def __init__(self, parent=None):
        """Initialise le bouton d'aide.

        Args:
            parent: Widget parent
        """
        super().__init__(parent)
        self._load_ui()
        self._load_stylesheet()
        self._connect_signals()

    def _load_ui(self):
        """Charge l'interface depuis le fichier .ui."""
        ui_file = Path(__file__).parent / "help_button.ui"
        loader = QtUiTools.QUiLoader()
        widget = loader.load(str(ui_file))

        # Copier les propriétés du widget chargé
        self.setText(widget.text())
        self.setToolTip(widget.toolTip())
        self.setCursor(widget.cursor())
        self.setMinimumSize(widget.minimumSize())

    def _load_stylesheet(self):
        """Charge la feuille de style depuis le fichier .qss."""
        qss_file = Path(__file__).parent / "help_button.qss"
        if qss_file.exists():
            with open(qss_file, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def _connect_signals(self):
        """Connecte les signaux internes."""
        self.clicked.connect(self.help_clicked.emit)
