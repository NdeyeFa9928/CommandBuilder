"""
Tests simples pour le chargeur YAML.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from command_builder.services.yaml_loader import load_yaml_with_includes


def test_load_simple_yaml():
    """Teste le chargement d'un fichier YAML simple."""
    temp_dir = Path(tempfile.mkdtemp())

    try:
        # Créer un fichier YAML simple
        yaml_content = """
name: "Test Simple"
description: "Fichier YAML de test"
version: 1.0
items:
  - item1
  - item2
"""
        yaml_file = temp_dir / "simple.yaml"
        yaml_file.write_text(yaml_content, encoding="utf-8")

        # Charger le fichier
        data = load_yaml_with_includes(str(yaml_file))

        # Vérifications
        assert data["name"] == "Test Simple"
        assert data["description"] == "Fichier YAML de test"
        assert data["version"] == 1.0
        assert len(data["items"]) == 2
        assert data["items"][0] == "item1"

    finally:
        shutil.rmtree(temp_dir)


def test_load_yaml_with_include():
    """Teste le chargement d'un fichier YAML avec inclusion."""
    temp_dir = Path(tempfile.mkdtemp())

    try:
        # Créer un fichier à inclure
        included_content = """
name: "Fichier inclus"
data: "Données incluses"
"""
        included_file = temp_dir / "included.yaml"
        included_file.write_text(included_content, encoding="utf-8")

        # Créer le fichier principal avec inclusion
        main_content = """
name: "Fichier principal"
included_data: !include included.yaml
other_data: "Autres données"
"""
        main_file = temp_dir / "main.yaml"
        main_file.write_text(main_content, encoding="utf-8")

        # Charger le fichier principal
        data = load_yaml_with_includes(str(main_file))

        # Vérifications
        assert data["name"] == "Fichier principal"
        assert data["other_data"] == "Autres données"
        assert data["included_data"]["name"] == "Fichier inclus"
        assert data["included_data"]["data"] == "Données incluses"

    finally:
        shutil.rmtree(temp_dir)


def test_load_yaml_file_not_found():
    """Teste le comportement quand un fichier n'existe pas."""
    with pytest.raises(FileNotFoundError):
        load_yaml_with_includes("fichier_inexistant.yaml")
