"""Service de gestion des erreurs YAML."""

from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
from pydantic import ValidationError
import yaml

from command_builder.models.yaml_error import YamlError
from command_builder.models.task import Task
from command_builder.services.yaml_loader import load_yaml_with_includes


class YamlErrorHandler:
    """Gère le chargement des tâches YAML et la collecte des erreurs."""

    def __init__(self):
        """Initialise le gestionnaire d'erreurs."""
        self.errors: List[YamlError] = []
        self.loaded_tasks: List[Task] = []

    def _create_error(
        self,
        file_name: str,
        error_type: str,
        error_message: str,
        line_number: Optional[int] = None,
        suggestion: Optional[str] = None,
    ) -> YamlError:
        """Crée une erreur YAML et l'ajoute à la liste."""
        error = YamlError(
            file_name=file_name,
            error_type=error_type,
            error_message=error_message,
            line_number=line_number,
            suggestion=suggestion,
        )
        self.errors.append(error)
        return error

    def load_yaml_task(self, file_path: Path) -> Optional[Task]:
        """
        Charge une tâche YAML et capture les erreurs.

        Args:
            file_path: Chemin vers le fichier YAML

        Returns:
            L'objet Task si succès, None si erreur
        """
        file_name = file_path.name

        try:
            # Charger le YAML
            yaml_data = load_yaml_with_includes(str(file_path))

            # Traiter les inclusions de commandes (aplatir les listes)
            if "commands" in yaml_data and isinstance(yaml_data["commands"], list):
                resolved_commands = []
                for cmd in yaml_data["commands"]:
                    # Si c'est une liste (inclusion résolue), ajouter tous les éléments
                    if isinstance(cmd, list):
                        resolved_commands.extend(cmd)
                    else:
                        resolved_commands.append(cmd)
                yaml_data["commands"] = resolved_commands

            # Valider et convertir en modèle Task
            task = Task(**yaml_data)
            return task

        except FileNotFoundError as e:
            self._create_error(
                file_name=file_name,
                error_type="FileNotFoundError",
                error_message=f"Fichier non trouvé: {str(e)}",
                suggestion="Vérifiez que le chemin du fichier est correct.",
            )
            return None

        except yaml.YAMLError as e:
            # Erreur de syntaxe YAML
            line_number = None
            if hasattr(e, "problem_mark"):
                line_number = e.problem_mark.line + 1

            self._create_error(
                file_name=file_name,
                error_type="SyntaxError",
                error_message=f"Erreur de syntaxe YAML: {str(e)}",
                line_number=line_number,
                suggestion="Vérifiez l'indentation et la syntaxe YAML du fichier.",
            )
            return None

        except ValidationError as e:
            # Erreur de validation Pydantic
            errors = e.errors()
            error_details = []
            for err in errors:
                field = ".".join(str(x) for x in err["loc"])
                msg = err["msg"]
                error_details.append(f"{field}: {msg}")

            self._create_error(
                file_name=file_name,
                error_type="ValidationError",
                error_message="Erreur de validation:\n  " + "\n  ".join(error_details),
                suggestion="Vérifiez que tous les champs requis sont présents et valides.",
            )
            return None

        except Exception as e:
            # Erreur générique
            self._create_error(
                file_name=file_name,
                error_type=type(e).__name__,
                error_message=str(e),
                suggestion="Vérifiez le contenu du fichier YAML.",
            )
            return None

    def load_all_tasks(
        self, task_files: List[Path]
    ) -> Tuple[List[Task], List[YamlError]]:
        """
        Charge toutes les tâches YAML et collecte les erreurs.

        Args:
            task_files: Liste des fichiers YAML à charger

        Returns:
            Tuple (liste des tâches chargées, liste des erreurs)
        """
        self.errors.clear()
        self.loaded_tasks.clear()

        for file_path in task_files:
            task = self.load_yaml_task(file_path)
            if task:
                self.loaded_tasks.append(task)

        return self.loaded_tasks, self.errors

    def has_errors(self) -> bool:
        """Retourne True s'il y a des erreurs."""
        return len(self.errors) > 0

    def has_critical_errors(self) -> bool:
        """Retourne True s'il y a des erreurs critiques."""
        return any(error.is_critical() for error in self.errors)

    def get_error_summary(self) -> str:
        """Retourne un résumé des erreurs."""
        if not self.errors:
            return "Aucune erreur"

        summary = f"{len(self.errors)} erreur(s) détectée(s):\n\n"
        for i, error in enumerate(self.errors, 1):
            summary += f"{i}. {error}\n\n"

        return summary
