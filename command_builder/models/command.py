"""
Modèles Pydantic pour les commandes et leurs paramètres.
"""
from typing import List, Optional, Any, Dict, Union
from enum import Enum
from pydantic import BaseModel, Field, validator


class ParameterType(str, Enum):
    """Types de paramètres supportés."""
    FILE = "file"
    DIRECTORY = "directory"
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"


class CommandCategory(str, Enum):
    """Catégories de commandes."""
    IMPORT = "import"
    ANALYSIS = "analysis"
    EXPORT = "export"
    UTILITY = "utility"


class ParameterValidation(BaseModel):
    """Règles de validation pour un paramètre."""
    file_extensions: Optional[List[str]] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    pattern: Optional[str] = None


class Parameter(BaseModel):
    """Définition d'un paramètre de commande."""
    name: str = Field(..., description="Nom du paramètre")
    flag: Optional[str] = Field(None, description="Flag de ligne de commande")
    type: ParameterType = Field(..., description="Type de données")
    description: str = Field(..., description="Description du paramètre")
    default: Optional[Any] = Field(None, description="Valeur par défaut")
    validation: Optional[ParameterValidation] = None

    @validator('flag')
    def validate_flag(cls, v):
        """Valide que le flag commence par -- ou -."""
        if v is not None and not (v.startswith('--') or v.startswith('-')):
            raise ValueError("Le flag doit commencer par '--' ou '-'")
        return v


class CommandParameters(BaseModel):
    """Paramètres d'une commande (requis et optionnels)."""
    required: List[Parameter] = Field(default_factory=list)
    optional: List[Parameter] = Field(default_factory=list)


class Command(BaseModel):
    """Définition complète d'une commande."""
    name: str = Field(..., description="Nom de la commande")
    description: str = Field(..., description="Description de l'objectif")
    category: CommandCategory = Field(..., description="Catégorie de la commande")
    executable: str = Field(..., description="Nom de l'exécutable")
    parameters: CommandParameters = Field(..., description="Paramètres de la commande")
    inputs: List[str] = Field(default_factory=list, description="Types d'entrées")
    outputs: List[str] = Field(default_factory=list, description="Types de sorties")

    def get_all_parameters(self) -> List[Parameter]:
        """Retourne tous les paramètres (requis + optionnels)."""
        return self.parameters.required + self.parameters.optional

    def get_parameter_by_name(self, name: str) -> Optional[Parameter]:
        """Trouve un paramètre par son nom."""
        for param in self.get_all_parameters():
            if param.name == name:
                return param
        return None

    def build_command_line(self, values: Dict[str, Any]) -> List[str]:
        """Construit la ligne de commande avec les valeurs fournies."""
        cmd_parts = [self.executable]
        
        # Ajouter les paramètres requis
        for param in self.parameters.required:
            if param.name not in values:
                raise ValueError(f"Paramètre requis manquant: {param.name}")
            
            value = values[param.name]
            if param.flag:
                cmd_parts.append(param.flag)
                if param.type != ParameterType.BOOLEAN or value:
                    cmd_parts.append(str(value))
            else:
                cmd_parts.append(str(value))
        
        # Ajouter les paramètres optionnels fournis
        for param in self.parameters.optional:
            if param.name in values:
                value = values[param.name]
                if param.type == ParameterType.BOOLEAN:
                    if value:  # Seulement ajouter le flag si True
                        cmd_parts.append(param.flag)
                else:
                    if param.flag:
                        cmd_parts.append(param.flag)
                    cmd_parts.append(str(value))
        
        return cmd_parts


class CommandInstance(BaseModel):
    """Instance d'une commande avec des valeurs spécifiques."""
    command: Command
    values: Dict[str, Any] = Field(default_factory=dict)
    
    def validate_values(self) -> List[str]:
        """Valide les valeurs fournies et retourne les erreurs."""
        errors = []
        
        # Vérifier les paramètres requis
        for param in self.command.parameters.required:
            if param.name not in self.values:
                errors.append(f"Paramètre requis manquant: {param.name}")
        
        # Valider les types et contraintes
        for param_name, value in self.values.items():
            param = self.command.get_parameter_by_name(param_name)
            if param:
                # Validation basique du type
                if param.type == ParameterType.INTEGER and not isinstance(value, int):
                    try:
                        int(value)
                    except ValueError:
                        errors.append(f"{param_name}: doit être un entier")
                
                elif param.type == ParameterType.FLOAT and not isinstance(value, (int, float)):
                    try:
                        float(value)
                    except ValueError:
                        errors.append(f"{param_name}: doit être un nombre")
                
                elif param.type == ParameterType.BOOLEAN and not isinstance(value, bool):
                    if str(value).lower() not in ['true', 'false', '1', '0']:
                        errors.append(f"{param_name}: doit être un booléen")
        
        return errors
    
    def to_command_line(self) -> List[str]:
        """Génère la ligne de commande."""
        return self.command.build_command_line(self.values)
