"""
Tests pour la génération de commandes avec options.
"""

import pytest
from PySide6.QtWidgets import QApplication

from command_builder.components.command_component import CommandComponent
from command_builder.models.arguments import Argument
from command_builder.models.command import Command


@pytest.fixture(scope="module")
def qapp():
    """Fixture pour créer une application Qt."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_build_command_with_flag_checked(qapp):
    """Test la génération de commande avec un flag coché."""
    command = Command(
        name="test",
        description="Test",
        command="mycommand {INPUT} {DEBUG} {VERBOSE}",
        arguments=[
            Argument(code="INPUT", name="Input", type="file", required=1),
            Argument(code="DEBUG", name="Debug", type="flag", required=0, value="--debug"),
            Argument(code="VERBOSE", name="Verbose", type="flag", required=0, value="--verbose"),
        ]
    )
    
    component = CommandComponent(command, simple_mode=False)
    
    # Remplir l'input
    component.argument_components["INPUT"]["component"].set_value("input.txt")
    
    # Cocher debug
    component.argument_components["DEBUG"]["component"].checkbox.setChecked(True)
    
    # Ne pas cocher verbose
    
    full_command = component._build_full_command()
    # DEBUG coché retourne "--debug", VERBOSE non coché est supprimé
    assert full_command == "mycommand input.txt --debug"


def test_build_command_with_flag_unchecked(qapp):
    """Test la génération de commande avec un flag non coché."""
    command = Command(
        name="test",
        description="Test",
        command="mycommand {INPUT} {VERBOSE}",
        arguments=[
            Argument(code="INPUT", name="Input", type="file", required=1),
            Argument(code="VERBOSE", name="Verbose", type="flag", required=0, value="--verbose"),
        ]
    )
    
    component = CommandComponent(command, simple_mode=False)
    
    # Remplir l'input
    component.argument_components["INPUT"]["component"].set_value("input.txt")
    
    # Ne pas cocher verbose (par défaut)
    
    full_command = component._build_full_command()
    # Le placeholder {VERBOSE} doit être supprimé
    assert full_command == "mycommand input.txt"


def test_build_command_with_option_checked_and_filled(qapp):
    """Test la génération avec une option cochée et remplie."""
    command = Command(
        name="test",
        description="Test",
        command="mycommand {INPUT} --log-level {LOG_LEVEL}",
        arguments=[
            Argument(code="INPUT", name="Input", type="file", required=1),
            Argument(code="LOG_LEVEL", name="Log Level", type="valued_option", required=0),
        ]
    )
    
    component = CommandComponent(command, simple_mode=False)
    
    # Remplir l'input
    component.argument_components["INPUT"]["component"].set_value("input.txt")
    
    # Cocher et remplir log level
    component.argument_components["LOG_LEVEL"]["component"].checkbox.setChecked(True)
    component.argument_components["LOG_LEVEL"]["component"].line_edit.setText("INFO")
    
    full_command = component._build_full_command()
    assert full_command == "mycommand input.txt --log-level INFO"


def test_build_command_with_option_unchecked(qapp):
    """Test la génération avec une option non cochée."""
    command = Command(
        name="test",
        description="Test",
        command="mycommand {INPUT} {LOG_LEVEL}",
        arguments=[
            Argument(code="INPUT", name="Input", type="file", required=1),
            Argument(code="LOG_LEVEL", name="Log Level", type="valued_option", required=0),
        ]
    )
    
    component = CommandComponent(command, simple_mode=False)
    
    # Remplir l'input
    component.argument_components["INPUT"]["component"].set_value("input.txt")
    
    # Ne pas cocher log level
    
    full_command = component._build_full_command()
    # Le placeholder {LOG_LEVEL} doit être supprimé
    assert full_command == "mycommand input.txt"


def test_build_command_with_option_checked_but_empty(qapp):
    """Test la génération avec une option cochée mais vide."""
    command = Command(
        name="test",
        description="Test",
        command="mycommand {INPUT} {LOG_LEVEL}",
        arguments=[
            Argument(code="INPUT", name="Input", type="file", required=1),
            Argument(code="LOG_LEVEL", name="Log Level", type="valued_option", required=0),
        ]
    )
    
    component = CommandComponent(command, simple_mode=False)
    
    # Remplir l'input
    component.argument_components["INPUT"]["component"].set_value("input.txt")
    
    # Cocher mais ne pas remplir
    component.argument_components["LOG_LEVEL"]["component"].checkbox.setChecked(True)
    
    full_command = component._build_full_command()
    # Même cochée, si vide, l'option est supprimée
    assert full_command == "mycommand input.txt"


def test_build_command_multiple_options(qapp):
    """Test la génération avec plusieurs options."""
    command = Command(
        name="test",
        description="Test",
        command="mycommand {INPUT} {DEBUG} {VERBOSE} --log {LOG_FILE} --threads {THREADS}",
        arguments=[
            Argument(code="INPUT", name="Input", type="file", required=1),
            Argument(code="DEBUG", name="Debug", type="flag", required=0),
            Argument(code="VERBOSE", name="Verbose", type="flag", required=0),
            Argument(code="LOG_FILE", name="Log File", type="valued_option", required=0),
            Argument(code="THREADS", name="Threads", type="valued_option", required=0),
        ]
    )
    
    component = CommandComponent(command, simple_mode=False)
    
    # Remplir l'input
    component.argument_components["INPUT"]["component"].set_value("input.txt")
    
    # Cocher debug
    component.argument_components["DEBUG"]["component"].checkbox.setChecked(True)
    
    # Ne pas cocher verbose
    
    # Cocher et remplir threads
    component.argument_components["THREADS"]["component"].checkbox.setChecked(True)
    component.argument_components["THREADS"]["component"].line_edit.setText("4")
    
    # Ne pas cocher log_file
    
    full_command = component._build_full_command()
    # Doit contenir input, debug, threads mais pas verbose ni log_file
    assert "input.txt" in full_command
    assert "4" in full_command  # threads value
    assert "--threads" in full_command
    # Vérifier que les espaces sont bien nettoyés
    assert "  " not in full_command  # Pas de double espace


def test_build_command_spaces_cleanup(qapp):
    """Test que les espaces multiples sont nettoyés."""
    command = Command(
        name="test",
        description="Test",
        command="mycommand {INPUT} {OPT1} {OPT2} {OPT3} output.txt",
        arguments=[
            Argument(code="INPUT", name="Input", type="file", required=1),
            Argument(code="OPT1", name="Opt1", type="flag", required=0),
            Argument(code="OPT2", name="Opt2", type="flag", required=0),
            Argument(code="OPT3", name="Opt3", type="flag", required=0),
        ]
    )
    
    component = CommandComponent(command, simple_mode=False)
    
    # Remplir l'input
    component.argument_components["INPUT"]["component"].set_value("input.txt")
    
    # Ne cocher aucune option
    
    full_command = component._build_full_command()
    # Les 3 options sont supprimées, il ne doit pas y avoir d'espaces multiples
    assert full_command == "mycommand input.txt output.txt"
    assert "  " not in full_command


def test_build_command_with_default_option_value(qapp):
    """Test la génération avec une option ayant une valeur par défaut."""
    command = Command(
        name="test",
        description="Test",
        command="mycommand {INPUT} --threads {THREADS}",
        arguments=[
            Argument(code="INPUT", name="Input", type="file", required=1),
            Argument(code="THREADS", name="Threads", type="valued_option", required=0, default="4"),
        ]
    )
    
    component = CommandComponent(command, simple_mode=False)
    
    # Remplir l'input
    component.argument_components["INPUT"]["component"].set_value("input.txt")
    
    # L'option threads doit être cochée et remplie par défaut
    full_command = component._build_full_command()
    assert full_command == "mycommand input.txt --threads 4"


def test_build_command_valued_option_removes_cli_flag(qapp):
    """Test que les valued_option vides sont supprimés (placeholders uniquement)."""
    command = Command(
        name="test",
        description="Test",
        command="mycommand {INPUT} {PROJECT_NAME} {LOG_FILE} {THREADS}",
        arguments=[
            Argument(code="INPUT", name="Input", type="file", required=1),
            Argument(code="PROJECT_NAME", name="Project", type="valued_option", required=0),
            Argument(code="LOG_FILE", name="Log File", type="valued_option", required=0),
            Argument(code="THREADS", name="Threads", type="valued_option", required=0, default="4"),
        ]
    )
    
    component = CommandComponent(command, simple_mode=False)
    
    # Remplir seulement l'input (THREADS a une valeur par défaut)
    component.argument_components["INPUT"]["component"].set_value("input.txt")
    
    full_command = component._build_full_command()
    
    # Vérifier que les placeholders vides sont supprimés
    assert "PROJECT_NAME" not in full_command
    assert "LOG_FILE" not in full_command
    assert "{" not in full_command
    assert "}" not in full_command
    
    # Vérifier que l'option avec valeur par défaut est présente
    assert "4" in full_command
    
    # La commande finale doit être propre
    assert full_command == "mycommand input.txt 4"


def test_build_command_optional_positional_argument_removed(qapp):
    """Test que les arguments positionnels optionnels vides sont supprimés."""
    command = Command(
        name="test",
        description="Test",
        command="campaignexport {DATABASE} {TXT_DIR} {IMG_DIR} {TOLERANCE}",
        arguments=[
            Argument(code="DATABASE", name="Base de données", type="file", required=1),
            Argument(code="TXT_DIR", name="Répertoire texte", type="directory", required=1),
            Argument(code="IMG_DIR", name="Répertoire images", type="directory", required=1),
            Argument(code="TOLERANCE", name="Tolérance image", type="float", required=0, default=""),
        ]
    )
    
    component = CommandComponent(command, simple_mode=False)
    
    # Remplir les arguments obligatoires seulement
    component.argument_components["DATABASE"]["component"].set_value("data.db")
    component.argument_components["TXT_DIR"]["component"].set_value("txt_output")
    component.argument_components["IMG_DIR"]["component"].set_value("img_output")
    # TOLERANCE reste vide
    
    full_command = component._build_full_command()
    
    # Vérifier que TOLERANCE n'apparaît pas
    assert "TOLERANCE" not in full_command
    assert "Tolérance" not in full_command
    assert "{" not in full_command  # Pas de placeholder
    
    # La commande finale doit être propre sans l'argument optionnel
    assert full_command == "campaignexport data.db txt_output img_output"
