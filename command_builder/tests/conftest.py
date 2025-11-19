"""
Fixtures partagées pour les tests de CommandBuilder.
"""

import json

import pytest


@pytest.fixture
def sample_command_json():
    """Fixture qui fournit un exemple de JSON de commande."""
    return {
        "name": "commande_test",
        "description": "Commande de test",
        "command": "echo {PARAM1}",
        "arguments": [
            {
                "code": "PARAM1",
                "name": "Paramètre 1",
                "description": "Description du paramètre",
                "type": "string",
                "required": 1,
            }
        ],
    }


@pytest.fixture
def sample_task_json(sample_command_json):
    """Fixture qui fournit un exemple de JSON de tâche."""
    return {
        "name": "Tâche de test",
        "description": "Description de la tâche de test",
        "commands": [sample_command_json],
    }


@pytest.fixture
def sample_pipeline_json(sample_task_json):
    """Fixture qui fournit un exemple de JSON de pipeline."""
    return {
        "name": "Test Pipeline",
        "description": "Pipeline de test",
        "tasks": [sample_task_json],
    }


@pytest.fixture
def sample_pipeline_file(tmp_path, sample_pipeline_json):
    """Fixture qui crée un fichier de pipeline temporaire."""
    pipeline_file = tmp_path / "test_pipeline.json"
    with open(pipeline_file, "w", encoding="utf-8") as f:
        json.dump(sample_pipeline_json, f)
    return pipeline_file
