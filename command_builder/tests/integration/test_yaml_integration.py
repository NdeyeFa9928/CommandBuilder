"""
Tests d'intégration simples pour le système YAML.
"""
import pytest
import tempfile
import shutil
from pathlib import Path

from command_builder.services.yaml_pipeline_loader import load_yaml_pipeline
from command_builder.models.pipeline import Pipeline


def test_pipeline_with_task_inclusion():
    """Teste un pipeline complet avec inclusion de tâches."""
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # Créer la structure de répertoires
        tasks_dir = temp_dir / "tasks"
        tasks_dir.mkdir()
        pipelines_dir = temp_dir / "pipelines"
        pipelines_dir.mkdir()
        
        # Créer un fichier de tâche
        task_content = """
name: "Tâche incluse"
description: "Une tâche chargée depuis un fichier séparé"
commands:
  - name: "commande_incluse"
    description: "Commande de la tâche incluse"
    command: "echo 'Tâche incluse'"
    arguments: []
"""
        task_file = tasks_dir / "task_incluse.yaml"
        task_file.write_text(task_content, encoding="utf-8")
        
        # Créer un pipeline qui inclut la tâche
        pipeline_content = """
name: "Pipeline avec inclusion"
description: "Pipeline qui inclut une tâche externe"
tasks:
  - !include ../tasks/task_incluse.yaml
  - name: "Tâche directe"
    description: "Tâche définie directement dans le pipeline"
    commands:
      - name: "commande_directe"
        description: "Commande directe"
        command: "echo 'Tâche directe'"
        arguments: []
"""
        pipeline_file = pipelines_dir / "pipeline_inclusion.yaml"
        pipeline_file.write_text(pipeline_content, encoding="utf-8")
        
        # Charger le pipeline
        pipeline = load_yaml_pipeline(pipeline_file)
        
        # Vérifications
        assert isinstance(pipeline, Pipeline)
        assert pipeline.name == "Pipeline avec inclusion"
        assert len(pipeline.tasks) == 2
        
        # Vérifier la tâche incluse
        task_incluse = pipeline.tasks[0]
        assert task_incluse.name == "Tâche incluse"
        assert len(task_incluse.commands) == 1
        assert task_incluse.commands[0].name == "commande_incluse"
        
        # Vérifier la tâche directe
        task_directe = pipeline.tasks[1]
        assert task_directe.name == "Tâche directe"
        assert len(task_directe.commands) == 1
        assert task_directe.commands[0].name == "commande_directe"
        
    finally:
        shutil.rmtree(temp_dir)


def test_pipeline_with_nested_inclusions():
    """Teste un pipeline avec des inclusions imbriquées."""
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # Créer la structure de répertoires
        commands_dir = temp_dir / "commands"
        commands_dir.mkdir()
        tasks_dir = temp_dir / "tasks"
        tasks_dir.mkdir()
        pipelines_dir = temp_dir / "pipelines"
        pipelines_dir.mkdir()
        
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
        
        # Créer un pipeline qui inclut la tâche
        pipeline_content = """
name: "Pipeline avec inclusions imbriquées"
description: "Pipeline avec tâche qui inclut une commande"
tasks:
  - !include ../tasks/task_avec_commande.yaml
"""
        pipeline_file = pipelines_dir / "pipeline_imbrique.yaml"
        pipeline_file.write_text(pipeline_content, encoding="utf-8")
        
        # Charger le pipeline
        pipeline = load_yaml_pipeline(pipeline_file)
        
        # Vérifications
        assert isinstance(pipeline, Pipeline)
        assert pipeline.name == "Pipeline avec inclusions imbriquées"
        assert len(pipeline.tasks) == 1
        
        # Vérifier la tâche
        task = pipeline.tasks[0]
        assert task.name == "Tâche avec commande incluse"
        assert len(task.commands) == 1
        
        # Vérifier la commande incluse
        command = task.commands[0]
        assert command.name == "commande_imbriquee"
        assert command.command == "echo 'Commande imbriquée'"
        
    finally:
        shutil.rmtree(temp_dir)


def test_real_pipeline_structure():
    """Teste avec la structure réelle des pipelines du projet."""
    # Ce test utilise les vrais fichiers du projet s'ils existent
    from command_builder.services.yaml_pipeline_loader import get_yaml_pipelines_directory, list_yaml_pipeline_files
    
    pipelines_dir = get_yaml_pipelines_directory()
    
    if pipelines_dir.exists():
        pipeline_files = list_yaml_pipeline_files()
        
        if pipeline_files:
            # Prendre le premier pipeline disponible
            first_pipeline_file = pipeline_files[0]
            
            # Essayer de le charger
            pipeline = load_yaml_pipeline(first_pipeline_file)
            
            # Vérifications de base
            assert isinstance(pipeline, Pipeline)
            assert pipeline.name is not None
            assert isinstance(pipeline.tasks, list)
            
            # Si le pipeline a des tâches, vérifier leur structure
            if pipeline.tasks:
                first_task = pipeline.tasks[0]
                assert first_task.name is not None
                assert isinstance(first_task.commands, list)
        else:
            pytest.skip("Aucun fichier de pipeline trouvé dans le projet")
    else:
        pytest.skip("Répertoire des pipelines non trouvé")
