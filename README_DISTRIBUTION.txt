================================================================================
                         CommandBuilder v0.2.0
        Assistant GUI pour composer des commandes CLI Windows
================================================================================

CONTENU DE CE DOSSIER
----------------------

CommandBuilder_0.2.0.exe    Interface graphique principale
data/                       Définitions des commandes et tâches
  ├── commands/             Commandes individuelles (YAML)
  └── tasks/                Tâches (groupes de commandes)


PRÉREQUIS IMPORTANTS
---------------------

⚠️ CommandBuilder est une INTERFACE GRAPHIQUE pour construire des commandes.
   Il NE CONTIENT PAS les outils CLI eux-mêmes.

Les outils suivants doivent être installés et accessibles :
  • tdmsimport.exe
  • csvexport.exe
  • computekey.exe
  • computeprofile.exe
  • computecurve.exe
  • tdmsdirimport.exe
  • tdmsscan.exe
  • csvimport.exe
  • pcapimport.exe
  • streampixImport.exe
  • kmzExport.exe
  • campaignExport.exe
  • spatialiteTest.exe

INSTALLATION
------------

Option A : Outils dans le PATH (recommandé)
  1. Installer les outils CLI sur votre système
  2. Ajouter leur dossier au PATH Windows
  3. Vérifier : ouvrir cmd et taper "tdmsimport --help"
  4. Lancer CommandBuilder_0.2.0.exe

Option B : Dossier tools/ local
  1. Créer un dossier "tools" à côté de l'exe
  2. Copier tous les outils CLI dans ce dossier
  3. Modifier les fichiers YAML dans data/commands/ pour utiliser :
     command: "tools\\tdmsimport.exe {INPUT_FILE} ..."
  4. Lancer CommandBuilder_0.2.0.exe


UTILISATION
-----------

1. Double-cliquer sur CommandBuilder_0.2.0.exe
2. Sélectionner une tâche dans la liste de gauche
3. Remplir les champs obligatoires (marqués *)
4. Cliquer sur "Exécuter"
5. Voir le résultat dans la console en bas


PERSONNALISATION
----------------

Vous pouvez modifier les tâches existantes ou en créer de nouvelles :

• Modifier une tâche :
  1. Ouvrir data/tasks/nom_de_la_tache.yaml
  2. Modifier les paramètres
  3. Sauvegarder
  4. Redémarrer CommandBuilder

• Créer une nouvelle tâche :
  1. Copier un fichier YAML existant dans data/tasks/
  2. Modifier le contenu selon vos besoins
  3. Sauvegarder avec un nouveau nom
  4. Redémarrer CommandBuilder → La nouvelle tâche apparaît !


DÉPANNAGE
---------

Erreur : "commande introuvable" ou "n'est pas reconnu"
→ L'outil CLI n'est pas dans le PATH
→ Solution : Vérifier l'installation des outils ou utiliser un chemin absolu

Erreur : "Veuillez remplir tous les champs obligatoires"
→ Un champ marqué * est vide
→ Solution : Remplir tous les champs obligatoires avant d'exécuter

La tâche n'apparaît pas dans la liste
→ Erreur dans le fichier YAML
→ Solution : Vérifier la syntaxe YAML (indentation, tirets, etc.)


STRUCTURE DES FICHIERS YAML
----------------------------

Voir la documentation complète dans :
https://github.com/votre-repo/CommandBuilder/docs/YAML_SYSTEM.md


SUPPORT
-------

Pour toute question ou problème :
• Consulter la documentation dans le dossier docs/
• Contacter l'équipe de développement


VERSION
-------

CommandBuilder v0.2.0
Dernière mise à jour : Novembre 2025


================================================================================
