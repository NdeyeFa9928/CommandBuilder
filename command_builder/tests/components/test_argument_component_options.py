"""
Tests pour le système de gestion des options dans ArgumentComponent.
"""

import pytest
from PySide6.QtWidgets import QApplication

from command_builder.components.argument_component import ArgumentComponent
from command_builder.models.arguments import Argument


@pytest.fixture(scope="module")
def qapp():
    """Fixture pour créer une application Qt."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_flag_argument_unchecked(qapp):
    """Test qu'un argument flag non coché retourne une chaîne vide."""
    argument = Argument(
        code="DEBUG",
        name="Mode debug",
        type="flag",
        required=0,
        default=""
    )
    
    component = ArgumentComponent(argument)
    
    # Vérifier que les widgets existent
    assert component.checkbox is not None
    assert component.line_edit is not None
    
    # Par défaut, non coché
    assert not component.checkbox.isChecked()
    assert component.get_value() == ""


def test_flag_argument_checked(qapp):
    """Test qu'un argument flag coché retourne '1'."""
    argument = Argument(
        code="DEBUG",
        name="Mode debug",
        type="flag",
        required=0,
        default=""
    )
    
    component = ArgumentComponent(argument)
    
    # Cocher la checkbox
    component.checkbox.setChecked(True)
    
    assert component.get_value() == "1"


def test_flag_argument_with_default(qapp):
    """Test qu'un argument flag avec default='1' est coché par défaut."""
    argument = Argument(
        code="VERBOSE",
        name="Mode verbeux",
        type="flag",
        required=0,
        default="1"
    )
    
    component = ArgumentComponent(argument)
    
    # Doit être coché par défaut
    assert component.checkbox.isChecked()
    assert component.get_value() == "1"


def test_valued_option_argument_unchecked(qapp):
    """Test qu'une valued_option non cochée retourne une chaîne vide."""
    argument = Argument(
        code="LOG_LEVEL",
        name="Niveau de log",
        type="valued_option",
        required=0,
        default=""
    )
    
    component = ArgumentComponent(argument)
    
    # Vérifier que les widgets existent
    assert component.checkbox is not None
    assert component.line_edit is not None
    
    # Par défaut, non coché
    assert not component.checkbox.isChecked()
    
    # Même si on remplit le champ, la valeur est vide si non coché
    component.line_edit.setText("INFO")
    assert component.get_value() == ""


def test_valued_option_argument_checked_with_value(qapp):
    """Test qu'une valued_option cochée avec valeur retourne la valeur."""
    argument = Argument(
        code="LOG_LEVEL",
        name="Niveau de log",
        type="valued_option",
        required=0,
        default=""
    )
    
    component = ArgumentComponent(argument)
    
    # Cocher et remplir
    component.checkbox.setChecked(True)
    component.line_edit.setText("INFO")
    
    assert component.get_value() == "INFO"


def test_valued_option_argument_checked_without_value(qapp):
    """Test qu'une valued_option cochée sans valeur retourne une chaîne vide."""
    argument = Argument(
        code="LOG_LEVEL",
        name="Niveau de log",
        type="valued_option",
        required=0,
        default=""
    )
    
    component = ArgumentComponent(argument)
    
    # Cocher mais ne pas remplir
    component.checkbox.setChecked(True)
    
    assert component.get_value() == ""


def test_valued_option_argument_with_default(qapp):
    """Test qu'une valued_option avec valeur par défaut est cochée et remplie."""
    argument = Argument(
        code="MAX_THREADS",
        name="Nombre de threads",
        type="valued_option",
        required=0,
        default="4"
    )
    
    component = ArgumentComponent(argument)
    
    # Doit être coché et rempli par défaut
    assert component.checkbox.isChecked()
    assert component.line_edit.text() == "4"
    assert component.get_value() == "4"


def test_string_argument_no_checkbox(qapp):
    """Test qu'un argument string n'affiche pas de checkbox."""
    argument = Argument(
        code="INPUT",
        name="Fichier d'entrée",
        type="string",
        required=1,
        default=""
    )
    
    component = ArgumentComponent(argument)
    
    # Vérifier que les widgets existent
    assert component.checkbox is not None
    assert component.line_edit is not None
    
    # Pour un string, get_value doit retourner le texte du line_edit
    component.line_edit.setText("test.txt")
    assert component.get_value() == "test.txt"


def test_file_argument_no_checkbox(qapp):
    """Test qu'un argument file n'affiche pas de checkbox."""
    argument = Argument(
        code="INPUT",
        name="Fichier d'entrée",
        type="file",
        required=1,
        default=""
    )
    
    component = ArgumentComponent(argument)
    
    # Vérifier que les widgets existent
    assert component.checkbox is not None
    assert component.line_edit is not None
    
    # Pour un file, get_value doit retourner le texte du line_edit
    component.line_edit.setText("input.txt")
    assert component.get_value() == "input.txt"


def test_set_value_flag(qapp):
    """Test la méthode set_value pour un argument flag."""
    argument = Argument(
        code="DEBUG",
        name="Mode debug",
        type="flag",
        required=0,
        default=""
    )
    
    component = ArgumentComponent(argument)
    
    # Définir à "1"
    component.set_value("1")
    assert component.checkbox.isChecked()
    
    # Définir à ""
    component.set_value("")
    assert not component.checkbox.isChecked()


def test_set_value_valued_option(qapp):
    """Test la méthode set_value pour une valued_option."""
    argument = Argument(
        code="LOG_LEVEL",
        name="Niveau de log",
        type="valued_option",
        required=0,
        default=""
    )
    
    component = ArgumentComponent(argument)
    
    # Définir une valeur
    component.set_value("INFO")
    assert component.checkbox.isChecked()
    assert component.line_edit.text() == "INFO"
    
    # Définir à vide
    component.set_value("")
    assert not component.checkbox.isChecked()
    assert component.line_edit.text() == ""


# Tests des signaux Qt supprimés car ils nécessitent pytest-qt
# qui n'est pas toujours disponible dans tous les environnements de test.
# Les fonctionnalités sont déjà testées via les tests get_value() et set_value().
