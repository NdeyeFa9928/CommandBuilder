import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from command_builder.components.main_window import MainWindow
from command_builder.services.yaml_task_loader import load_yaml_tasks


def get_icon_path():
    """Retourne le chemin absolu vers l'icône de l'application."""
    # Chemin relatif depuis le point d'entrée de l'application
    icon_path = Path(__file__).parent / "command_builder" / "assets" / "icone.png"
    return str(icon_path.absolute())


def setup_application():
    """Configure l'application Qt."""
    app = QApplication(sys.argv)
    app.setApplicationName("CommandBuilder")
    
    # Définir l'icône de l'application
    icon_path = get_icon_path()
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)
    
    return app


if __name__ == "__main__":
    app = setup_application()
    tasks = load_yaml_tasks()
    main_window = MainWindow()
    main_window.set_tasks(tasks)
    main_window.show()
    sys.exit(app.exec())