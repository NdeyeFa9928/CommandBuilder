"""
Tests simples pour le chargeur de tâches YAML.
"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

from command_builder.models.task import Task
from command_builder.services.yaml_task_loader import (
    get_yaml_tasks_directory,
    list_yaml_task_files,
    load_yaml_task,
    load_yaml_tasks,
)


def test_get_yaml_tasks_directory():
    """Teste la récupération du répertoire des tâches."""
    tasks_dir = get_yaml_tasks_directory()

    # Vérifications de base
    assert tasks_dir.name == "tasks"
    assert tasks_dir.parent.name == "data"
    assert tasks_dir.is_absolute()


def test_list_yaml_task_files():
    """Teste la liste des fichiers de tâche avec des fichiers temporaires."""
    temp_dir = Path(tempfile.mkdtemp())

    try:
        # Créer quelques fichiers YAML
        (temp_dir / "task1.yaml").write_text("name: Task 1", encoding="utf-8")
        (temp_dir / "task2.yml").write_text("name: Task 2", encoding="utf-8")
        (temp_dir / "not_yaml.txt").write_text("Not a YAML file", encoding="utf-8")

        # Mock la fonction pour utiliser notre répertoire temporaire
        with patch(
            "command_builder.services.yaml_task_loader.get_yaml_tasks_directory",
            return_value=temp_dir,
        ):
            files = list_yaml_task_files()

            # Vérifications
            assert len(files) == 2
            file_names = [f.name for f in files]
            assert "task1.yaml" in file_names
            assert "task2.yml" in file_names
            assert "not_yaml.txt" not in file_names

    finally:
        shutil.rmtree(temp_dir)


def test_load_yaml_task_simple():
    """Teste le chargement d'une tâche simple."""
    temp_dir = Path(tempfile.mkdtemp())

    try:
        # Créer un fichier de tâche simple
        task_content = """
name: "Tâche de test"
description: "Une tâche simple pour les tests"
commands:
  - name: "commande1"
    description: "Première commande"
    command: "echo 'Hello'"
    arguments: []
"""
        task_file = temp_dir / "test_task.yaml"
        task_file.write_text(task_content, encoding="utf-8")

        # Charger la tâche
        task = load_yaml_task(task_file)

        # Vérifications
        assert isinstance(task, Task)
        assert task.name == "Tâche de test"
        assert task.description == "Une tâche simple pour les tests"
        assert len(task.commands) == 1
        assert task.commands[0].name == "commande1"

    finally:
        shutil.rmtree(temp_dir)


def test_load_yaml_tasks_with_mock():
    """Teste le chargement de plusieurs tâches avec des mocks."""
    # Créer des tâches de test
    task1 = Task(name="Tâche 1", description="Première tâche", commands=[])
    task2 = Task(name="Tâche 2", description="Deuxième tâche", commands=[])

    # Mock les fonctions nécessaires
    with (
        patch(
            "command_builder.services.yaml_task_loader.list_yaml_task_files"
        ) as mock_list,
        patch(
            "command_builder.services.yaml_error_handler.YamlErrorHandler.load_yaml_task"
        ) as mock_load,
    ):
        # Configurer les mocks
        mock_list.return_value = [Path("task1.yaml"), Path("task2.yaml")]
        mock_load.side_effect = [task1, task2]

        # Appeler la fonction - retourne maintenant (tasks, errors)
        tasks, errors = load_yaml_tasks()

        # Vérifications
        assert len(tasks) == 2
        assert tasks[0].name == "Tâche 1"
        assert tasks[1].name == "Tâche 2"
        assert len(errors) == 0

        # Vérifier que les mocks ont été appelés
        mock_list.assert_called_once()
        assert mock_load.call_count == 2


def test_load_yaml_tasks_with_error():
    """Teste le chargement de tâches avec une erreur sur un fichier."""
    task1 = Task(name="Tâche 1", description="Première tâche", commands=[])

    with (
        patch(
            "command_builder.services.yaml_task_loader.list_yaml_task_files"
        ) as mock_list,
        patch(
            "command_builder.services.yaml_error_handler.YamlErrorHandler.load_yaml_task"
        ) as mock_load,
    ):
        # Configurer les mocks - première tâche OK, deuxième retourne None (erreur)
        mock_list.return_value = [Path("task1.yaml"), Path("task2.yaml")]
        mock_load.side_effect = [task1, None]

        # Appeler la fonction - retourne maintenant (tasks, errors)
        tasks, errors = load_yaml_tasks()

        # Vérifications
        assert len(tasks) == 1  # Seule la première tâche a été chargée
        assert tasks[0].name == "Tâche 1"
        # Les erreurs sont gérées par YamlErrorHandler, pas par des exceptions
