"""Fenêtre d'aide avec documentation complète YAML."""

from pathlib import Path

from PySide6 import QtUiTools
from PySide6.QtWidgets import QDialog


class HelpWindow(QDialog):
    """Fenêtre d'aide affichant la documentation YAML complète."""

    # Chemin vers les fichiers HTML de documentation
    HELP_DOCS_DIR = Path(__file__).parent.parent.parent.parent / "docs" / "help"

    def __init__(self, parent=None):
        """Initialise la fenêtre d'aide.

        Args:
            parent: Widget parent
        """
        super().__init__(parent)
        self._load_ui()
        self._load_stylesheet()
        self._connect_signals()
        self._populate_content()

    def _load_ui(self):
        """Charge l'interface depuis le fichier .ui."""
        from PySide6.QtWidgets import QPushButton, QTabWidget, QTextBrowser

        ui_file = Path(__file__).parent / "help_window.ui"
        loader = QtUiTools.QUiLoader()
        ui = loader.load(str(ui_file))

        # Copier les propriétés
        self.setWindowTitle(ui.windowTitle())
        self.resize(ui.size())

        # Récupérer le layout de l'UI chargée et l'appliquer à ce dialog
        ui_layout = ui.layout()
        self.setLayout(ui_layout)

        # Récupérer les widgets
        self.tab_widget = self.findChild(QTabWidget, "tabWidget")
        self.intro_text = self.findChild(QTextBrowser, "introText")
        self.structure_text = self.findChild(QTextBrowser, "structureText")
        self.arguments_text = self.findChild(QTextBrowser, "argumentsText")
        self.shared_text = self.findChild(QTextBrowser, "sharedText")
        self.examples_text = self.findChild(QTextBrowser, "examplesText")
        self.close_button = self.findChild(QPushButton, "closeButton")

    def _load_stylesheet(self):
        """Charge la feuille de style depuis le fichier .qss."""
        qss_file = Path(__file__).parent / "help_window.qss"
        if qss_file.exists():
            with open(qss_file, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def _connect_signals(self):
        """Connecte les signaux des widgets."""
        if self.close_button:
            self.close_button.clicked.connect(self.accept)

    def _populate_content(self):
        """Remplit le contenu de chaque onglet."""
        self._populate_intro()
        self._populate_structure()
        self._populate_arguments()
        self._populate_shared()
        self._populate_examples()

    def _load_html_file(self, filename: str) -> str:
        """Charge un fichier HTML depuis le dossier docs/help.

        Args:
            filename: Nom du fichier HTML (ex: 'intro.html')

        Returns:
            Contenu HTML du fichier ou chaîne vide si non trouvé
        """
        html_path = self.HELP_DOCS_DIR / filename
        if html_path.exists():
            with open(html_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def _populate_intro(self):
        """Remplit l'onglet Introduction."""
        content = self._load_html_file("intro.html")
        if content:
            self.intro_text.setHtml(content)
            return
        # Fallback si le fichier n'existe pas
        content = """
        <h2>📘 Guide YAML - L'essentiel</h2>
        
        <div style="background-color: #e3f2fd; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #2196F3;">
            <h3 style="margin-top: 0;">Principe</h3>
            <p style="font-size: 14px; line-height: 1.6;">
            CommandBuilder utilise deux types de fichiers YAML :<br>
            <b>1. Fichiers de commandes</b> (réutilisables) : définissent une commande CLI<br>
            <b>2. Fichiers de tâches</b> (workflows) : groupent plusieurs commandes à exécuter en séquence
            </p>
        </div>
        
        <h3>📁 Structure des fichiers</h3>
        <div style="background-color: #f5f5f5; padding: 12px; border-radius: 6px; margin: 10px 0; font-size: 13px;">
        <b>Commandes :</b> <code>command_builder/data/commands/ma_commande.yaml</code><br>
        <b>Tâches :</b> <code>command_builder/data/tasks/ma_tache.yaml</code><br>
        <b>Recommandation :</b> <span style="color: #d32f2f; font-weight: bold;">Un fichier = Une commande ou une tâche</span>
        </div>
        
        <h3>🎯 Structure minimale (copier-coller)</h3>
        <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; border-left: 4px solid #4caf50; font-size: 13px;">
<span style="color: #c62828; font-weight: bold;">name:</span> "Ma tâche"
<span style="color: #c62828; font-weight: bold;">description:</span> "Ce que fait cette tâche"
<span style="color: #c62828; font-weight: bold;">commands:</span>
  - <span style="color: #c62828; font-weight: bold;">name:</span> "Commande 1"
    <span style="color: #c62828; font-weight: bold;">description:</span> "Description"
    <span style="color: #c62828; font-weight: bold;">command:</span> "executable.exe {ARG1} {ARG2}"
    <span style="color: #c62828; font-weight: bold;">arguments:</span>
      - <span style="color: #c62828; font-weight: bold;">code:</span> "ARG1"
        <span style="color: #c62828; font-weight: bold;">name:</span> "Nom affiché"
        <span style="color: #c62828; font-weight: bold;">type:</span> "file"
        <span style="color: #c62828; font-weight: bold;">required:</span> 1
</pre>
        
        <h3>⚡ Points clés</h3>
        <table border="0" cellpadding="8" cellspacing="0" style="width: 100%; margin: 10px 0;">
            <tr>
                <td style="background-color: #fff3e0; border-radius: 4px; padding: 10px;">
                    <b>1. Placeholders</b><br>
                    <code>{CODE}</code> dans la commande → remplacé par la valeur saisie
                </td>
            </tr>
            <tr>
                <td style="background-color: #e8f5e9; border-radius: 4px; padding: 10px;">
                    <b>2. Types d'arguments</b><br>
                    <code>string</code> | <code>file</code> | <code>directory</code> | <code>flag</code> | <code>valued_option</code>
                </td>
            </tr>
            <tr>
                <td style="background-color: #e3f2fd; border-radius: 4px; padding: 10px;">
                    <b>3. Required</b><br>
                    <code>required: 1</code> = obligatoire (astérisque rouge)<br>
                    <code>required: 0</code> = optionnel
                </td>
            </tr>
            <tr>
                <td style="background-color: #f3e5f5; border-radius: 4px; padding: 10px;">
                    <b>4. Arguments partagés</b><br>
                    Saisir UNE FOIS une valeur utilisée par PLUSIEURS commandes
                </td>
            </tr>
        </table>
        
        <h3>🖥️ Comprendre l'interface</h3>
        <table border="0" cellpadding="10" cellspacing="0" style="width: 100%; margin: 10px 0;">
            <tr>
                <td style="background-color: #ffebee; border-radius: 4px; width: 50%;">
                    <b style="color: #c62828;">🔴 Astérisque rouge (*)</b><br>
                    <span style="font-size: 13px;">Champ obligatoire (<code>required: 1</code>)<br>
                    Affiché APRÈS le nom : "Base de données : *"</span>
                </td>
                <td style="background-color: #c8e6c9; border-radius: 4px; width: 50%;">
                    <b style="color: #1b5e20;">🟢 Texte vert</b><br>
                    <span style="font-size: 13px;">Valeur pré-remplie (par défaut)<br>
                    Modifiable par l'utilisateur</span>
                </td>
            </tr>
            <tr>
                <td style="background-color: #e3f2fd; border-radius: 4px;">
                    <b style="color: #1565c0;">🔵 Couleur du label</b><br>
                    <span style="font-size: 13px;">Noir = champ vide<br>
                    Bleu = champ rempli</span>
                </td>
                <td style="background-color: #fff3e0; border-radius: 4px;">
                    <b style="color: #f57c00;">📋 Étapes d'exécution</b><br>
                    <span style="font-size: 13px;">Les commandes s'exécutent dans l'ordre<br>
                    Si erreur → arrêt immédiat</span>
                </td>
            </tr>
            <tr>
                <td style="background-color: #e8f5e9; border-radius: 4px;">
                    <b style="color: #2e7d32;">✅ Case à cocher</b><br>
                    <span style="font-size: 13px;">Type <code>flag</code> ou <code>valued_option</code><br>
                    Coché = inclus dans la commande</span>
                </td>
                <td style="background-color: #f3e5f5; border-radius: 4px;">
                    <b style="color: #6a1b9a;">📂 Listes</b><br>
                    <span style="font-size: 13px;">Gauche = tâches disponibles<br>
                    Cliquez pour voir ses commandes</span>
                </td>
            </tr>
        </table>
        
        <h3>📖 Onglets de cette aide</h3>
        <ul style="line-height: 1.6;">
            <li><b>Structure</b> → Templates complets (fichiers, !include)</li>
            <li><b>Arguments</b> → Les 5 types expliqués</li>
            <li><b>Arguments Partagés</b> → Éviter la répétition</li>
            <li><b>Exemples</b> → Cas réels avec !include</li>
        </ul>
        
        <h3>⚡ Points clés supplémentaires</h3>
        <ul style="line-height: 1.6; color: #d32f2f;">
            <li><b>Valeurs par défaut des tâches</b> → Prioritaires sur celles des commandes</li>
            <li><b>!include</b> → Réutilisez les commandes dans plusieurs tâches</li>
            <li><b>Modification post-build</b> → Les fichiers YAML sont modifiables sans recompilation</li>
        </ul>
        """
        self.intro_text.setHtml(content)

    def _populate_structure(self):
        """Remplit l'onglet Structure."""
        content = self._load_html_file("structure.html")
        if content:
            self.structure_text.setHtml(content)
            return
        # Fallback si le fichier n'existe pas
        content = """
        <h2>📐 Référence complète YAML</h2>
        
        <div style="background-color: #e3f2fd; padding: 15px; border-radius: 6px; margin: 15px 0; border-left: 4px solid #2196F3;">
            <h3 style="margin-top: 0;">🎯 Structure d'un fichier de commande</h3>
            <pre style="background-color: #ffffff; padding: 12px; border-radius: 4px; font-size: 12px; margin: 10px 0;">
<span style="color: #c62828; font-weight: bold;">name:</span> "nom_de_la_commande"           <span style="color: #666;"># 🔴 OBLIGATOIRE - Nom affiché</span>
<span style="color: #c62828; font-weight: bold;">description:</span> "Description courte"    <span style="color: #666;"># 🔴 OBLIGATOIRE - Texte explicatif</span>
<span style="color: #c62828; font-weight: bold;">command:</span> "executable {ARG1} {ARG2}"  <span style="color: #666;"># 🔴 OBLIGATOIRE - Commande CLI avec placeholders</span>
<span style="color: #c62828; font-weight: bold;">arguments:</span>                           <span style="color: #666;"># 🔴 OBLIGATOIRE - Liste (peut être vide [])</span>
  - <span style="color: #c62828; font-weight: bold;">code:</span> "ARG1"                     <span style="color: #666;"># 🔴 OBLIGATOIRE - Identifiant unique</span>
    <span style="color: #c62828; font-weight: bold;">name:</span> "Nom affiché"              <span style="color: #666;"># 🔴 OBLIGATOIRE - Label dans l'interface</span>
    <span style="color: #c62828; font-weight: bold;">description:</span> "Texte d'aide"      <span style="color: #666;"># 🟡 OPTIONNEL - Tooltip</span>
    <span style="color: #c62828; font-weight: bold;">type:</span> "string"                   <span style="color: #666;"># 🔴 OBLIGATOIRE - string|file|directory|flag|valued_option</span>
    <span style="color: #c62828; font-weight: bold;">required:</span> 1                      <span style="color: #666;"># 🔴 OBLIGATOIRE - 0 ou 1</span>
    <span style="color: #1565c0;">default:</span> "valeur_par_defaut"      <span style="color: #666;"># 🟡 OPTIONNEL - Valeur pré-remplie</span>
    <span style="color: #1565c0;">value:</span> "--flag"                   <span style="color: #666;"># 🟠 OBLIGATOIRE pour type "flag"</span>
    <span style="color: #1565c0;">validation:</span>                       <span style="color: #666;"># 🟡 OPTIONNEL - Pour type "file"</span>
      file_extensions: [".csv", ".txt"]  <span style="color: #666;"># Liste des extensions acceptées</span>
</pre>
        </div>
        
        <div style="background-color: #e8f5e9; padding: 15px; border-radius: 6px; margin: 15px 0; border-left: 4px solid #4caf50;">
            <h3 style="margin-top: 0;">🎯 Structure d'un fichier de tâche</h3>
            <pre style="background-color: #ffffff; padding: 12px; border-radius: 4px; font-size: 12px; margin: 10px 0;">
<span style="color: #c62828; font-weight: bold;">name:</span> "nom_de_la_tache"            <span style="color: #666;"># 🔴 OBLIGATOIRE - Nom affiché</span>
<span style="color: #c62828; font-weight: bold;">description:</span> "Description"          <span style="color: #666;"># 🔴 OBLIGATOIRE - Texte explicatif</span>

<span style="color: #1565c0;">arguments:</span>                          <span style="color: #666;"># 🟡 OPTIONNEL - Arguments partagés entre commandes</span>
  - <span style="color: #c62828; font-weight: bold;">code:</span> "SHARED_ARG"              <span style="color: #666;"># Même structure qu'un argument normal</span>
    <span style="color: #c62828; font-weight: bold;">name:</span> "Argument partagé"
    <span style="color: #c62828; font-weight: bold;">type:</span> "string"
    <span style="color: #c62828; font-weight: bold;">required:</span> 1
    <span style="color: #1565c0;">values:</span>                          <span style="color: #666;"># 🔴 OBLIGATOIRE si arguments partagés</span>
    - <span style="color: #c62828; font-weight: bold;">command:</span> "nom_commande1"      <span style="color: #666;"># Nom de la commande cible</span>
      <span style="color: #c62828; font-weight: bold;">argument:</span> "ARG_DANS_CMD1"     <span style="color: #666;"># Code de l'argument dans cette commande</span>
    - <span style="color: #c62828; font-weight: bold;">command:</span> "nom_commande2"
      <span style="color: #c62828; font-weight: bold;">argument:</span> "ARG_DANS_CMD2"

<span style="color: #c62828; font-weight: bold;">commands:</span>                           <span style="color: #666;"># 🔴 OBLIGATOIRE - Liste des commandes</span>
  - <span style="color: #9c27b0; font-weight: bold;">!include</span> ../commands/cmd1.yaml  <span style="color: #666;"># Méthode 1 : Inclusion (RECOMMANDÉ)</span>
  - <span style="color: #9c27b0; font-weight: bold;">!include</span> ../commands/cmd2.yaml
  
  - <span style="color: #c62828; font-weight: bold;">name:</span> "Commande inline"         <span style="color: #666;"># Méthode 2 : Définition directe</span>
    <span style="color: #c62828; font-weight: bold;">description:</span> "Description"
    <span style="color: #c62828; font-weight: bold;">command:</span> "echo test"
    <span style="color: #c62828; font-weight: bold;">arguments:</span> []
</pre>
        </div>
        
        <div style="background-color: #fff3e0; padding: 12px; border-radius: 6px; margin: 15px 0; border-left: 4px solid #ff9800;">
            <h3 style="margin-top: 0;">📝 Règles importantes</h3>
            <ul style="line-height: 1.8; margin: 5px 0;">
                <li><b>Indentation :</b> 2 espaces (pas de tabulations)</li>
                <li><b>Placeholders :</b> <code>{CODE}</code> en MAJUSCULES dans la commande</li>
                <li><b>Chemins relatifs :</b> <code>../commands/</code> depuis <code>tasks/</code></li>
                <li><b>Extensions :</b> <code>.yaml</code> ou <code>.yml</code> (les deux fonctionnent)</li>
                <li><b>Commentaires :</b> <code># Texte</code> (ignoré par le parser)</li>
                <li><b>Guillemets :</b> Obligatoires pour les chaînes avec espaces ou caractères spéciaux</li>
            </ul>
        </div>
        
        <h2>📐 Templates prêts à copier</h2>
        
        <div style="background-color: #fff3e0; padding: 12px; border-radius: 6px; margin: 15px 0; border-left: 4px solid #ff9800;">
            <b>💡 Bonne pratique :</b> Créez <b>un fichier par commande</b> dans <code>data/commands/</code>,<br>
            puis <b>réutilisez-les</b> dans les tâches avec <code>!include</code>
        </div>
        
        <h3>Template 1 : Fichier de commande (réutilisable)</h3>
        <p style="color: #666; font-size: 13px;"><b>Fichier :</b> <code>data/commands/ma_commande.yaml</code></p>
        <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; border-left: 4px solid #4caf50;">
<span style="color: #c62828; font-weight: bold;">name:</span> "Ma commande"
<span style="color: #c62828; font-weight: bold;">description:</span> "Description de la commande"
<span style="color: #c62828; font-weight: bold;">command:</span> "executable.exe {ARG1} {ARG2}"
<span style="color: #c62828; font-weight: bold;">arguments:</span>
  - <span style="color: #c62828; font-weight: bold;">code:</span> "ARG1"
    <span style="color: #c62828; font-weight: bold;">name:</span> "Argument 1"
    <span style="color: #c62828; font-weight: bold;">type:</span> "file"
    <span style="color: #c62828; font-weight: bold;">required:</span> 1
        </pre>
        <p style="color: #666; font-size: 13px;">✅ Cette commande peut être incluse dans plusieurs tâches</p>
        
        <h3>Template 2 : Tâche simple (minimum requis)</h3>
        <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; border-left: 4px solid #c62828;">
<span style="color: #c62828; font-weight: bold;">name:</span> "Ma tâche"
<span style="color: #c62828; font-weight: bold;">description:</span> "Description de la tâche"
<span style="color: #c62828; font-weight: bold;">commands:</span>
  - <span style="color: #c62828; font-weight: bold;">name:</span> "Ma commande"
    <span style="color: #c62828; font-weight: bold;">description:</span> "Description de la commande"
    <span style="color: #c62828; font-weight: bold;">command:</span> "echo Hello World"
    <span style="color: #c62828; font-weight: bold;">arguments:</span> []
        </pre>
        <p style="color: #666; font-size: 13px;">✅ Tous les champs en rouge sont obligatoires</p>
        
        <h3>Template 3 : Tâche avec inclusion de commandes</h3>
        <p style="color: #666; font-size: 13px;"><b>Fichier :</b> <code>data/tasks/ma_tache.yaml</code></p>
        <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; border-left: 4px solid #9c27b0;">
<span style="color: #c62828; font-weight: bold;">name:</span> "Ma tâche"
<span style="color: #c62828; font-weight: bold;">description:</span> "Exécute plusieurs commandes"
<span style="color: #c62828; font-weight: bold;">commands:</span>
  - <span style="color: #9c27b0; font-weight: bold;">!include</span> ../commands/ma_commande.yaml
  - <span style="color: #9c27b0; font-weight: bold;">!include</span> ../commands/autre_commande.yaml
        </pre>
        <p style="color: #666; font-size: 13px;">
        ✅ <code>!include</code> charge le fichier de commande<br>
        ✅ Les chemins sont relatifs au fichier YAML<br>
        ✅ <code>../commands/</code> remonte d'un niveau (de tasks vers data)
        </p>
        
        <h3>Template 4 : Commande avec arguments</h3>
        <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; border-left: 4px solid #1565c0;">
<span style="color: #c62828; font-weight: bold;">name:</span> "Traitement de fichier"
<span style="color: #c62828; font-weight: bold;">description:</span> "Traite un fichier CSV"
<span style="color: #c62828; font-weight: bold;">commands:</span>
  - <span style="color: #c62828; font-weight: bold;">name:</span> "Process"
    <span style="color: #c62828; font-weight: bold;">description:</span> "Traite le fichier"
    <span style="color: #c62828; font-weight: bold;">command:</span> "process.exe {INPUT_FILE} {OUTPUT_FILE}"
    <span style="color: #c62828; font-weight: bold;">arguments:</span>
      - <span style="color: #c62828; font-weight: bold;">code:</span> "INPUT_FILE"
        <span style="color: #c62828; font-weight: bold;">name:</span> "Fichier d'entrée"
        <span style="color: #c62828; font-weight: bold;">type:</span> "file"
        <span style="color: #c62828; font-weight: bold;">required:</span> 1
      
      - <span style="color: #c62828; font-weight: bold;">code:</span> "OUTPUT_FILE"
        <span style="color: #c62828; font-weight: bold;">name:</span> "Fichier de sortie"
        <span style="color: #c62828; font-weight: bold;">type:</span> "file"
        <span style="color: #c62828; font-weight: bold;">required:</span> 0
        <span style="color: #1565c0;">default:</span> "output.csv"
        </pre>
        <p style="color: #666; font-size: 13px;">💡 <code>{INPUT_FILE}</code> et <code>{OUTPUT_FILE}</code> sont remplacés par les valeurs saisies</p>
        
        <h3>Template 5 : Avec flags et options</h3>
        <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; border-left: 4px solid #1565c0;">
<span style="color: #c62828; font-weight: bold;">name:</span> "Traitement avancé"
<span style="color: #c62828; font-weight: bold;">description:</span> "Avec options CLI"
<span style="color: #c62828; font-weight: bold;">commands:</span>
  - <span style="color: #c62828; font-weight: bold;">name:</span> "Process"
    <span style="color: #c62828; font-weight: bold;">description:</span> "Traite avec options"
    <span style="color: #c62828; font-weight: bold;">command:</span> "process {INPUT} {DEBUG} --log-level {LOG_LEVEL}"
    <span style="color: #c62828; font-weight: bold;">arguments:</span>
      # Fichier obligatoire
      - <span style="color: #c62828; font-weight: bold;">code:</span> "INPUT"
        <span style="color: #c62828; font-weight: bold;">name:</span> "Fichier"
        <span style="color: #c62828; font-weight: bold;">type:</span> "file"
        <span style="color: #c62828; font-weight: bold;">required:</span> 1
      
      # Flag (checkbox seule)
      - <span style="color: #c62828; font-weight: bold;">code:</span> "DEBUG"
        <span style="color: #c62828; font-weight: bold;">name:</span> "Mode debug"
        <span style="color: #c62828; font-weight: bold;">type:</span> "flag"
        <span style="color: #c62828; font-weight: bold;">required:</span> 0
        <span style="color: #c62828; font-weight: bold;">value:</span> "--debug"
      
      # Option avec valeur (checkbox + champ)
      - <span style="color: #c62828; font-weight: bold;">code:</span> "LOG_LEVEL"
        <span style="color: #c62828; font-weight: bold;">name:</span> "Niveau de log"
        <span style="color: #c62828; font-weight: bold;">type:</span> "valued_option"
        <span style="color: #c62828; font-weight: bold;">required:</span> 0
        <span style="color: #1565c0;">default:</span> "INFO"
        </pre>
        <p style="color: #666; font-size: 13px;">⚠️ Pour les <code>flag</code> : le champ <code>value</code> est obligatoire</p>
        
        <h3>Template 6 : Avec arguments partagés</h3>
        <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; border-left: 4px solid #1565c0;">
<span style="color: #c62828; font-weight: bold;">name:</span> "Pipeline"
<span style="color: #c62828; font-weight: bold;">description:</span> "Plusieurs commandes avec argument commun"
<span style="color: #1565c0;">shared_arguments:</span>
  - <span style="color: #c62828; font-weight: bold;">code:</span> "DATABASE"
    <span style="color: #c62828; font-weight: bold;">name:</span> "Base de données"
    <span style="color: #c62828; font-weight: bold;">type:</span> "file"
    <span style="color: #c62828; font-weight: bold;">required:</span> 1

<span style="color: #c62828; font-weight: bold;">commands:</span>
  - <span style="color: #c62828; font-weight: bold;">name:</span> "Import"
    <span style="color: #c62828; font-weight: bold;">description:</span> "Importe les données"
    <span style="color: #c62828; font-weight: bold;">command:</span> "import.exe --db {DATABASE}"
    <span style="color: #c62828; font-weight: bold;">arguments:</span> []
  
  - <span style="color: #c62828; font-weight: bold;">name:</span> "Export"
    <span style="color: #c62828; font-weight: bold;">description:</span> "Exporte les données"
    <span style="color: #c62828; font-weight: bold;">command:</span> "export.exe --db {DATABASE}"
    <span style="color: #c62828; font-weight: bold;">arguments:</span> []
        </pre>
        <p style="color: #666; font-size: 13px;">💡 L'argument DATABASE est saisi une seule fois et utilisé par toutes les commandes</p>
        
        <h3>Template 7 : Construction de chemins</h3>
        <div style="background-color: #e3f2fd; padding: 12px; border-radius: 6px; margin: 10px 0; border-left: 4px solid #2196F3;">
            <b>💡 Astuce avancée :</b> Vous pouvez combiner plusieurs placeholders pour construire des chemins
        </div>
        <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; border-left: 4px solid #1565c0;">
<span style="color: #c62828; font-weight: bold;">name:</span> "campaignexport"
<span style="color: #c62828; font-weight: bold;">description:</span> "Export avec construction de chemin"
<span style="color: #c62828; font-weight: bold;">command:</span> "campaignexport {DATABASE_FILE}\\{PROJECT_NAME}.sqlite {OUTPUT_DIR}"
<span style="color: #c62828; font-weight: bold;">arguments:</span>
  - <span style="color: #c62828; font-weight: bold;">code:</span> "DATABASE_FILE"
    <span style="color: #c62828; font-weight: bold;">name:</span> "Répertoire de base"
    <span style="color: #c62828; font-weight: bold;">type:</span> "directory"
    <span style="color: #c62828; font-weight: bold;">required:</span> 1
  
  - <span style="color: #c62828; font-weight: bold;">code:</span> "PROJECT_NAME"
    <span style="color: #c62828; font-weight: bold;">name:</span> "Nom du projet"
    <span style="color: #c62828; font-weight: bold;">type:</span> "string"
    <span style="color: #c62828; font-weight: bold;">required:</span> 1
  
  - <span style="color: #c62828; font-weight: bold;">code:</span> "OUTPUT_DIR"
    <span style="color: #c62828; font-weight: bold;">name:</span> "Dossier de sortie"
    <span style="color: #c62828; font-weight: bold;">type:</span> "directory"
    <span style="color: #c62828; font-weight: bold;">required:</span> 1
        </pre>
        <div style="background-color: #e8f5e9; padding: 10px; border-radius: 4px; margin: 10px 0;">
        <b>Résultat :</b><br>
        Si <code>DATABASE_FILE = L:\PROJET\BASE</code> et <code>PROJECT_NAME = I2_S38</code><br>
        → Commande générée : <code>campaignexport L:\PROJET\BASE\I2_S38.sqlite L:\OUTPUT</code>
        </div>
        <p style="color: #666; font-size: 13px;">
        ✅ Utilisez <code>\\</code> pour Windows ou <code>/</code> pour Linux<br>
        ✅ Vous pouvez combiner autant de placeholders que nécessaire
        </p>
        """
        self.structure_text.setHtml(content)

    def _populate_arguments(self):
        """Remplit l'onglet Arguments."""
        content = self._load_html_file("arguments.html")
        if content:
            self.arguments_text.setHtml(content)
            return
        # Fallback si le fichier n'existe pas
        content = """
        <h2>🔧 Les 5 types d'arguments</h2>
        
        <div style="background-color: #fff3e0; padding: 12px; border-radius: 6px; margin: 10px 0; border-left: 4px solid #ff9800;">
            <b>💡 Principe :</b> Le <code>code</code> est utilisé dans la commande avec <code>{CODE}</code> et sera remplacé par la valeur saisie
        </div>
        
        <h3>1️⃣ Type "string" - Texte libre</h3>
        <pre style="background-color: #f5f5f5; padding: 12px; border-radius: 4px; font-size: 13px; border-left: 3px solid #4caf50;">
- <span style="color: #c62828;">code:</span> "TABLE_NAME"
  <span style="color: #c62828;">name:</span> "Nom de la table"
  <span style="color: #c62828;">type:</span> "string"
  <span style="color: #c62828;">required:</span> 0
  <span style="color: #1565c0;">default:</span> "MyTable"</pre>
        <p style="margin: 5px 0 15px 0; color: #666;"><b>Interface :</b> Champ de texte simple</p>
        
        <h3>2️⃣ Type "file" - Sélection de fichier</h3>
        <pre style="background-color: #f5f5f5; padding: 12px; border-radius: 4px; font-size: 13px; border-left: 3px solid #4caf50;">
- <span style="color: #c62828;">code:</span> "INPUT_FILE"
  <span style="color: #c62828;">name:</span> "Fichier d'entrée"
  <span style="color: #c62828;">type:</span> "file"
  <span style="color: #c62828;">required:</span> 1
  <span style="color: #1565c0;">validation:</span>
    file_extensions: [".csv", ".txt"]</pre>
        <p style="margin: 5px 0 15px 0; color: #666;"><b>Interface :</b> Champ + bouton "Parcourir"</p>
        
        <h3>3️⃣ Type "directory" - Sélection de dossier</h3>
        <pre style="background-color: #f5f5f5; padding: 12px; border-radius: 4px; font-size: 13px; border-left: 3px solid #4caf50;">
- <span style="color: #c62828;">code:</span> "OUTPUT_DIR"
  <span style="color: #c62828;">name:</span> "Dossier de sortie"
  <span style="color: #c62828;">type:</span> "directory"
  <span style="color: #c62828;">required:</span> 0</pre>
        <p style="margin: 5px 0 15px 0; color: #666;"><b>Interface :</b> Champ + bouton "Parcourir" (dossiers)</p>
        
        <h3>4️⃣ Type "flag" - Case à cocher (--debug, -v)</h3>
        <pre style="background-color: #f5f5f5; padding: 12px; border-radius: 4px; font-size: 13px; border-left: 3px solid #2196f3;">
- <span style="color: #c62828;">code:</span> "DEBUG"
  <span style="color: #c62828;">name:</span> "Mode debug"
  <span style="color: #c62828;">type:</span> "flag"
  <span style="color: #c62828;">required:</span> 0
  <span style="color: #c62828;">value:</span> "--debug"  <span style="color: #666;"># ⚠️ OBLIGATOIRE pour flag</span></pre>
        <p style="margin: 5px 0 15px 0; color: #666;">
        <b>Interface :</b> Case à cocher seule<br>
        <b>Comportement :</b> Coché → insère <code>--debug</code> | Décoché → supprimé
        </p>
        
        <h3>5️⃣ Type "valued_option" - Case + champ (--log-level INFO)</h3>
        <pre style="background-color: #f5f5f5; padding: 12px; border-radius: 4px; font-size: 13px; border-left: 3px solid #2196f3;">
- <span style="color: #c62828;">code:</span> "LOG_LEVEL"
  <span style="color: #c62828;">name:</span> "Niveau de log"
  <span style="color: #c62828;">type:</span> "valued_option"
  <span style="color: #c62828;">required:</span> 0
  <span style="color: #1565c0;">default:</span> "INFO"</pre>
        <p style="margin: 5px 0 15px 0; color: #666;">
        <b>Interface :</b> Case à cocher + champ de saisie<br>
        <b>Comportement :</b> Coché + rempli → insère la valeur | Décoché ou vide → supprimé
        </p>
        
        <hr style="margin: 20px 0; border: none; border-top: 2px solid #e0e0e0;">
        
        <h3>📋 Champs disponibles (résumé)</h3>
        <table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse; width: 100%; font-size: 13px;">
            <tr style="background-color: #e3f2fd;">
                <th style="width: 25%;">Champ</th>
                <th style="width: 15%;">Obligatoire</th>
                <th>Description</th>
            </tr>
            <tr>
                <td><code>code</code></td>
                <td style="background-color: #ffebee;">🔴 OUI</td>
                <td>Identifiant (MAJUSCULES recommandé)</td>
            </tr>
            <tr>
                <td><code>name</code></td>
                <td style="background-color: #ffebee;">🔴 OUI</td>
                <td>Label affiché dans l'interface</td>
            </tr>
            <tr>
                <td><code>type</code></td>
                <td style="background-color: #ffebee;">🔴 OUI</td>
                <td>string | file | directory | flag | valued_option</td>
            </tr>
            <tr>
                <td><code>required</code></td>
                <td style="background-color: #ffebee;">🔴 OUI</td>
                <td>0 = optionnel | 1 = obligatoire (astérisque rouge)</td>
            </tr>
            <tr>
                <td><code>default</code></td>
                <td style="background-color: #e3f2fd;">🔵 Non</td>
                <td>Valeur pré-remplie</td>
            </tr>
            <tr>
                <td><code>value</code></td>
                <td style="background-color: #ffebee;">🔴 Pour flag</td>
                <td>Valeur insérée si coché (ex: "--debug")</td>
            </tr>
            <tr>
                <td><code>validation</code></td>
                <td style="background-color: #e3f2fd;">🔵 Non</td>
                <td>Extensions de fichiers autorisées</td>
            </tr>
        </table>
        
        <div style="background-color: #ffebee; padding: 12px; border-radius: 6px; margin: 15px 0; border-left: 4px solid #f44336;">
            <b>⚠️ Règles importantes :</b>
            <ul style="margin: 5px 0; padding-left: 20px;">
                <li><code>flag</code> et <code>valued_option</code> → toujours <code>required: 0</code></li>
                <li><code>flag</code> → le champ <code>value</code> est OBLIGATOIRE</li>
                <li>Placeholders vides → automatiquement supprimés de la commande finale</li>
                <li><code>default</code> dans la tâche → <b>prioritaire</b> sur celui de la commande</li>
                <li>Les valeurs préremplies s'affichent en <span style="color: #2e7d32; font-weight: bold;">vert</span></li>
            </ul>
        </div>
        """
        self.arguments_text.setHtml(content)

    def _populate_shared(self):
        """Remplit l'onglet Arguments Partagés."""
        content = self._load_html_file("shared.html")
        if content:
            self.shared_text.setHtml(content)
            return
        # Fallback si le fichier n'existe pas
        content = r"""
        <h2>🔗 Arguments partagés entre commandes</h2>
        
        <div style="background-color: #e8f5e9; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #4caf50;">
            <h3 style="margin-top: 0;">💡 Pourquoi utiliser des arguments partagés ?</h3>
            <p style="font-size: 14px; line-height: 1.6;">
            Quand plusieurs commandes utilisent <b>la même valeur</b> (ex: répertoire de base, fichier de sortie),<br>
            → <b>Définir une seule fois</b> au niveau de la tâche<br>
            → L'utilisateur saisit <b>une seule fois</b> ✅<br>
            → La valeur est <b>automatiquement injectée</b> dans les commandes concernées<br>
            → Les valeurs par défaut de la tâche <b>remplacent</b> celles des commandes
            </p>
        </div>
        
        <h3>📝 Syntaxe : Section <code>arguments</code> avec <code>values</code></h3>
        <div style="background-color: #fff3e0; padding: 12px; border-radius: 6px; margin: 10px 0; border-left: 4px solid #ff9800;">
            <b>⚠️ IMPORTANT :</b> La section s'appelle <code>arguments</code> (pas <code>shared_arguments</code>)<br>
            Chaque argument contient une liste <code>values</code> qui indique où l'injecter.
        </div>
        
        <h3>🎯 Exemple réel : Traitement de campagne</h3>
        <p style="color: #666; font-size: 13px;">Cas d'usage : Import TDMS vers une base, puis export de cette base vers TXT/Images</p>
        <pre style="background-color: #f5f5f5; padding: 12px; border-radius: 4px; font-size: 12px; border-left: 3px solid #9C27B0;">
<span style="color: #c62828; font-weight: bold;">name:</span> "Traitement campagne"
<span style="color: #c62828; font-weight: bold;">description:</span> "Import TDMS du dossier + export campagne (TXT + IMAGES)"

<span style="color: #1565c0; font-weight: bold;">arguments:</span>  <span style="color: #666;"># ← Arguments partagés de la tâche</span>
  - <span style="color: #c62828;">code:</span> "base"  <span style="color: #666;"># ← Code de l'argument partagé</span>
    <span style="color: #c62828;">name:</span> "Répertoire de base"
    <span style="color: #c62828;">description:</span> "Répertoire contenant la base de données"
    <span style="color: #c62828;">type:</span> "directory"
    <span style="color: #c62828;">required:</span> 1
    <span style="color: #1565c0;">default:</span> "L:\\PROJET\\BASE"
    <span style="color: #1565c0; font-weight: bold;">values:</span>  <span style="color: #666;"># ← Liste des injections</span>
      - <span style="color: #c62828;">command:</span> "tdmsdirimport_tc"  <span style="color: #666;"># ← Nom de la commande</span>
        <span style="color: #c62828;">argument:</span> "OUTPUT_DIR"       <span style="color: #666;"># ← Code de l'argument cible</span>
      - <span style="color: #c62828;">command:</span> "campaignexport"
        <span style="color: #c62828;">argument:</span> "DATABASE_FILE"    <span style="color: #666;"># ← Injecté ici aussi</span>

<span style="color: #c62828; font-weight: bold;">commands:</span>
  - !include ../commands/tdmsdirimport_commands.yaml
  - !include ../commands/campaignexport_commands.yaml
</pre>
        
        <div style="background-color: #e3f2fd; padding: 12px; border-radius: 6px; margin: 15px 0; border-left: 4px solid #2196F3;">
            <b>🔍 Comment ça fonctionne :</b>
            <ol style="margin: 5px 0; padding-left: 20px; line-height: 1.8;">
                <li>L'utilisateur saisit <b>une seule fois</b> le répertoire de base : <code>L:\PROJET\BASE</code></li>
                <li>Cette valeur est injectée dans <code>OUTPUT_DIR</code> de <code>tdmsdirimport_tc</code></li>
                <li>Cette même valeur est injectée dans <code>DATABASE_FILE</code> de <code>campaignexport</code></li>
                <li>Résultat : <b>cohérence garantie</b> entre les deux commandes ✅</li>
            </ol>
        </div>
        
        <h3>🔄 Cas avec plusieurs arguments partagés</h3>
        <pre style="background-color: #f5f5f5; padding: 12px; border-radius: 4px; font-size: 12px; border-left: 3px solid #9C27B0;">
<span style="color: #1565c0;">arguments:</span>
  - <span style="color: #c62828;">code:</span> "projet"  <span style="color: #666;"># ← Argument partagé 1</span>
    <span style="color: #c62828;">name:</span> "Nom du projet"
    <span style="color: #c62828;">type:</span> "string"
    <span style="color: #c62828;">required:</span> 1
    <span style="color: #1565c0;">default:</span> "E3D_S29"
    <span style="color: #1565c0;">values:</span>
      - <span style="color: #c62828;">command:</span> "tdmsdirimport_tc"
        <span style="color: #c62828;">argument:</span> "PNAME"
      - <span style="color: #c62828;">command:</span> "campaignexport"
        <span style="color: #c62828;">argument:</span> "PROJECT_NAME"
  
  - <span style="color: #c62828;">code:</span> "base_dir"  <span style="color: #666;"># ← Argument partagé 2</span>
    <span style="color: #c62828;">name:</span> "Répertoire de base"
    <span style="color: #c62828;">type:</span> "directory"
    <span style="color: #c62828;">required:</span> 1
    <span style="color: #1565c0;">values:</span>
      - <span style="color: #c62828;">command:</span> "tdmsdirimport_tc"
        <span style="color: #c62828;">argument:</span> "OUTPUT_DIR"
      - <span style="color: #c62828;">command:</span> "campaignexport"
        <span style="color: #c62828;">argument:</span> "DATABASE_FILE"
</pre>
        
        <h3>🔀 Combinaison : Arguments partagés + Arguments locaux</h3>
        <p style="color: #666; font-size: 13px;">Les commandes peuvent avoir leurs propres arguments EN PLUS des arguments partagés :</p>
        <pre style="background-color: #f5f5f5; padding: 12px; border-radius: 4px; font-size: 12px; border-left: 3px solid #9C27B0;">
<span style="color: #1565c0;">arguments:</span>  <span style="color: #666;"># ← Partagés (niveau tâche)</span>
  - <span style="color: #c62828;">code:</span> "base"
    <span style="color: #c62828;">name:</span> "Base de données"
    <span style="color: #c62828;">type:</span> "directory"
    <span style="color: #c62828;">required:</span> 1
    <span style="color: #1565c0;">values:</span>
      - <span style="color: #c62828;">command:</span> "export_cmd"
        <span style="color: #c62828;">argument:</span> "DATABASE"

<span style="color: #c62828;">commands:</span>
  - <span style="color: #c62828;">name:</span> "export_cmd"
    <span style="color: #c62828;">command:</span> "export.exe {DATABASE} {FORMAT}"
    <span style="color: #c62828;">arguments:</span>  <span style="color: #666;"># ← Locaux (spécifiques à cette commande)</span>
      - <span style="color: #c62828;">code:</span> "FORMAT"
        <span style="color: #c62828;">name:</span> "Format de sortie"
        <span style="color: #c62828;">type:</span> "string"
        <span style="color: #c62828;">required:</span> 0
        <span style="color: #1565c0;">default:</span> "CSV"
</pre>
        <p style="color: #666; margin: 5px 0;">
        ✅ <code>DATABASE</code> = partagé (saisi une fois, utilisé partout)<br>
        ✅ <code>FORMAT</code> = local (spécifique à la commande export_cmd)
        </p>
        
        <div style="background-color: #ffebee; padding: 12px; border-radius: 6px; margin: 15px 0; border-left: 4px solid #f44336;">
            <b>⚠️ Règles importantes :</b>
            <ul style="margin: 5px 0; padding-left: 20px;">
                <li>Section <code>arguments</code> (pas <code>shared_arguments</code>)</li>
                <li>Chaque argument doit avoir une liste <code>values</code></li>
                <li>Dans <code>values</code> : <code>command</code> = nom de la commande, <code>argument</code> = code de l'argument cible</li>
                <li>Les valeurs <code>default</code> de la tâche <b>remplacent</b> celles des commandes</li>
                <li>Un argument partagé peut être injecté dans <b>plusieurs commandes</b></li>
            </ul>
        </div>
        """
        self.shared_text.setHtml(content)

    def _populate_validation(self):
        """Remplit l'onglet Validation (non utilisé actuellement)."""
        # Onglet supprimé pour simplifier l'aide
        pass

    def _populate_examples(self):
        """Remplit l'onglet Exemples Complets."""
        content = self._load_html_file("examples.html")
        if content:
            self.examples_text.setHtml(content)
            return
        # Fallback si le fichier n'existe pas
        content = r"""
        <h2>📚 Exemples réels de votre projet</h2>
        
        <h3>1️⃣ Commande avec construction de chemin : campaignexport</h3>
        <p style="color: #666; font-size: 13px;">Fichier : <code>data/commands/campaignexport_commands.yaml</code></p>
        <pre style="background-color: #f5f5f5; padding: 12px; border-radius: 4px; font-size: 12px; border-left: 3px solid #00BCD4;">
<span style="color: #c62828;">name:</span> "campaignexport"
<span style="color: #c62828;">description:</span> "Exporte les tables SQLite en fichiers texte + images"
<span style="color: #c62828;">command:</span> "campaignexport {DATABASE_FILE}\\{PROJECT_NAME}.sqlite {TXT_OUTPUT_DIRECTORY} {IMG_OUTPUT_DIRECTORY} > {LOG_FILE}"
<span style="color: #c62828;">arguments:</span>
  - <span style="color: #c62828;">code:</span> "PROJECT_NAME"
    <span style="color: #c62828;">name:</span> "Nom de la base"
    <span style="color: #c62828;">type:</span> "string"
    <span style="color: #c62828;">required:</span> 1
    <span style="color: #1565c0;">default:</span> "E3D_S29"
  
  - <span style="color: #c62828;">code:</span> "DATABASE_FILE"
    <span style="color: #c62828;">name:</span> "Répertoire de base"
    <span style="color: #c62828;">type:</span> "directory"
    <span style="color: #c62828;">required:</span> 1
    <span style="color: #1565c0;">default:</span> "L:\\PROJET\\BASE"
  
  - <span style="color: #c62828;">code:</span> "TXT_OUTPUT_DIRECTORY"
    <span style="color: #c62828;">name:</span> "Répertoire texte"
    <span style="color: #c62828;">type:</span> "directory"
    <span style="color: #c62828;">required:</span> 1
    <span style="color: #1565c0;">default:</span> "L:\\PROJET\\TXT"
  
  - <span style="color: #c62828;">code:</span> "IMG_OUTPUT_DIRECTORY"
    <span style="color: #c62828;">name:</span> "Répertoire images"
    <span style="color: #c62828;">type:</span> "directory"
    <span style="color: #c62828;">required:</span> 1
    <span style="color: #1565c0;">default:</span> "L:\\PROJET\\IMG"
  
  - <span style="color: #c62828;">code:</span> "LOG_FILE"
    <span style="color: #c62828;">name:</span> "Fichier de log"
    <span style="color: #c62828;">type:</span> "string"
    <span style="color: #c62828;">required:</span> 1
    <span style="color: #1565c0;">default:</span> "log_campaignexport.txt"
</pre>
        <div style="background-color: #fff3e0; padding: 10px; border-radius: 4px; margin: 10px 0; border-left: 3px solid #ff9800;">
        <b>💡 Construction de chemin :</b> <code>{DATABASE_FILE}\\{PROJECT_NAME}.sqlite</code><br>
        Combine un répertoire + un nom de fichier pour créer le chemin complet<br>
        Résultat : <code>L:\PROJET\BASE\E3D_S29.sqlite</code>
        </div>
        <p style="color: #666; margin: 5px 0 20px 0;">
        ✅ Commande générée : <code>campaignexport L:\PROJET\BASE\E3D_S29.sqlite L:\PROJET\TXT L:\PROJET\IMG > log.txt</code>
        </p>
        
        <h3>2️⃣ Commande avec options : tdmsdirimport</h3>
        <p style="color: #666; font-size: 13px;">Fichier : <code>data/commands/tdmsdirimport_commands.yaml</code></p>
        <pre style="background-color: #f5f5f5; padding: 12px; border-radius: 4px; font-size: 11px; border-left: 3px solid #00BCD4;">
<span style="color: #c62828;">name:</span> "tdmsdirimport_tc"
<span style="color: #c62828;">description:</span> "Importe tous les fichiers TDMS d'un dossier vers une base SQLite"
<span style="color: #c62828;">command:</span> "tdmsdirimport {TDMS_DIR} {OUTPUT_DIR} --pname {PNAME} --keys {KEYS_FILE} --config {CONFIG} {TOL} {PTABLE} {IMU_LAG_TIME} > {LOG_FILE}"
<span style="color: #c62828;">arguments:</span>
  - <span style="color: #c62828;">code:</span> "TDMS_DIR"
    <span style="color: #c62828;">name:</span> "Répertoire TDMS (entrée)"
    <span style="color: #c62828;">type:</span> "directory"
    <span style="color: #c62828;">required:</span> 1
    <span style="color: #1565c0;">default:</span> "L:\\PROJET\\TDMS"
  
  - <span style="color: #c62828;">code:</span> "OUTPUT_DIR"
    <span style="color: #c62828;">name:</span> "Répertoire de sortie (base)"
    <span style="color: #c62828;">type:</span> "directory"
    <span style="color: #c62828;">required:</span> 1
    <span style="color: #1565c0;">default:</span> "L:\\PROJET\\BASE"
  
  - <span style="color: #c62828;">code:</span> "PNAME"
    <span style="color: #c62828;">name:</span> "Nom du projet"
    <span style="color: #c62828;">type:</span> "string"
    <span style="color: #c62828;">required:</span> 1
    <span style="color: #1565c0;">default:</span> "E3D_S29"
  
  - <span style="color: #c62828;">code:</span> "TOL"
    <span style="color: #c62828;">name:</span> "Tolérance"
    <span style="color: #c62828;">type:</span> "valued_option"  <span style="color: #666;"># ← Option avec valeur</span>
    <span style="color: #c62828;">required:</span> 0
    <span style="color: #c62828;">value:</span> "--tol"
    <span style="color: #1565c0;">default:</span> "0"
  
  - <span style="color: #c62828;">code:</span> "PTABLE"
    <span style="color: #c62828;">name:</span> "Table de points"
    <span style="color: #c62828;">type:</span> "valued_option"
    <span style="color: #c62828;">required:</span> 0
    <span style="color: #c62828;">value:</span> "--ptable"
    <span style="color: #1565c0;">default:</span> "IMU"
</pre>
        <p style="color: #666; margin: 5px 0 20px 0;">
        ✅ Commande générée : <code>tdmsdirimport L:\PROJET\TDMS L:\PROJET\BASE --pname E3D_S29 --tol 0 --ptable IMU ...</code>
        </p>
        
        <h3>3️⃣ Tâche avec !include et arguments partagés</h3>
        <p style="color: #666; font-size: 13px;">Fichier : <code>data/tasks/traitement_campagne_task.yaml</code></p>
        <pre style="background-color: #f5f5f5; padding: 12px; border-radius: 4px; font-size: 12px; border-left: 3px solid #4caf50;">
<span style="color: #c62828;">name:</span> "Traitement campagne"
<span style="color: #c62828;">description:</span> "Import TDMS du dossier + export campagne (TXT + IMAGES)"

<span style="color: #1565c0;">arguments:</span>  <span style="color: #666;"># ← Arguments partagés entre les 2 commandes</span>
  - <span style="color: #c62828;">code:</span> "PROJECT_NAME"
    <span style="color: #c62828;">name:</span> "Nom du projet"
    <span style="color: #c62828;">type:</span> "string"
    <span style="color: #c62828;">required:</span> 1
    <span style="color: #1565c0;">default:</span> "E3D_S29"
    <span style="color: #1565c0;">values:</span>
      - <span style="color: #c62828;">command:</span> "tdmsdirimport_tc"
        <span style="color: #c62828;">argument:</span> "PNAME"           <span style="color: #666;"># → Nom de la table</span>
      - <span style="color: #c62828;">command:</span> "campaignexport"
        <span style="color: #c62828;">argument:</span> "PROJECT_NAME"    <span style="color: #666;"># → Nom du fichier .sqlite</span>
  
  - <span style="color: #c62828;">code:</span> "DATABASE_FILE"
    <span style="color: #c62828;">name:</span> "Répertoire de base"
    <span style="color: #c62828;">type:</span> "directory"
    <span style="color: #c62828;">required:</span> 1
    <span style="color: #1565c0;">default:</span> "L:\\PROJET\\BASE"
    <span style="color: #1565c0;">values:</span>
      - <span style="color: #c62828;">command:</span> "tdmsdirimport_tc"
        <span style="color: #c62828;">argument:</span> "OUTPUT_DIR"      <span style="color: #666;"># → Où créer la base</span>
      - <span style="color: #c62828;">command:</span> "campaignexport"
        <span style="color: #c62828;">argument:</span> "DATABASE_FILE"   <span style="color: #666;"># → Où lire la base</span>

<span style="color: #c62828;">commands:</span>
  - !include ../commands/tdmsdirimport_commands.yaml
  - !include ../commands/campaignexport_commands.yaml
</pre>
        
        <div style="background-color: #e8f5e9; padding: 12px; border-radius: 6px; margin: 15px 0; border-left: 4px solid #4caf50;">
            <b>🎯 Résultat avec construction de chemin :</b>
            <ol style="margin: 5px 0; padding-left: 20px; line-height: 1.8;">
                <li>L'utilisateur saisit : <code>PROJECT_NAME = "E3D_S29"</code> et <code>DATABASE_FILE = "L:\PROJET\BASE"</code></li>
                <li>Commande 1 : <code>tdmsdirimport ... L:\PROJET\BASE --pname E3D_S29 ...</code></li>
                <li>Commande 2 : <code>campaignexport <b>L:\PROJET\BASE\E3D_S29.sqlite</b> ...</code></li>
                <li>✅ Le chemin est construit avec <code>{DATABASE_FILE}\{PROJECT_NAME}.sqlite</code></li>
                <li>✅ <b>Cohérence garantie</b> : même nom de projet partout</li>
            </ol>
        </div>
        
        <h3>4️⃣ Conseils pratiques</h3>
        <div style="background-color: #fff3e0; padding: 12px; border-radius: 6px; margin: 10px 0; border-left: 4px solid #ff9800;">
            <b>💡 Bonnes pratiques :</b>
            <ul style="margin: 5px 0; padding-left: 20px; line-height: 1.8;">
                <li><b>Commandes réutilisables</b> : Créez des fichiers de commandes dans <code>data/commands/</code></li>
                <li><b>Tâches spécifiques</b> : Combinez les commandes avec <code>!include</code> dans <code>data/tasks/</code></li>
                <li><b>Arguments partagés</b> : Utilisez <code>arguments</code> + <code>values</code> pour éviter la répétition</li>
                <li><b>Valeurs par défaut</b> : Définissez des <code>default</code> pour accélérer la saisie</li>
                <li><b>Validation</b> : Utilisez <code>file_extensions</code> pour les fichiers</li>
                <li><b>Logs</b> : Redirigez la sortie avec <code>> {LOG_FILE}</code></li>
            </ul>
        </div>
        
        <h3>5️⃣ Boutons d'exécution</h3>
        <div style="background-color: #e8f5e9; padding: 12px; border-radius: 6px; margin: 10px 0; border-left: 4px solid #4caf50;">
            <b>▶️ Bouton "Exécuter" (vert) :</b>
            <ul style="margin: 5px 0; padding-left: 20px; line-height: 1.8;">
                <li>Situé dans la <b>console</b>, toujours visible à côté du bouton Stop</li>
                <li><b>Grisé</b> au démarrage → <b>Vert</b> quand une tâche est sélectionnée</li>
                <li>Lance l'exécution de <b>toutes les commandes</b> de la tâche en séquence</li>
                <li>Devient <b>grisé</b> pendant l'exécution (désactivé)</li>
                <li>Redevient <b>vert</b> à la fin de l'exécution</li>
            </ul>
        </div>
        
        <div style="background-color: #ffebee; padding: 12px; border-radius: 6px; margin: 10px 0; border-left: 4px solid #f44336;">
            <b>⏹️ Bouton "Stop" (rouge) :</b>
            <ul style="margin: 5px 0; padding-left: 20px; line-height: 1.8;">
                <li>Situé dans la <b>console</b>, toujours visible à côté du bouton Exécuter</li>
                <li><b>Grisé</b> par défaut → <b>Rouge</b> pendant l'exécution</li>
                <li>Cliquez dessus pour <b>arrêter immédiatement</b> la commande en cours</li>
                <li>Les commandes suivantes <b>ne seront pas exécutées</b></li>
                <li>Utile pour les commandes longues (import TDMS, calculs, etc.)</li>
                <li>L'arrêt est <b>quasi-instantané</b> même si la commande est avancée</li>
            </ul>
        </div>
        
        <div style="background-color: #e3f2fd; padding: 12px; border-radius: 6px; margin: 10px 0; border-left: 4px solid #2196F3;">
            <b>🎯 États visuels :</b>
            <table style="width: 100%; margin-top: 10px; font-size: 13px;">
                <tr>
                    <td style="padding: 5px;"><b>Au démarrage :</b></td>
                    <td style="padding: 5px;"><code>[▶ Exécuter (grisé)]  [⏹ Stop (grisé)]</code></td>
                </tr>
                <tr>
                    <td style="padding: 5px;"><b>Tâche sélectionnée :</b></td>
                    <td style="padding: 5px;"><code>[▶ Exécuter (VERT)]  [⏹ Stop (grisé)]</code></td>
                </tr>
                <tr>
                    <td style="padding: 5px;"><b>En exécution :</b></td>
                    <td style="padding: 5px;"><code>[▶ Exécuter (grisé)]  [⏹ Stop (ROUGE)]</code></td>
                </tr>
                <tr>
                    <td style="padding: 5px;"><b>Fin d'exécution :</b></td>
                    <td style="padding: 5px;"><code>[▶ Exécuter (VERT)]  [⏹ Stop (grisé)]</code></td>
                </tr>
            </table>
        </div>
        """
        self.examples_text.setHtml(content)
