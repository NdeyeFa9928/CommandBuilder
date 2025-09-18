#!/usr/bin/env python3
"""
CommandBuilder - GUI Assistant for Windows CLI Commands
Entry point for the application.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from command_builder.app import CommandBuilderApp


def main():
    """Main entry point for CommandBuilder application."""
    app = CommandBuilderApp()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
