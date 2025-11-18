"""
Module contenant les mixins et interfaces pour les modèles.
"""

from abc import ABC
from typing import List, Optional, Dict, Any


class WithArguments:
    """
    Interface pour les objets qui contiennent des arguments.
    Permet de factoriser le comportement commun entre Task et Command.
    
    Les classes qui héritent de ce mixin doivent avoir un attribut 'arguments'.
    Avec Pydantic, cet attribut est automatiquement créé via la définition du champ.
    
    Fournit également la validation des arguments obligatoires.
    """
    
    @staticmethod
    def validate_single_argument(arg: Any, value: str) -> tuple[bool, Optional[str]]:
        """
        Valide un argument individuel.
        Méthode statique pour éviter la duplication dans Argument et TaskArgument.
        
        Args:
            arg: L'argument à valider (doit avoir 'required' et 'name')
            value: La valeur à valider
            
        Returns:
            Tuple (is_valid, error_message)
        """
        if not hasattr(arg, 'required') or not hasattr(arg, 'name'):
            return True, None
        
        if (arg.required == 1 or arg.required is True) and not value.strip():
            return False, f"Le champ '{arg.name}' est obligatoire"
        
        return True, None
    
    def get_argument_by_code(self, code: str) -> Optional[Any]:
        """
        Récupère un argument par son code.
        
        Args:
            code: Le code de l'argument à rechercher
            
        Returns:
            L'argument trouvé ou None
        """
        if not self.arguments:
            return None
        
        for arg in self.arguments:
            if hasattr(arg, 'code') and arg.code == code:
                return arg
        return None
    
    def validate_arguments(self, argument_values: Dict[str, str]) -> tuple[bool, List[str]]:
        """
        Valide que tous les arguments requis sont fournis et valides.
        
        Cette méthode centralise la logique de validation pour tous les objets
        qui contiennent des arguments (Command, Task, etc.).
        
        Args:
            argument_values: Dictionnaire {code_argument: valeur}
            
        Returns:
            Tuple (is_valid, error_messages)
            - is_valid: True si tous les arguments sont valides
            - error_messages: Liste des messages d'erreur
        """
        if not hasattr(self, 'arguments') or not self.arguments:
            return True, []
        
        errors = []
        
        for arg in self.arguments:
            value = argument_values.get(arg.code, "")
            # Utiliser directement la méthode statique
            is_valid, error_msg = self.validate_single_argument(arg, value)
            
            if not is_valid and error_msg:
                errors.append(error_msg)
        
        return len(errors) == 0, errors
    
    def get_required_arguments(self) -> List[Any]:
        """
        Retourne la liste des arguments obligatoires.
        
        Returns:
            Liste des arguments avec required=1 (ou True)
        """
        if not hasattr(self, 'arguments') or not self.arguments:
            return []
        
        return [
            arg for arg in self.arguments 
            if hasattr(arg, 'required') and (arg.required == 1 or arg.required is True)
        ]
    
    def get_optional_arguments(self) -> List[Any]:
        """
        Retourne la liste des arguments optionnels.
        
        Returns:
            Liste des arguments avec required=0 (ou False)
        """
        if not hasattr(self, 'arguments') or not self.arguments:
            return []
        
        return [
            arg for arg in self.arguments 
            if hasattr(arg, 'required') and (arg.required == 0 or arg.required is False)
        ]
    
    def get_argument_values(self) -> Dict[str, str]:
        """
        Récupère toutes les valeurs par défaut des arguments.
        
        Returns:
            Dictionnaire {code: valeur_par_defaut}
        """
        values = {}
        if not self.arguments:
            return values
            
        for arg in self.arguments:
            if hasattr(arg, 'code') and hasattr(arg, 'default'):
                values[arg.code] = arg.default or ""
        return values
    
    def has_required_arguments(self) -> bool:
        """
        Vérifie si tous les arguments requis ont une valeur.
        
        Returns:
            True si tous les arguments requis sont remplis, False sinon
        """
        if not self.arguments:
            return True
            
        for arg in self.arguments:
            if hasattr(arg, 'required') and arg.required:
                if not hasattr(arg, 'default') or not arg.default:
                    return False
        return True
    
    def get_required_arguments(self) -> List[Any]:
        """
        Retourne uniquement les arguments requis.
        
        Returns:
            Liste des arguments requis
        """
        if not self.arguments:
            return []
            
        return [
            arg for arg in self.arguments 
            if hasattr(arg, 'required') and arg.required
        ]
    
    def get_optional_arguments(self) -> List[Any]:
        """
        Retourne uniquement les arguments optionnels.
        
        Returns:
            Liste des arguments optionnels
        """
        if not self.arguments:
            return []
            
        return [
            arg for arg in self.arguments 
            if not hasattr(arg, 'required') or not arg.required
        ]
    
    def has_argument(self, code: str) -> bool:
        """
        Vérifie si un argument avec ce code existe.
        
        Args:
            code: Le code de l'argument à vérifier
            
        Returns:
            True si l'argument existe, False sinon
        """
        return self.get_argument_by_code(code) is not None
    
    def count_arguments(self) -> int:
        """
        Retourne le nombre total d'arguments.
        
        Returns:
            Nombre d'arguments
        """
        return len(self.arguments) if self.arguments else 0
    
    def count_required_arguments(self) -> int:
        """
        Retourne le nombre d'arguments requis.
        
        Returns:
            Nombre d'arguments requis
        """
        return len(self.get_required_arguments())
