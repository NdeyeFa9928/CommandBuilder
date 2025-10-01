import sys
from PySide6.QtWidgets import QApplication
from command_builder.components.main_window import MainWindow
from command_builder.services.yaml_task_loader import load_yaml_tasks


def setup_application():
    """Configure l'application Qt."""
    app = QApplication(sys.argv)
    app.setApplicationName("CommandBuilder")
    return app


if __name__ == "__main__":
    app = setup_application()
    tasks = load_yaml_tasks()
    main_window = MainWindow()
    main_window.set_tasks(tasks)
    main_window.show()
    sys.exit(app.exec())
