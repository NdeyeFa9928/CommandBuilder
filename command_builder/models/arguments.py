from pydantic import BaseModel
from typing import Optional, Any, List


class Argument(BaseModel):
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
    """Argument au niveau de la tâche, partagé entre plusieurs commandes."""
    code: str
    name: str
    description: Optional[str] = ""
    type: Optional[str] = "string"
    required: Optional[int] = 0
    default: Optional[str] = ""
    validation: Optional[dict[str, Any]] = None
    values: List[ArgumentValue] = []  # Liste des commandes/arguments cibles
