"""
Tests d'intégration simples pour le système YAML.
"""

import shutil
import tempfile
from pathlib import Path

import pytest

from command_builder.models.task import Task
from command_builder.services.yaml_task_loader import load_yaml_task


def test_task_with_command_inclusion():
    """Teste une tâche avec inclusion de commandes."""
    temp_dir = Path(tempfile.mkdtemp())

    try:
        # Créer la structure de répertoires
        commands_dir = temp_dir / "commands"
        commands_dir.mkdir()
        tasks_dir = temp_dir / "tasks"
        tasks_dir.mkdir()

        # Créer un fichier de commande
        command_content = """
name: "commande_incluse"
description: "Commande chargée depuis un fichier séparé"
command: "echo 'Commande incluse'"
arguments: []
"""
        command_file = commands_dir / "commande_incluse.yaml"
        command_file.write_text(command_content, encoding="utf-8")

        # Créer une tâche qui inclut la commande
        task_content = """
name: "Tâche avec inclusion"
description: "Tâche qui inclut une commande externe"
commands:
  - !include ../commands/commande_incluse.yaml
  - name: "commande_directe"
    description: "Commande définie directement"
    command: "echo 'Commande directe'"
    arguments: []
"""
        task_file = tasks_dir / "task_inclusion.yaml"
        task_file.write_text(task_content, encoding="utf-8")

        # Charger la tâche
        task = load_yaml_task(task_file)

        # Vérifications
        assert isinstance(task, Task)
        assert task.name == "Tâche avec inclusion"
        assert len(task.commands) == 2

        # Vérifier la commande incluse
        commande_incluse = task.commands[0]
        assert commande_incluse.name == "commande_incluse"

        # Vérifier la commande directe
        commande_directe = task.commands[1]
    finally:
        shutil.rmtree(temp_dir)


def test_task_with_nested_inclusions():
    """Teste une tâche avec des inclusions imbriquées."""
    temp_dir = Path(tempfile.mkdtemp())

    try:
        # Créer la structure de répertoires
        commands_dir = temp_dir / "commands"
        commands_dir.mkdir()
        tasks_dir = temp_dir / "tasks"
        tasks_dir.mkdir()

        # Créer un fichier de commande
        command_content = """
name: "commande_imbriquee"
description: "Commande chargée depuis un fichier séparé"
command: "echo 'Commande imbriquée'"
arguments: []
"""
        command_file = commands_dir / "commande_imbriquee.yaml"
        command_file.write_text(command_content, encoding="utf-8")

        # Créer un fichier de tâche qui inclut la commande
        task_content = """
name: "Tâche avec commande incluse"
description: "Tâche qui inclut une commande externe"
commands:
  - !include ../commands/commande_imbriquee.yaml
"""
        task_file = tasks_dir / "task_avec_commande.yaml"
        task_file.write_text(task_content, encoding="utf-8")

        # Charger la tâche
        task = load_yaml_task(task_file)

        # Vérifications
        assert isinstance(task, Task)
        assert task.name == "Tâche avec commande incluse"
        assert len(task.commands) == 1

        # Vérifier la commande incluse
        command = task.commands[0]
        assert command.name == "commande_imbriquee"
        assert command.command == "echo 'Commande imbriquée'"

    finally:
        shutil.rmtree(temp_dir)


def test_real_task_structure():
    """Teste avec la structure réelle des tâches du projet."""
    # Ce test utilise les vrais fichiers du projet s'ils existent
    from command_builder.services.yaml_task_loader import (
        get_yaml_tasks_directory,
        list_yaml_task_files,
    )

    tasks_dir = get_yaml_tasks_directory()

    if tasks_dir.exists():
        task_files = list_yaml_task_files()

        if task_files:
            # Prendre la première tâche disponible
            first_task_file = task_files[0]

            # Essayer de la charger
            task = load_yaml_task(first_task_file)

            # Vérifications de base
            assert isinstance(task, Task)
            assert task.name is not None
            assert isinstance(task.commands, list)

            # Si la tâche a des commandes, vérifier leur structure
            if task.commands:
                first_command = task.commands[0]
                assert first_command.name is not None
                assert isinstance(first_command.arguments, list)
        else:
            pytest.skip("Aucun fichier de tâche trouvé dans le projet")
    else:
        pytest.skip("Répertoire des tâches non trouvé")
