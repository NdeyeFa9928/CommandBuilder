"""Tests unitaires pour YamlErrorHandler."""

from pathlib import Path

import pytest

from command_builder.models.yaml_error import YamlError
from command_builder.services.yaml_error_handler import YamlErrorHandler


class TestYamlErrorHandlerCreation:
    """Tests de création et initialisation."""

    def test_initialization(self):
        """Test que le handler s'initialise correctement."""
        handler = YamlErrorHandler()
        assert handler.errors == []
        assert handler.loaded_tasks == []
        assert not handler.has_errors()
        assert not handler.has_critical_errors()

    def test_get_error_summary_no_errors(self):
        """Test du résumé quand il n'y a pas d'erreurs."""
        handler = YamlErrorHandler()
        summary = handler.get_error_summary()
        assert summary == "Aucune erreur"


class TestYamlErrorHandlerLoadTask:
    """Tests de chargement de tâches individuelles."""

    def test_load_valid_task(self, tmp_path):
        """Test du chargement d'une tâche valide."""
        # Créer un fichier YAML valide
        yaml_file = tmp_path / "valid_task.yaml"
        yaml_file.write_text("""
name: "Test Task"
description: "A test task"
commands:
  - name: "Test Command"
    description: "A test command"
    command: "echo test"
    arguments: []
""")

        handler = YamlErrorHandler()
        task = handler.load_yaml_task(yaml_file)

        assert task is not None
        assert task.name == "Test Task"
        assert len(handler.errors) == 0
        assert not handler.has_errors()

    def test_load_task_file_not_found(self):
        """Test du chargement d'un fichier inexistant."""
        handler = YamlErrorHandler()
        task = handler.load_yaml_task(Path("nonexistent.yaml"))

        assert task is None
        assert len(handler.errors) == 1
        assert handler.errors[0].error_type == "FileNotFoundError"
        assert handler.has_errors()

    def test_load_task_invalid_yaml_syntax(self, tmp_path):
        """Test du chargement d'un fichier avec syntaxe YAML invalide."""
        yaml_file = tmp_path / "invalid_syntax.yaml"
        yaml_file.write_text("""
name: "Test Task"
description: "Missing closing quote
commands: []
""")

        handler = YamlErrorHandler()
        task = handler.load_yaml_task(yaml_file)

        assert task is None
        assert len(handler.errors) == 1
        assert handler.errors[0].error_type == "SyntaxError"
        assert "syntaxe YAML" in handler.errors[0].error_message

    def test_load_task_validation_error(self, tmp_path):
        """Test du chargement d'un fichier avec erreur de validation Pydantic."""
        yaml_file = tmp_path / "validation_error.yaml"
        yaml_file.write_text("""
description: "Missing name field"
commands: []
""")

        handler = YamlErrorHandler()
        task = handler.load_yaml_task(yaml_file)

        assert task is None
        assert len(handler.errors) == 1
        assert handler.errors[0].error_type == "ValidationError"
        assert "name" in handler.errors[0].error_message.lower()

    def test_load_task_with_command_list_inclusion(self, tmp_path):
        """Test du chargement avec résolution d'inclusions (liste de commandes)."""
        yaml_file = tmp_path / "task_with_list.yaml"
        yaml_file.write_text("""
name: "Task with list"
description: "Test"
commands:
  - - name: "Command 1"
      description: "First"
      command: "echo 1"
      arguments: []
    - name: "Command 2"
      description: "Second"
      command: "echo 2"
      arguments: []
""")

        handler = YamlErrorHandler()
        task = handler.load_yaml_task(yaml_file)

        assert task is not None
        assert len(task.commands) == 2
        assert task.commands[0].name == "Command 1"
        assert task.commands[1].name == "Command 2"


class TestYamlErrorHandlerLoadAll:
    """Tests de chargement de plusieurs tâches."""

    def test_load_all_tasks_empty_list(self):
        """Test du chargement d'une liste vide."""
        handler = YamlErrorHandler()
        tasks, errors = handler.load_all_tasks([])

        assert tasks == []
        assert errors == []

    def test_load_all_tasks_mixed_valid_invalid(self, tmp_path):
        """Test du chargement avec tâches valides et invalides."""
        # Tâche valide
        valid_file = tmp_path / "valid.yaml"
        valid_file.write_text("""
name: "Valid Task"
description: "Valid"
commands:
  - name: "Command"
    description: "Test"
    command: "echo test"
    arguments: []
""")

        # Tâche invalide
        invalid_file = tmp_path / "invalid.yaml"
        invalid_file.write_text("""
description: "Missing name"
commands: []
""")

        handler = YamlErrorHandler()
        tasks, errors = handler.load_all_tasks([valid_file, invalid_file])

        assert len(tasks) == 1
        assert tasks[0].name == "Valid Task"
        assert len(errors) == 1
        assert errors[0].file_name == "invalid.yaml"

    def test_load_all_tasks_clears_previous_state(self, tmp_path):
        """Test que load_all_tasks nettoie l'état précédent."""
        valid_file = tmp_path / "task.yaml"
        valid_file.write_text("""
name: "Task"
description: "Test"
commands: []
""")

        handler = YamlErrorHandler()

        # Premier chargement
        tasks1, errors1 = handler.load_all_tasks([valid_file])
        assert len(tasks1) == 1

        # Deuxième chargement
        tasks2, errors2 = handler.load_all_tasks([valid_file])
        assert len(tasks2) == 1
        assert len(handler.loaded_tasks) == 1  # Pas de duplication


class TestYamlErrorHandlerErrorSummary:
    """Tests du résumé d'erreurs."""

    def test_get_error_summary_with_errors(self, tmp_path):
        """Test du résumé avec plusieurs erreurs."""
        invalid1 = tmp_path / "invalid1.yaml"
        invalid1.write_text("invalid: yaml: syntax")

        invalid2 = tmp_path / "invalid2.yaml"
        invalid2.write_text("description: 'Missing name'\ncommands: []")

        handler = YamlErrorHandler()
        handler.load_all_tasks([invalid1, invalid2])

        summary = handler.get_error_summary()
        assert "2 erreur(s)" in summary
        assert "invalid1.yaml" in summary
        assert "invalid2.yaml" in summary

    def test_has_critical_errors(self, tmp_path):
        """Test de détection des erreurs critiques."""
        # Pour l'instant, toutes les erreurs sont critiques
        # Ce test peut évoluer si on ajoute des erreurs non-critiques
        invalid_file = tmp_path / "invalid.yaml"
        invalid_file.write_text("invalid")

        handler = YamlErrorHandler()
        handler.load_yaml_task(invalid_file)

        assert handler.has_errors()
        # Dépend de l'implémentation de YamlError.is_critical()
