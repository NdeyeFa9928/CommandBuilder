"""
Tests simples pour le chargeur de pipelines YAML.
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

from command_builder.services.yaml_pipeline_loader import (
    get_yaml_pipelines_directory,
    list_yaml_pipeline_files,
    load_yaml_pipeline,
    load_yaml_pipelines
)
from command_builder.models.pipeline import Pipeline


def test_get_yaml_pipelines_directory():
    """Teste la récupération du répertoire des pipelines."""
    pipelines_dir = get_yaml_pipelines_directory()
    
    # Vérifications de base
    assert pipelines_dir.name == "pipelines"
    assert pipelines_dir.parent.name == "data"
    assert pipelines_dir.is_absolute()


def test_list_yaml_pipeline_files():
    """Teste la liste des fichiers de pipeline avec des fichiers temporaires."""
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # Créer quelques fichiers YAML
        (temp_dir / "pipeline1.yaml").write_text("name: Pipeline 1", encoding="utf-8")
        (temp_dir / "pipeline2.yml").write_text("name: Pipeline 2", encoding="utf-8")
        (temp_dir / "not_yaml.txt").write_text("Not a YAML file", encoding="utf-8")
        
        # Mock la fonction pour utiliser notre répertoire temporaire
        with patch('command_builder.services.yaml_pipeline_loader.get_yaml_pipelines_directory', return_value=temp_dir):
            files = list_yaml_pipeline_files()
            
            # Vérifications
            assert len(files) == 2
            file_names = [f.name for f in files]
            assert "pipeline1.yaml" in file_names
            assert "pipeline2.yml" in file_names
            assert "not_yaml.txt" not in file_names
            
    finally:
        shutil.rmtree(temp_dir)


def test_load_yaml_pipeline_simple():
    """Teste le chargement d'un pipeline simple."""
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # Créer un fichier de pipeline simple
        pipeline_content = """
name: "Pipeline de test"
description: "Un pipeline simple pour les tests"
tasks:
  - name: "Tâche 1"
    description: "Première tâche"
    commands:
      - name: "commande1"
        description: "Première commande"
        command: "echo 'Hello'"
        arguments: []
"""
        pipeline_file = temp_dir / "test_pipeline.yaml"
        pipeline_file.write_text(pipeline_content, encoding="utf-8")
        
        # Charger le pipeline
        pipeline = load_yaml_pipeline(pipeline_file)
        
        # Vérifications
        assert isinstance(pipeline, Pipeline)
        assert pipeline.name == "Pipeline de test"
        assert pipeline.description == "Un pipeline simple pour les tests"
        assert len(pipeline.tasks) == 1
        assert pipeline.tasks[0].name == "Tâche 1"
        assert len(pipeline.tasks[0].commands) == 1
        assert pipeline.tasks[0].commands[0].name == "commande1"
        
    finally:
        shutil.rmtree(temp_dir)


def test_load_yaml_pipelines_with_mock():
    """Teste le chargement de plusieurs pipelines avec des mocks."""
    # Créer des pipelines de test
    pipeline1 = Pipeline(name="Pipeline 1", description="Premier pipeline", tasks=[])
    pipeline2 = Pipeline(name="Pipeline 2", description="Deuxième pipeline", tasks=[])
    
    # Mock les fonctions nécessaires
    with patch('command_builder.services.yaml_pipeline_loader.list_yaml_pipeline_files') as mock_list, \
         patch('command_builder.services.yaml_pipeline_loader.load_yaml_pipeline') as mock_load:
        
        # Configurer les mocks
        mock_list.return_value = [Path("pipeline1.yaml"), Path("pipeline2.yaml")]
        mock_load.side_effect = [pipeline1, pipeline2]
        
        # Appeler la fonction
        pipelines = load_yaml_pipelines()
        
        # Vérifications
        assert len(pipelines) == 2
        assert pipelines[0].name == "Pipeline 1"
        assert pipelines[1].name == "Pipeline 2"
        
        # Vérifier que les mocks ont été appelés
        mock_list.assert_called_once()
        assert mock_load.call_count == 2


def test_load_yaml_pipelines_with_error():
    """Teste le chargement de pipelines avec une erreur sur un fichier."""
    pipeline1 = Pipeline(name="Pipeline 1", description="Premier pipeline", tasks=[])
    
    with patch('command_builder.services.yaml_pipeline_loader.list_yaml_pipeline_files') as mock_list, \
         patch('command_builder.services.yaml_pipeline_loader.load_yaml_pipeline') as mock_load, \
         patch('builtins.print') as mock_print:
        
        # Configurer les mocks
        mock_list.return_value = [Path("pipeline1.yaml"), Path("pipeline2.yaml")]
        mock_load.side_effect = [pipeline1, ValueError("Erreur de format")]
        
        # Appeler la fonction
        pipelines = load_yaml_pipelines()
        
        # Vérifications
        assert len(pipelines) == 1  # Seul le premier pipeline a été chargé
        assert pipelines[0].name == "Pipeline 1"
        
        # Vérifier que l'erreur a été affichée
        mock_print.assert_called()
        print_args = mock_print.call_args[0][0]
        assert "Erreur lors du chargement" in print_args
