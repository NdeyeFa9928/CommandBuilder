"""Tests unitaires pour la validation des arguments (types, formats, etc.)."""

import pytest
from command_builder.models.arguments import Argument
from command_builder.models.command import Command
from command_builder.models.with_argument import WithArguments


class TestArgumentValidationRequired:
    """Tests de validation des arguments obligatoires."""

    def test_required_argument_empty_fails(self):
        """Test qu'un argument obligatoire vide échoue."""
        arg = Argument(code="INPUT", name="Input", required=1, type="text")
        is_valid, error = WithArguments.validate_single_argument(arg, "")
        
        assert not is_valid
        assert "obligatoire" in error.lower()

    def test_required_argument_whitespace_fails(self):
        """Test qu'un argument obligatoire avec espaces échoue."""
        arg = Argument(code="INPUT", name="Input", required=1, type="text")
        is_valid, error = WithArguments.validate_single_argument(arg, "   ")
        
        assert not is_valid
        assert "obligatoire" in error.lower()

    def test_required_argument_filled_succeeds(self):
        """Test qu'un argument obligatoire rempli réussit."""
        arg = Argument(code="INPUT", name="Input", required=1, type="text")
        is_valid, error = WithArguments.validate_single_argument(arg, "value")
        
        assert is_valid
        assert error is None

    def test_optional_argument_empty_succeeds(self):
        """Test qu'un argument optionnel vide réussit."""
        arg = Argument(code="OPT", name="Optional", required=0, type="text")
        is_valid, error = WithArguments.validate_single_argument(arg, "")
        
        assert is_valid
        assert error is None


class TestArgumentValidationTypes:
    """Tests de validation par type d'argument."""

    def test_text_argument_accepts_any_string(self):
        """Test que le type text accepte n'importe quelle chaîne."""
        arg = Argument(code="TEXT", name="Text", type="text", required=1)
        
        assert WithArguments.validate_single_argument(arg, "simple")[0]
        assert WithArguments.validate_single_argument(arg, "with spaces")[0]
        assert WithArguments.validate_single_argument(arg, "123")[0]
        assert WithArguments.validate_single_argument(arg, "special@#$")[0]

    @pytest.mark.skip(reason="Validation par type non implémentée - à implémenter")
    def test_number_argument_validates_numeric(self):
        """Test que le type number valide les nombres."""
        arg = Argument(code="NUM", name="Number", type="number", required=1)
        
        # Valides
        assert WithArguments.validate_single_argument(arg, "123")[0]
        assert WithArguments.validate_single_argument(arg, "123.45")[0]
        assert WithArguments.validate_single_argument(arg, "-10")[0]
        assert WithArguments.validate_single_argument(arg, "0")[0]
        
        # Invalides
        is_valid, error = WithArguments.validate_single_argument(arg, "abc")
        assert not is_valid
        assert "nombre" in error.lower()
        
        is_valid, error = WithArguments.validate_single_argument(arg, "12.34.56")
        assert not is_valid

    @pytest.mark.skip(reason="Validation par type non implémentée - à implémenter")
    def test_file_argument_validates_path_exists(self):
        """Test que le type file valide l'existence du fichier."""
        arg = Argument(code="FILE", name="File", type="file", required=1)
        
        # Fichier inexistant
        is_valid, error = WithArguments.validate_single_argument(arg, "nonexistent.txt")
        assert not is_valid
        assert "existe pas" in error.lower() or "not found" in error.lower()

    @pytest.mark.skip(reason="Validation par type non implémentée - à implémenter")
    def test_directory_argument_validates_path_exists(self):
        """Test que le type directory valide l'existence du dossier."""
        arg = Argument(code="DIR", name="Directory", type="directory", required=1)
        
        # Dossier inexistant
        is_valid, error = WithArguments.validate_single_argument(arg, "nonexistent_dir")
        assert not is_valid
        assert "existe pas" in error.lower() or "not found" in error.lower()

    def test_boolean_argument_accepts_any_value(self):
        """Test que le type boolean accepte n'importe quelle valeur (checkbox)."""
        arg = Argument(code="BOOL", name="Boolean", type="boolean", required=0)
        
        # Les booléens sont généralement optionnels et acceptent tout
        assert WithArguments.validate_single_argument(arg, "true")[0]
        assert WithArguments.validate_single_argument(arg, "false")[0]
        assert WithArguments.validate_single_argument(arg, "")[0]


