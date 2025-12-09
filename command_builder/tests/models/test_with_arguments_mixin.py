"""Tests unitaires pour le mixin `WithArguments` (présent dans `command_builder.models.with_argument`).
Ces tests n'impliquent aucun composant Qt et sont donc sûrs sur toutes les plateformes.
"""

from command_builder.models.arguments import Argument
from command_builder.models.command import Command


def _make_command(values: dict[str, str] | None = None):
    """Crée une commande de test avec deux arguments (req + opt)."""
    values = values or {}
    return Command(
        name="Dummy",
        description="cmd",
        command="echo {input} {opt}",
        arguments=[
            Argument(
                code="input",
                name="Input",
                required=True,
                default=values.get("input", ""),
            ),
            Argument(
                code="opt",
                name="Optional",
                required=False,
                default=values.get("opt", "def"),
            ),
        ],
    )


class TestWithArguments:
    """Validation du contrat d'API fourni par le mixin."""

    def test_get_argument_by_code(self):
        cmd = _make_command()
        assert cmd.get_argument_by_code("input").code == "input"
        assert cmd.get_argument_by_code("missing") is None

    def test_required_and_optional_lists(self):
        cmd = _make_command()
        req = cmd.get_required_arguments()
        opt = cmd.get_optional_arguments()
        assert len(req) == 1 and req[0].code == "input"
        assert len(opt) == 1 and opt[0].code == "opt"

    def test_count_methods(self):
        cmd = _make_command()
        assert cmd.count_arguments() == 2
        assert cmd.count_required_arguments() == 1

    def test_has_required_arguments_false_then_true(self):
        cmd = _make_command()
        # valeur requise absente -> False
        assert cmd.has_required_arguments() is False
        # on remplit la valeur requise
        cmd.get_argument_by_code("input").default = "file.txt"
        assert cmd.has_required_arguments() is True

    def test_get_argument_values(self):
        cmd = _make_command({"input": "data.csv"})
        values = cmd.get_argument_values()
        # input défini, opt possède sa valeur par défaut
        assert values == {"input": "data.csv", "opt": "def"}
