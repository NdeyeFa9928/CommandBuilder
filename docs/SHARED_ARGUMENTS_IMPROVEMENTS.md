# Améliorations des Arguments Partagés

## Résumé des modifications

Ce document décrit les améliorations apportées à la gestion des arguments partagés dans CommandBuilder.

## Fonctionnalités ajoutées

### 1. Affichage des commandes concernées

Les arguments partagés affichent maintenant les noms des commandes qui les utilisent, directement sous le champ de saisie.

**Exemple d'affichage :**
```
[Champ de saisie pour "Base de données commune"]
Utilisé par : campaignexport, computeprofile, csvexport
```

**Implémentation :**
- Modification de `argument_component.ui` pour ajouter un `QLabel` (`commandsLabel`)
- Ajout du paramètre `affected_commands: Optional[List[str]]` dans `ArgumentComponent.__init__()`
- Affichage automatique des commandes concernées dans `_setup_ui()`

### 2. Mise à jour en temps réel

Lorsqu'un utilisateur modifie la valeur d'un argument partagé, les champs correspondants dans les commandes sont automatiquement mis à jour en temps réel.

**Comportement :**
1. L'utilisateur saisit une valeur dans un argument partagé (ex: "C:\data\database.db")
2. La valeur est immédiatement propagée à tous les champs d'arguments concernés dans les commandes
3. L'utilisateur voit les changements instantanément sans avoir à cliquer sur un bouton

**Implémentation :**
- Modification de `command_form.py` :
  - `_add_shared_arguments_section()` : Extraction des noms de commandes concernées et passage à `ArgumentComponent`
  - `_refresh_command_displays()` : Implémentation de la logique de mise à jour en temps réel
  - Utilisation de `set_value()` pour mettre à jour les `ArgumentComponent` des commandes

## Fichiers modifiés

### 1. `command_builder/components/argument_component/argument_component.ui`
- Changement du layout principal de `QHBoxLayout` à `QVBoxLayout`
- Ajout d'un `QLabel` nommé `commandsLabel` pour afficher les commandes concernées
- Style : `font-size: 10px; color: #888; font-style: italic;`

### 2. `command_builder/components/argument_component/argument_component.py`
- Ajout de l'import `QLabel` et `List, Optional` de `typing`
- Modification du constructeur `__init__()` :
  - Nouveau paramètre : `affected_commands: Optional[List[str]] = None`
  - Stockage de `self.affected_commands`
- Modification de `_load_ui()` :
  - Récupération du widget `commandsLabel`
- Modification de `_setup_ui()` :
  - Affichage des commandes concernées si `affected_commands` n'est pas vide
  - Masquage du label si aucune commande n'est concernée

### 3. `command_builder/components/command_form/command_form.py`
- Modification de `_add_shared_arguments_section()` :
  - Extraction des noms de commandes concernées depuis `task_arg.values`
  - Passage de `affected_commands` au constructeur `ArgumentComponent`
  - Activation du bouton de parcours pour les types "file" et "directory"
- Modification de `_refresh_command_displays()` :
  - Implémentation complète de la logique de mise à jour en temps réel
  - Parcours des arguments partagés modifiés
  - Recherche des `CommandComponent` et `ArgumentComponent` correspondants
  - Mise à jour des valeurs via `set_value()`

### 4. `command_builder/tests/components/test_argument_component.py`
- Ajout de l'import `QLabel`
- Nouvelle classe de tests : `TestArgumentComponentAffectedCommands`
  - Test d'initialisation avec des commandes concernées
  - Test d'initialisation sans commandes concernées

## Tests

Tous les tests unitaires existants passent avec succès. Les nouveaux tests vérifient :
- L'initialisation correcte du composant avec et sans commandes concernées
- Le stockage correct de la liste `affected_commands`

## Utilisation

### Pour les développeurs

```python
# Créer un ArgumentComponent avec des commandes concernées
affected_commands = ["command1", "command2"]
arg_component = ArgumentComponent(
    argument=my_argument,
    affected_commands=affected_commands
)

# Le label affichera automatiquement :
# "Utilisé par : command1, command2"
```

### Pour les utilisateurs

1. Ouvrez une tâche avec des arguments partagés
2. Remplissez un argument partagé (ex: "Base de données")
3. Observez :
   - Les noms des commandes concernées sous le champ
   - La mise à jour automatique des champs correspondants dans les commandes ci-dessous

## Rétrocompatibilité

Les modifications sont entièrement rétrocompatibles :
- Le paramètre `affected_commands` est optionnel (valeur par défaut : `None`)
- Si aucune commande n'est fournie, le comportement est identique à l'ancienne version
- Les tests existants continuent de fonctionner sans modification

## Améliorations futures possibles

1. **Coloration des champs synchronisés** : Mettre en évidence visuellement les champs qui sont liés à un argument partagé
2. **Indicateur de synchronisation** : Ajouter une icône pour indiquer qu'un champ est contrôlé par un argument partagé
3. **Validation croisée** : Vérifier que les valeurs partagées sont valides pour toutes les commandes concernées
4. **Historique des valeurs** : Mémoriser les dernières valeurs utilisées pour chaque argument partagé
