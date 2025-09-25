"""
Tests pour le service de chargement des pipelines.
"""
import json
import os
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from command_builder.services.pipeline_loader import (
    load_pipeline,
    get_pipelines_directory,
    list_pipeline_files,
    load_pipelines,
)
from command_builder.models.pipeline import Pipeline


def test_load_pipeline(sample_pipeline_file, sample_pipeline_json):
    """Teste le chargement d'un pipeline à partir d'un fichier."""
    # Charger le pipeline à partir du fichier temporaire
    pipeline = load_pipeline(sample_pipeline_file)
    
    # Vérifier que le pipeline est correctement chargé
    assert isinstance(pipeline, Pipeline)
    assert pipeline.name == sample_pipeline_json["name"]
    assert pipeline.description == sample_pipeline_json["description"]
    assert len(pipeline.tasks) == len(sample_pipeline_json["tasks"])


def test_get_pipelines_directory():
    """Teste la récupération du répertoire des pipelines."""
    with patch("command_builder.services.pipeline_loader.Path") as mock_path:
        # Configurer le mock pour retourner un chemin spécifique
        mock_path.return_value.absolute.return_value = Path("/fake/path")
        
        # Appeler la fonction
        result = get_pipelines_directory()
        
        # Vérifier que la fonction a appelé Path avec le bon argument
        mock_path.assert_called_once_with("command_builder/data/pipelines")
        
        # Vérifier que la fonction a retourné le résultat de Path().absolute()
        assert result == Path("/fake/path")


def test_list_pipeline_files():
    """Teste la liste des fichiers de pipeline."""
    with patch("command_builder.services.pipeline_loader.get_pipelines_directory") as mock_get_dir, \
         patch("pathlib.Path.glob") as mock_glob:
        # Configurer le mock pour retourner un répertoire spécifique
        mock_dir = Path("/fake/pipelines")
        mock_get_dir.return_value = mock_dir
        
        # Configurer le mock pour simuler la présence de fichiers JSON
        mock_files = [Path("/fake/pipelines/test1.json"), Path("/fake/pipelines/test2.json")]
        mock_glob.return_value = mock_files
        
        # Appeler la fonction
        result = list_pipeline_files()
        
        # Vérifier que la fonction a appelé get_pipelines_directory
        mock_get_dir.assert_called_once()
        
        # Vérifier que la fonction a retourné les fichiers attendus
        assert result == mock_files


def test_load_pipelines_success():
    """Teste le chargement de plusieurs pipelines avec succès."""
    with patch("command_builder.services.pipeline_loader.list_pipeline_files") as mock_list_files, \
         patch("command_builder.services.pipeline_loader.load_pipeline") as mock_load_pipeline, \
         patch("builtins.print") as mock_print:
        
        # Configurer les mocks
        mock_files = [Path("/fake/pipelines/test1.json"), Path("/fake/pipelines/test2.json")]
        mock_list_files.return_value = mock_files
        
        pipeline1 = Pipeline(name="Pipeline 1", description="Description 1", tasks=[])
        pipeline2 = Pipeline(name="Pipeline 2", description="Description 2", tasks=[])
        mock_load_pipeline.side_effect = [pipeline1, pipeline2]
        
        # Appeler la fonction
        result = load_pipelines()
        
        # Vérifier que la fonction a appelé list_pipeline_files
        mock_list_files.assert_called_once()
        
        # Vérifier que load_pipeline a été appelé pour chaque fichier
        assert mock_load_pipeline.call_count == 2
        mock_load_pipeline.assert_any_call(mock_files[0])
        mock_load_pipeline.assert_any_call(mock_files[1])
        
        # Vérifier que la fonction a retourné les pipelines attendus
        assert len(result) == 2
        assert result[0] == pipeline1
        assert result[1] == pipeline2
        
        # Vérifier que les noms des pipelines ont été affichés
        mock_print.assert_any_call(pipeline1.name)
        mock_print.assert_any_call(pipeline2.name)


def test_load_pipelines_empty():
    """Teste le chargement de pipelines quand aucun fichier n'est trouvé."""
    with patch("command_builder.services.pipeline_loader.list_pipeline_files") as mock_list_files, \
         patch("builtins.print") as mock_print:
        
        # Configurer le mock pour ne retourner aucun fichier
        mock_list_files.return_value = []
        
        # Appeler la fonction
        result = load_pipelines()
        
        # Vérifier que la fonction a appelé list_pipeline_files
        mock_list_files.assert_called_once()
        
        # Vérifier que la fonction a affiché le message d'erreur
        mock_print.assert_called_once_with("Aucun fichier pipeline trouvé")
        
        # Vérifier que la fonction a retourné une liste vide
        assert result == []


def test_load_pipelines_with_error():
    """Teste le chargement de pipelines avec une erreur sur l'un des fichiers."""
    with patch("command_builder.services.pipeline_loader.list_pipeline_files") as mock_list_files, \
         patch("command_builder.services.pipeline_loader.load_pipeline") as mock_load_pipeline, \
         patch("builtins.print") as mock_print:
        
        # Configurer les mocks
        mock_files = [Path("/fake/pipelines/test1.json"), Path("/fake/pipelines/test2.json")]
        mock_list_files.return_value = mock_files
        
        # Le premier pipeline se charge correctement, le second génère une erreur
        pipeline1 = Pipeline(name="Pipeline 1", description="Description 1", tasks=[])
        mock_load_pipeline.side_effect = [pipeline1, ValueError("Format JSON invalide")]
        
        # Appeler la fonction
        result = load_pipelines()
        
        # Vérifier que la fonction a appelé list_pipeline_files
        mock_list_files.assert_called_once()
        
        # Vérifier que load_pipeline a été appelé pour chaque fichier
        assert mock_load_pipeline.call_count == 2
        
        # Vérifier que la fonction a retourné uniquement le pipeline valide
        assert len(result) == 1
        assert result[0] == pipeline1
        
        # Vérifier que l'erreur a été affichée
        mock_print.assert_any_call(f"Erreur lors du chargement du pipeline {mock_files[1].name}: Format JSON invalide")
