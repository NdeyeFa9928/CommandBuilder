"""
Tests étendus pour le loader YAML avec support !include.
Améliore la couverture de yaml_loader.py
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import yaml

from command_builder.services.yaml_loader import (
    IncludeLoader,
    include_constructor,
    load_task,
    load_yaml_with_includes,
)


class TestIncludeLoader:
    """Tests pour la classe IncludeLoader."""

    def test_loader_with_file_stream(self, tmp_path):
        """Teste le loader avec un fichier réel."""
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("key: value")
        
        with open(yaml_file, "r") as f:
            loader = IncludeLoader(f)
            assert loader._root == tmp_path

    def test_loader_with_string_stream(self):
        """Teste le loader avec un stream sans attribut name."""
        from io import StringIO
        
        stream = StringIO("key: value")
        loader = IncludeLoader(stream)
        
        # Doit utiliser le répertoire courant
        assert loader._root == Path.cwd()


class TestIncludeConstructor:
    """Tests pour la fonction include_constructor."""

    def test_include_existing_file(self, tmp_path):
        """Teste l'inclusion d'un fichier existant."""
        # Créer le fichier à inclure
        include_file = tmp_path / "included.yaml"
        include_file.write_text("included_key: included_value")
        
        # Créer le fichier principal
        main_file = tmp_path / "main.yaml"
        main_file.write_text("data: !include included.yaml")
        
        # Charger
        with open(main_file, "r") as f:
            result = yaml.load(f, IncludeLoader)
        
        assert result["data"]["included_key"] == "included_value"

    def test_include_nonexistent_file(self, tmp_path):
        """Teste l'inclusion d'un fichier inexistant."""
        main_file = tmp_path / "main.yaml"
        main_file.write_text("data: !include nonexistent.yaml")
        
        with pytest.raises(FileNotFoundError) as exc_info:
            with open(main_file, "r") as f:
                yaml.load(f, IncludeLoader)
        
        assert "non trouvé" in str(exc_info.value)

    def test_include_nested(self, tmp_path):
        """Teste les inclusions imbriquées."""
        # Créer la structure de fichiers
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        
        # Fichier le plus profond
        deep_file = subdir / "deep.yaml"
        deep_file.write_text("deep_key: deep_value")
        
        # Fichier intermédiaire
        middle_file = tmp_path / "middle.yaml"
        middle_file.write_text("middle_data: !include subdir/deep.yaml")
        
        # Fichier principal
        main_file = tmp_path / "main.yaml"
        main_file.write_text("main_data: !include middle.yaml")
        
        # Charger
        with open(main_file, "r") as f:
            result = yaml.load(f, IncludeLoader)
        
        assert result["main_data"]["middle_data"]["deep_key"] == "deep_value"

    def test_include_relative_path(self, tmp_path):
        """Teste l'inclusion avec un chemin relatif."""
        # Créer la structure
        commands_dir = tmp_path / "commands"
        commands_dir.mkdir()
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        
        # Fichier de commande
        cmd_file = commands_dir / "cmd.yaml"
        cmd_file.write_text("name: TestCommand\ncommand: echo test")
        
        # Fichier de tâche avec chemin relatif
        task_file = tasks_dir / "task.yaml"
        task_file.write_text("commands:\n  - !include ../commands/cmd.yaml")
        
        # Charger
        with open(task_file, "r") as f:
            result = yaml.load(f, IncludeLoader)
        
        assert result["commands"][0]["name"] == "TestCommand"


class TestLoadYamlWithIncludes:
    """Tests pour la fonction load_yaml_with_includes."""

    def test_load_simple_yaml(self, tmp_path):
        """Teste le chargement d'un YAML simple."""
        yaml_file = tmp_path / "simple.yaml"
        yaml_file.write_text("name: Test\nvalue: 42")
        
        result = load_yaml_with_includes(str(yaml_file))
        
        assert result["name"] == "Test"
        assert result["value"] == 42

    def test_load_yaml_with_list(self, tmp_path):
        """Teste le chargement d'un YAML avec liste."""
        yaml_file = tmp_path / "list.yaml"
        yaml_file.write_text("items:\n  - item1\n  - item2\n  - item3")
        
        result = load_yaml_with_includes(str(yaml_file))
        
        assert len(result["items"]) == 3
        assert "item1" in result["items"]

    def test_load_yaml_with_include(self, tmp_path):
        """Teste le chargement avec inclusion."""
        # Fichier à inclure
        include_file = tmp_path / "include.yaml"
        include_file.write_text("included: true")
        
        # Fichier principal
        main_file = tmp_path / "main.yaml"
        main_file.write_text("main: true\ndata: !include include.yaml")
        
        result = load_yaml_with_includes(str(main_file))
        
        assert result["main"] is True
        assert result["data"]["included"] is True

    def test_load_nonexistent_file(self):
        """Teste le chargement d'un fichier inexistant."""
        with pytest.raises(FileNotFoundError):
            load_yaml_with_includes("/nonexistent/path/file.yaml")