class TestCommandValidationIntegration:
    """Tests d'intégration de la validation au niveau Command."""

    def test_command_validate_all_arguments(self):
        """Test de validation de tous les arguments d'une commande."""
        command = Command(
            name="Test",
            description="Test",
            command="test {INPUT} {OPT}",
            arguments=[
                Argument(code="INPUT", name="Input", required=1, type="text"),
                Argument(code="OPT", name="Optional", required=0, type="text"),
            ]
        )
        
        # Tous remplis
        is_valid, errors = command.validate_arguments({"INPUT": "value", "OPT": "opt"})
        assert is_valid
        assert len(errors) == 0
        
        # Argument obligatoire manquant
        is_valid, errors = command.validate_arguments({"INPUT": "", "OPT": "opt"})
        assert not is_valid
        assert len(errors) == 1
        assert "Input" in errors[0]
        
        # Argument optionnel manquant (OK)
        is_valid, errors = command.validate_arguments({"INPUT": "value", "OPT": ""})
        assert is_valid
        assert len(errors) == 0

    def test_command_validate_multiple_errors(self):
        """Test de validation avec plusieurs erreurs."""
        command = Command(
            name="Test",
            description="Test",
            command="test {A} {B} {C}",
            arguments=[
                Argument(code="A", name="Arg A", required=1, type="text"),
                Argument(code="B", name="Arg B", required=1, type="text"),
                Argument(code="C", name="Arg C", required=0, type="text"),
            ]
        )
        
        # Deux arguments obligatoires manquants
        is_valid, errors = command.validate_arguments({"A": "", "B": "", "C": ""})
        assert not is_valid
        assert len(errors) == 2
        assert any("Arg A" in err for err in errors)
        assert any("Arg B" in err for err in errors)


class TestArgumentValidationEdgeCases:
    """Tests des cas limites de validation."""

    def test_argument_without_required_field(self):
        """Test qu'un argument sans champ required est traité comme valide."""
        # Créer un argument sans le champ required (cas limite)
        arg = Argument(code="TEST", name="Test", type="text")
        arg.required = None  # Simuler l'absence du champ
        
        is_valid, error = WithArguments.validate_single_argument(arg, "")
        assert is_valid  # Devrait être valide par défaut

    def test_required_as_boolean_true(self):
        """Test que required=True fonctionne (en plus de required=1)."""
        arg = Argument(code="TEST", name="Test", type="text")
        arg.required = True
        
        is_valid, error = WithArguments.validate_single_argument(arg, "")
        assert not is_valid
        assert "obligatoire" in error.lower()

    def test_required_as_boolean_false(self):
        """Test que required=False fonctionne (en plus de required=0)."""
        arg = Argument(code="TEST", name="Test", type="text")
        arg.required = False
        
        is_valid, error = WithArguments.validate_single_argument(arg, "")
        assert is_valid

    def test_validation_with_default_value(self):
        """Test que la validation utilise la valeur fournie, pas la valeur par défaut."""
        arg = Argument(code="TEST", name="Test", required=1, default="default_value")
        
        # Même avec une valeur par défaut, si on passe "", ça doit échouer
        is_valid, error = WithArguments.validate_single_argument(arg, "")
        assert not is_valid


class TestArgumentValidationCustomRules:
    """Tests pour les règles de validation personnalisées (validation dict)."""

    @pytest.mark.skip(reason="Validation personnalisée non implémentée - à implémenter")
    def test_min_length_validation(self):
        """Test de validation de longueur minimale."""
        arg = Argument(
            code="TEXT",
            name="Text",
            type="text",
            required=1,
            validation={"min_length": 5}
        )
        
        is_valid, error = WithArguments.validate_single_argument(arg, "abc")
        assert not is_valid
        assert "5" in error
        
        is_valid, error = WithArguments.validate_single_argument(arg, "abcdef")
        assert is_valid

    @pytest.mark.skip(reason="Validation personnalisée non implémentée - à implémenter")
    def test_max_length_validation(self):
        """Test de validation de longueur maximale."""
        arg = Argument(
            code="TEXT",
            name="Text",
            type="text",
            required=1,
            validation={"max_length": 10}
        )
        
        is_valid, error = WithArguments.validate_single_argument(arg, "12345678901")
        assert not is_valid
        
        is_valid, error = WithArguments.validate_single_argument(arg, "12345")
        assert is_valid

    @pytest.mark.skip(reason="Validation personnalisée non implémentée - à implémenter")
    def test_pattern_validation(self):
        """Test de validation par expression régulière."""
        arg = Argument(
            code="EMAIL",
            name="Email",
            type="text",
            required=1,
            validation={"pattern": r"^[\w\.-]+@[\w\.-]+\.\w+$"}
        )
        
        is_valid, error = WithArguments.validate_single_argument(arg, "invalid-email")
        assert not is_valid
        
        is_valid, error = WithArguments.validate_single_argument(arg, "user@example.com")
        assert is_valid

    @pytest.mark.skip(reason="Validation personnalisée non implémentée - à implémenter")
    def test_min_max_number_validation(self):
        """Test de validation de plage numérique."""
        arg = Argument(
            code="PORT",
            name="Port",
            type="number",
            required=1,
            validation={"min": 1024, "max": 65535}
        )
        
        is_valid, error = WithArguments.validate_single_argument(arg, "80")
        assert not is_valid
        
        is_valid, error = WithArguments.validate_single_argument(arg, "8080")
        assert is_valid
        
        is_valid, error = WithArguments.validate_single_argument(arg, "70000")
        assert not is_valid
