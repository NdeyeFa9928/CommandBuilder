"""
Modèles Pydantic pour les commandes et leurs arguments.
"""
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field, validator
import os
import shlex


class CommandArgument(BaseModel):
    """Définition d'un argument de commande."""
    code: str = Field(..., description="Code unique de l'argument")
    name: str = Field(..., description="Nom lisible de l'argument")
    description: str = Field(..., description="Description détaillée")
    type: str = Field(..., description="Type de l'argument (file, directory, string, int, float, bool)")
    required: bool = Field(default=False, description="Si l'argument est obligatoire")
    default: Optional[Any] = Field(None, description="Valeur par défaut")
    validation: Optional[Dict[str, Any]] = Field(None, description="Règles de validation")
    
    def validate_value(self, value: Any) -> List[str]:
        """Valide une valeur pour cet argument selon son type et ses règles de validation."""
        errors = []
        
        # Vérification de base selon le type
        if value is None:
            if self.required:
                errors.append(f"L'argument {self.name} est requis")
            return errors
        
        # Validation selon le type
        if self.type == "file":
            if not isinstance(value, str):
                errors.append(f"L'argument {self.name} doit être un chemin de fichier")
            elif not os.path.isfile(value):
                errors.append(f"Le fichier {value} n'existe pas")
            elif self.validation and "file_extensions" in self.validation:
                ext = os.path.splitext(value)[1].lower()
                if ext not in self.validation["file_extensions"]:
                    allowed = ", ".join(self.validation["file_extensions"])
                    errors.append(f"Le fichier {value} doit avoir une extension parmi: {allowed}")
        
        elif self.type == "directory":
            if not isinstance(value, str):
                errors.append(f"L'argument {self.name} doit être un chemin de répertoire")
            elif not os.path.isdir(value):
                errors.append(f"Le répertoire {value} n'existe pas")
        
        elif self.type == "int":
            try:
                int_val = int(value)
                if self.validation:
                    if "min" in self.validation and int_val < self.validation["min"]:
                        errors.append(f"L'argument {self.name} doit être >= {self.validation['min']}")
                    if "max" in self.validation and int_val > self.validation["max"]:
                        errors.append(f"L'argument {self.name} doit être <= {self.validation['max']}")
            except (ValueError, TypeError):
                errors.append(f"L'argument {self.name} doit être un entier")
        
        elif self.type == "float":
            try:
                float_val = float(value)
                if self.validation:
                    if "min" in self.validation and float_val < self.validation["min"]:
                        errors.append(f"L'argument {self.name} doit être >= {self.validation['min']}")
                    if "max" in self.validation and float_val > self.validation["max"]:
                        errors.append(f"L'argument {self.name} doit être <= {self.validation['max']}")
            except (ValueError, TypeError):
                errors.append(f"L'argument {self.name} doit être un nombre")
        
        elif self.type == "bool":
            if not isinstance(value, bool) and value not in (0, 1, "0", "1", "true", "false", "True", "False"):
                errors.append(f"L'argument {self.name} doit être une valeur booléenne")
        
        # Validation personnalisée supplémentaire
        if self.validation and "pattern" in self.validation and isinstance(value, str):
            import re
            pattern = self.validation["pattern"]
            if not re.match(pattern, value):
                errors.append(f"L'argument {self.name} ne correspond pas au format requis")
        
        return errors


class Command(BaseModel):
    """Définition d'une commande avec ses arguments."""
    name: str = Field(..., description="Nom unique de la commande")
    description: str = Field(..., description="Description de la commande")
    command: str = Field(..., description="Modèle de ligne de commande avec placeholders")
    arguments: List[CommandArgument] = Field(default_factory=list, description="Arguments de la commande")
    
    def get_argument_by_code(self, code: str) -> Optional[CommandArgument]:
        """Trouve un argument par son code."""
        for arg in self.arguments:
            if arg.code == code:
                return arg
        return None
    
    def get_required_arguments(self) -> List[CommandArgument]:
        """Retourne la liste des arguments obligatoires."""
        return [arg for arg in self.arguments if arg.required]
    
    def get_optional_arguments(self) -> List[CommandArgument]:
        """Retourne la liste des arguments optionnels."""
        return [arg for arg in self.arguments if not arg.required]


class CommandInstance(BaseModel):
    """Instance d'une commande avec des valeurs pour ses arguments."""
    command: Command
    values: Dict[str, Any] = Field(default_factory=dict, description="Valeurs des arguments")
    
    def set_value(self, arg_code: str, value: Any):
        """Définit la valeur d'un argument."""
        if self.command.get_argument_by_code(arg_code) is not None:
            self.values[arg_code] = value
    
    def get_value(self, arg_code: str) -> Any:
        """Récupère la valeur d'un argument."""
        return self.values.get(arg_code)
    
    def validate_values(self) -> List[str]:
        """Valide toutes les valeurs des arguments."""
        errors = []
        
        # Vérifier les arguments requis
        for arg in self.command.get_required_arguments():
            if arg.code not in self.values:
                errors.append(f"L'argument requis '{arg.name}' n'est pas défini")
        
        # Valider chaque valeur définie
        for arg_code, value in self.values.items():
            arg = self.command.get_argument_by_code(arg_code)
            if arg:
                arg_errors = arg.validate_value(value)
                errors.extend(arg_errors)
            else:
                errors.append(f"Argument inconnu: {arg_code}")
        
        return errors
    
    def to_command_line(self) -> List[str]:
        """
        Génère la ligne de commande complète avec les valeurs des arguments.
        Retourne une liste de segments pour éviter les problèmes d'échappement.
        """
        if not self.values:
            return []
        
        # Remplacer les placeholders dans le modèle de commande
        cmd_template = self.command.command
        for arg_code, value in self.values.items():
            placeholder = "{" + arg_code + "}"
            if placeholder in cmd_template:
                if value is not None:
                    cmd_template = cmd_template.replace(placeholder, str(value))
                else:
                    # Supprimer les options avec des valeurs None
                    parts = cmd_template.split()
                    filtered_parts = []
                    skip_next = False
                    for i, part in enumerate(parts):
                        if placeholder in part:
                            if part.startswith("--") and "=" not in part:
                                skip_next = True
                            continue
                        if skip_next:
                            skip_next = False
                            continue
                        filtered_parts.append(part)
                    cmd_template = " ".join(filtered_parts)
        
        # Diviser la commande en segments
        return shlex.split(cmd_template)
    
    def to_command_string(self) -> str:
        """Génère la ligne de commande sous forme de chaîne."""
        cmd_parts = self.to_command_line()
        return " ".join(cmd_parts)
