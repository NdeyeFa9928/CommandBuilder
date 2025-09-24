import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QFile, QTextStream

from command_builder.components.main_window import MainWindow
from command_builder.services.pipeline_loader import load_pipelines


def setup_application():
    """Configure l'application Qt."""
    app = QApplication(sys.argv)
    app.setApplicationName("CommandBuilder")
    app.setOrganizationName("TN-SIC")
    
    # Appliquer un style global
    global_style = """
    QWidget {
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    """
    app.setStyleSheet(global_style)
    
    return app


if __name__ == "__main__":
    app = setup_application()
    pipelines = load_pipelines()
    main_window = MainWindow()
    main_window.set_pipelines(pipelines)
    main_window.show()
    sys.exit(app.exec())