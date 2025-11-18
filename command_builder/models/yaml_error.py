"""Modèle pour représenter une erreur YAML."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class YamlError:
    """Représente une erreur lors du chargement d'une tâche YAML.

    Attributes:
        file_name: Nom du fichier YAML avec erreur
        error_type: Type d'erreur (SyntaxError, ValidationError, FileNotFoundError, etc.)
        error_message: Message d'erreur détaillé
        line_number: Numéro de ligne (optionnel)
        suggestion: Suggestion pour corriger l'erreur (optionnel)
    """

    file_name: str
    error_type: str
    error_message: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None

    def __str__(self) -> str:
        """Retourne une représentation lisible de l'erreur."""
        result = f"[{self.error_type}] {self.file_name}"
        if self.line_number:
            result += f" (ligne {self.line_number})"
        result += f"\n  {self.error_message}"
        if self.suggestion:
            result += f"\n  💡 {self.suggestion}"
        return result

    def is_critical(self) -> bool:
        """Retourne True si l'erreur est critique (empêche le chargement)."""
        critical_types = {"SyntaxError", "ValidationError", "FileNotFoundError"}
        return self.error_type in critical_types
