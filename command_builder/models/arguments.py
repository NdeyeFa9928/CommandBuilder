from typing import Any, List, Optional

from pydantic import BaseModel


class Argument(BaseModel):
    """
    Argument d'une commande.

    La validation est gérée par WithArguments.validate_single_argument().
    """

    code: str
    name: str
    description: Optional[str] = ""
    type: Optional[str] = "string"
    required: Optional[int] = 0
    default: Optional[str] = ""
    validation: Optional[dict[str, Any]] = None


class ArgumentValue(BaseModel):
    """Définit où injecter la valeur d'un argument de tâche."""

    command: str  # Nom de la commande
    argument: str  # Code de l'argument dans la commande


class TaskArgument(BaseModel):
    """
    Argument au niveau de la tâche, partagé entre plusieurs commandes.

    La validation est gérée par WithArguments.validate_single_argument().
    """

    code: str
    name: str
    description: Optional[str] = ""
    type: Optional[str] = "string"
    required: Optional[int] = 0
    default: Optional[str] = ""
    validation: Optional[dict[str, Any]] = None
    values: List[ArgumentValue] = []  # Liste des commandes/arguments cibles
