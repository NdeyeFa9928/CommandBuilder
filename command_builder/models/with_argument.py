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
    """
    
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
