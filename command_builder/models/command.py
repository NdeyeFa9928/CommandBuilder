from pydantic import BaseModel
from typing import List
from command_builder.models.arguments import Argument
from command_builder.models.with_argument import WithArguments


class Command(BaseModel, WithArguments):
    """
    Représente une commande avec ses arguments.
    Hérite de WithArguments pour bénéficier des méthodes communes de gestion des arguments.
    """
    name: str
    description: str
    command: str
    arguments: List[Argument]
