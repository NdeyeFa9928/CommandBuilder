from typing import List

from pydantic import BaseModel

from command_builder.models.arguments import Argument
from command_builder.models.with_argument import WithArguments


class Command(BaseModel, WithArguments):
    """
    Représente une commande avec ses arguments.
    Hérite de WithArguments pour bénéficier des méthodes communes de gestion des arguments.

    Les méthodes de validation (validate_arguments, get_required_arguments, etc.)
    sont héritées de WithArguments.
    """

    name: str
    description: str
    command: str
    arguments: List[Argument]