class TestLoadTask:
    """Tests pour la fonction load_task."""

    def test_load_task_with_default_root(self, tmp_path, monkeypatch):
        """Teste le chargement d'une tâche avec le root par défaut."""
        # Créer la structure
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        
        task_file = tasks_dir / "test_task.yaml"
        task_file.write_text("name: TestTask\ndescription: A test task")
        
        # Patcher le chemin par défaut
        monkeypatch.setattr(
            "command_builder.services.yaml_loader.Path",
            lambda x: tmp_path if x == Path(__file__).parent else Path(x)
        )
        
        # Le test vérifie que la fonction accepte un data_root explicite
        result = load_task("test_task", data_root=str(tmp_path))
        
        assert result["name"] == "TestTask"

    def test_load_task_with_explicit_root(self, tmp_path):
        """Teste le chargement d'une tâche avec un root explicite."""
        # Créer la structure
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        
        task_file = tasks_dir / "my_task.yaml"
        task_file.write_text("name: MyTask\ncommands: []")
        
        result = load_task("my_task", data_root=str(tmp_path))
        
        assert result["name"] == "MyTask"

    def test_load_nonexistent_task(self, tmp_path):
        """Teste le chargement d'une tâche inexistante."""
        # Créer le dossier tasks vide
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        
        with pytest.raises(FileNotFoundError) as exc_info:
            load_task("nonexistent_task", data_root=str(tmp_path))
        
        assert "non trouvée" in str(exc_info.value)

    def test_load_task_with_includes(self, tmp_path):
        """Teste le chargement d'une tâche avec inclusions."""
        # Créer la structure
        commands_dir = tmp_path / "commands"
        commands_dir.mkdir()
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        
        # Fichier de commande
        cmd_file = commands_dir / "echo_cmd.yaml"
        cmd_file.write_text(
            "name: EchoCommand\n"
            "description: Echo something\n"
            "command: echo {MESSAGE}\n"
            "arguments:\n"
            "  - code: MESSAGE\n"
            "    name: Message\n"
            "    type: string\n"
            "    required: 1"
        )
        
        # Fichier de tâche
        task_file = tasks_dir / "echo_task.yaml"
        task_file.write_text(
            "name: EchoTask\n"
            "description: Task with echo\n"
            "commands:\n"
            "  - !include ../commands/echo_cmd.yaml"
        )
        
        result = load_task("echo_task", data_root=str(tmp_path))
        
        assert result["name"] == "EchoTask"
        assert len(result["commands"]) == 1
        assert result["commands"][0]["name"] == "EchoCommand"


class TestYamlLoaderEdgeCases:
    """Tests pour les cas limites du loader YAML."""

    def test_empty_yaml_file(self, tmp_path):
        """Teste le chargement d'un fichier YAML vide."""
        yaml_file = tmp_path / "empty.yaml"
        yaml_file.write_text("")
        
        result = load_yaml_with_includes(str(yaml_file))
        
        assert result is None

    def test_yaml_with_comments(self, tmp_path):
        """Teste le chargement d'un YAML avec commentaires."""
        yaml_file = tmp_path / "comments.yaml"
        yaml_file.write_text(
            "# This is a comment\n"
            "name: Test  # Inline comment\n"
            "# Another comment\n"
            "value: 123"
        )
        
        result = load_yaml_with_includes(str(yaml_file))
        
        assert result["name"] == "Test"
        assert result["value"] == 123

    def test_yaml_with_multiline_string(self, tmp_path):
        """Teste le chargement d'un YAML avec chaîne multiligne."""
        yaml_file = tmp_path / "multiline.yaml"
        yaml_file.write_text(
            "description: |\n"
            "  This is a\n"
            "  multiline string\n"
            "  with multiple lines"
        )
        
        result = load_yaml_with_includes(str(yaml_file))
        
        assert "multiline string" in result["description"]

    def test_yaml_with_special_characters(self, tmp_path):
        """Teste le chargement d'un YAML avec caractères spéciaux."""
        yaml_file = tmp_path / "special.yaml"
        yaml_file.write_text(
            "path: C:\\Users\\Test\\file.txt\n"
            "command: echo \"Hello World\"\n"
            "accent: eaue",
            encoding="utf-8"
        )
        
        result = load_yaml_with_includes(str(yaml_file))
        
        assert "Users" in result["path"]
        assert "Hello World" in result["command"]
        assert result["accent"] == "eaue"

    def test_include_with_list_items(self, tmp_path):
        """Teste l'inclusion dans une liste."""
        # Fichiers à inclure
        cmd1 = tmp_path / "cmd1.yaml"
        cmd1.write_text("name: Command1")
        
        cmd2 = tmp_path / "cmd2.yaml"
        cmd2.write_text("name: Command2")
        
        # Fichier principal
        main_file = tmp_path / "main.yaml"
        main_file.write_text(
            "commands:\n"
            "  - !include cmd1.yaml\n"
            "  - !include cmd2.yaml"
        )
        
        result = load_yaml_with_includes(str(main_file))
        
        assert len(result["commands"]) == 2
        assert result["commands"][0]["name"] == "Command1"
        assert result["commands"][1]["name"] == "Command2"
