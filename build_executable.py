#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build script for CommandBuilder executable using PyInstaller.
Adapted for CommandBuilder project structure.
"""

import argparse
import os
import subprocess
import sys
from importlib import import_module
from pathlib import Path


def get_version() -> str:
    """Return CommandBuilder package version."""
    try:
        return import_module("command_builder").__version__
    except Exception:
        return "0.0.0"


def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.absolute()


def clean_dist_directory(dist_dir):
    """Clean the distribution directory."""
    if dist_dir.exists():
        for item in dist_dir.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                import shutil

                shutil.rmtree(item)
    else:
        dist_dir.mkdir(parents=True, exist_ok=True)


def collect_data_files(base_dir):
    """Collect all data files that need to be included in the executable."""
    data_files = []

    # Add UI files (.ui)
    for ui_file in base_dir.rglob("*.ui"):
        rel_path = ui_file.relative_to(base_dir)
        dest_dir = rel_path.parent
        data_files.append((str(rel_path), str(dest_dir)))

    # Add QSS style files (.qss)
    for qss_file in base_dir.rglob("*.qss"):
        rel_path = qss_file.relative_to(base_dir)
        dest_dir = rel_path.parent
        data_files.append((str(rel_path), str(dest_dir)))

    # Add whole tasks directory (allows user to drop new YAML files next to the exe)
    tasks_dir = base_dir / "command_builder" / "data" / "tasks"
    if tasks_dir.exists():
        rel_path = tasks_dir.relative_to(base_dir)
        # Destination inside the bundle: command_builder/data
        data_files.append((str(rel_path), "command_builder/data"))

    # Add JSON command files
    commands_dir = base_dir / "command_builder" / "data" / "commands"
    if commands_dir.exists():
        for json_file in commands_dir.rglob("*.json"):
            rel_path = json_file.relative_to(base_dir)
            dest_dir = rel_path.parent
            data_files.append((str(rel_path), str(dest_dir)))

    # Add asset files (icons, images)
    assets_dir = base_dir / "command_builder" / "assets"
    if assets_dir.exists():
        for asset_file in assets_dir.rglob("*"):
            if asset_file.is_file() and asset_file.suffix in [
                ".ico",
                ".png",
                ".jpg",
                ".jpeg",
                ".svg",
            ]:
                rel_path = asset_file.relative_to(base_dir)
                dest_dir = rel_path.parent
                data_files.append((str(rel_path), str(dest_dir)))

    # Add help documentation HTML files
    help_docs_dir = base_dir / "docs" / "help"
    if help_docs_dir.exists():
        for html_file in help_docs_dir.glob("*.html"):
            rel_path = html_file.relative_to(base_dir)
            dest_dir = rel_path.parent
            data_files.append((str(rel_path), str(dest_dir)))

    return data_files


def get_app_icon(base_dir):
    """Get the application icon path."""
    assets_dir = base_dir / "command_builder" / "assets"

    # Preferred icon files in order of preference
    icon_candidates = [
        assets_dir / "icone.png",  # Fichier d'icône existant
        assets_dir / "icon.png",
        assets_dir / "icon.ico",
        assets_dir / "app_icon.png",
        assets_dir / "app_icon.ico",
    ]

    for icon_path in icon_candidates:
        if icon_path.exists():
            return str(icon_path)

    return None


def get_pyinstaller_path():
    """Get the path to PyInstaller executable."""
    # Try pipenv first
    try:
        result = subprocess.run(
            ["pipenv", "run", "which", "pyinstaller"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Fallback to system PyInstaller
    try:
        result = subprocess.run(
            ["which", "pyinstaller"], capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "pyinstaller"  # Hope it's in PATH


def install_pyinstaller_if_needed():
    """Install PyInstaller if not available."""
    try:
        subprocess.run(
            ["pipenv", "run", "pyinstaller", "--version"],
            capture_output=True,
            check=True,
        )
        print("PyInstaller is already installed.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("PyInstaller not found. Installing PyInstaller...")
        try:
            subprocess.run(["pipenv", "install", "--dev", "pyinstaller"], check=True)
            print("PyInstaller installed successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error installing PyInstaller: {e}")
            return False


def copy_data_directory(base_dir, dist_dir):
    """Copy the data directory to dist/ so users can modify YAML files."""
    import shutil

    source_data = base_dir / "command_builder" / "data"
    dest_data = dist_dir / "data"

    if not source_data.exists():
        print(f"Warning: Source data directory not found: {source_data}")
        return

    # Remove existing data directory if present
    if dest_data.exists():
        shutil.rmtree(dest_data)

    # Copy the entire data directory
    shutil.copytree(source_data, dest_data)
    print(f"[OK] Data directory copied to: {dest_data}")

    # Count files copied
    task_files = (
        list((dest_data / "tasks").glob("*.yaml"))
        if (dest_data / "tasks").exists()
        else []
    )
    command_files = (
        list((dest_data / "commands").glob("*.yaml"))
        if (dest_data / "commands").exists()
        else []
    )

    print(f"  - {len(task_files)} task files")
    print(f"  - {len(command_files)} command files")

    # Copy README for end users
    readme_source = base_dir / "README_DISTRIBUTION.txt"
    if readme_source.exists():
        readme_dest = dist_dir / "README.txt"
        shutil.copy2(readme_source, readme_dest)
        print("[OK] README.txt copied")


def build_executable(dev_mode=False):
    """Build the executable using PyInstaller."""
    base_dir = get_project_root()
    dist_dir = base_dir / "dist"

    print("CommandBuilder - Building executable...")
    print(f"Project root: {base_dir}")

    # Clean distribution directory
    print("Cleaning distribution directory...")
    clean_dist_directory(dist_dir)

    # Install PyInstaller if needed
    if not install_pyinstaller_if_needed():
        return False

    # Collect data files
    print("Collecting data files...")
    data_files = collect_data_files(base_dir)

    # Get application icon
    app_icon = get_app_icon(base_dir)

    # Build PyInstaller command
    command = ["pipenv", "run", "pyinstaller"]

    exe_name = f"CommandBuilder_{get_version()}"

    # Basic options and PySide6 specifics
    command.extend(
        [
            "--onefile",
            f"--name={exe_name}",
            f"--distpath={dist_dir}",
            "--clean",
        ]
    )

    # Windowed mode (no console) unless in dev mode
    if not dev_mode:
        command.append("--windowed")

    # Add icon if available
    if app_icon:
        command.append(f"--icon={app_icon}")
        print(f"Using icon: {app_icon}")

    # Add data files
    for src, dest in data_files:
        if os.name == "nt":  # Windows
            command.append(f"--add-data={src};{dest}")
        else:  # Unix-like
            command.append(f"--add-data={src}:{dest}")

    # Add main script
    command.append("main.py")

    # Print build information
    print("\nBuilding executable with the following resources:")
    for src, dest in data_files:
        print(f"  {src} -> {dest}")

    print("\nExecuting command:")
    print(" ".join(command))

    # Execute PyInstaller
    try:
        print("\nExecuting PyInstaller...")
        result = subprocess.run(command, cwd=base_dir, capture_output=True, text=True)

        # Print output
        if result.stdout:
            print("\nOutput:")
            print(result.stdout)

        # Check for errors
        if result.returncode != 0:
            print("\nError building executable:")
            print(result.stderr)
            return False

        print("\nBuild completed successfully!")
        print(f"Executable is available in: {dist_dir}")

        # Copy data directory next to the executable
        print("\nCopying data directory...")
        copy_data_directory(base_dir, dist_dir)

        # List built files
        if dist_dir.exists():
            print("\nBuilt files:")
            for item in dist_dir.iterdir():
                print(f"  {item.name}")

        return True

    except Exception as e:
        print(f"\nAn error occurred while building the executable: {e}")
        return False


def main():
    """Main entry point for the build script."""
    parser = argparse.ArgumentParser(description="Build CommandBuilder executable")
    parser.add_argument(
        "--dev", action="store_true", help="Build in development mode (with console)"
    )

    args = parser.parse_args()

    success = build_executable(dev_mode=args.dev)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
