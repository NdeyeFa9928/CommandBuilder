"""Fenêtre d'aide avec documentation complète YAML."""

from pathlib import Path
from PySide6.QtWidgets import QDialog
from PySide6 import QtUiTools


class HelpWindow(QDialog):
    """Fenêtre d'aide affichant la documentation YAML complète."""
    
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
        from PySide6.QtWidgets import QTabWidget, QTextBrowser, QPushButton
        
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
    
    def _populate_intro(self):
        """Remplit l'onglet Introduction."""
        content = """
        <h2>📘 Guide YAML - L'essentiel</h2>
        
        <div style="background-color: #e3f2fd; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #2196F3;">
            <h3 style="margin-top: 0;">Principe</h3>
            <p style="font-size: 14px; line-height: 1.6;">
            Un fichier YAML = Une <b>tâche</b> contenant une ou plusieurs <b>commandes CLI</b> à exécuter en séquence.<br>
            <b>Emplacement :</b> <code>command_builder/data/tasks/ma_tache.yaml</code>
            </p>
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
                <td style="background-color: #e8f5e9; border-radius: 4px; width: 50%;">
                    <b style="color: #2e7d32;">✅ Case à cocher</b><br>
                    <span style="font-size: 13px;">Type <code>flag</code> ou <code>valued_option</code><br>
                    Coché = inclus dans la commande</span>
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
        </table>
        
        <h3>📖 Onglets</h3>
        <ul style="line-height: 1.6;">
            <li><b>Structure</b> → Templates complets</li>
            <li><b>Arguments</b> → Les 5 types expliqués</li>
            <li><b>Arguments Partagés</b> → Éviter la répétition</li>
            <li><b>Exemples</b> → Cas réels</li>
        </ul>
        """
        self.intro_text.setHtml(content)
    
    def _populate_structure(self):
        """Remplit l'onglet Structure."""
        content = """
        <h2>📐 Templates prêts à copier</h2>
        
        <h3>Template 1 : Tâche simple (minimum requis)</h3>
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
        
        <h3>Template 2 : Commande avec arguments</h3>
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
        
        <h3>Template 3 : Avec flags et options</h3>
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
        
        <h3>Template 4 : Avec arguments partagés</h3>
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
        """
        self.structure_text.setHtml(content)
    
    def _populate_arguments(self):
        """Remplit l'onglet Arguments."""
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
            </ul>
        </div>
        """
        self.arguments_text.setHtml(content)
    
    def _populate_shared(self):
        """Remplit l'onglet Arguments Partagés."""
        content = """
        <h2>🔗 Arguments partagés</h2>
        
        <div style="background-color: #e8f5e9; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #4caf50;">
            <h3 style="margin-top: 0;">💡 Pourquoi ?</h3>
            <p style="font-size: 14px; line-height: 1.6;">
            Quand plusieurs commandes utilisent <b>la même valeur</b> (ex: base de données, fichier d'entrée),<br>
            → Définir une seule fois au lieu de répéter<br>
            → L'utilisateur saisit <b>une seule fois</b> ✅
            </p>
        </div>
        
        <h3>📝 Cas simple : Même code partout</h3>
        <pre style="background-color: #f5f5f5; padding: 12px; border-radius: 4px; font-size: 13px; border-left: 3px solid #9C27B0;">
<span style="color: #c62828; font-weight: bold;">name:</span> "Pipeline"
<span style="color: #c62828; font-weight: bold;">description:</span> "Import puis validation"

<span style="color: #1565c0; font-weight: bold;">shared_arguments:</span>
  - <span style="color: #c62828;">code:</span> "DATABASE"
    <span style="color: #c62828;">name:</span> "Base de données"
    <span style="color: #c62828;">type:</span> "file"
    <span style="color: #c62828;">required:</span> 1

<span style="color: #c62828; font-weight: bold;">commands:</span>
  - <span style="color: #c62828;">name:</span> "Import"
    <span style="color: #c62828;">command:</span> "import.exe --db {DATABASE}"
    <span style="color: #c62828;">arguments:</span> []
  
  - <span style="color: #c62828;">name:</span> "Validation"
    <span style="color: #c62828;">command:</span> "validate.exe --db {DATABASE}"
    <span style="color: #c62828;">arguments:</span> []
</pre>
        <p style="color: #666; margin: 5px 0 20px 0;">
        ✅ L'utilisateur saisit DATABASE <b>une seule fois</b><br>
        ✅ Les deux commandes utilisent automatiquement la même valeur
        </p>
        
        <h3>🔄 Cas avancé : Codes différents (mapping)</h3>
        <p>Si vos commandes utilisent des codes différents pour le même concept :</p>
        <pre style="background-color: #f5f5f5; padding: 12px; border-radius: 4px; font-size: 13px; border-left: 3px solid #9C27B0;">
<span style="color: #1565c0;">shared_arguments:</span>
  - <span style="color: #c62828;">code:</span> "INPUT_FILE"
    <span style="color: #c62828;">name:</span> "Fichier source"
    <span style="color: #c62828;">type:</span> "file"
    <span style="color: #c62828;">required:</span> 1

<span style="color: #c62828;">commands:</span>
  - <span style="color: #c62828;">name:</span> "Import"
    <span style="color: #c62828;">command:</span> "import.exe --source {SOURCE_FILE}"
    <span style="color: #c62828;">arguments:</span> []
    <span style="color: #1565c0;">shared_argument_mapping:</span>
      INPUT_FILE: "SOURCE_FILE"  <span style="color: #666;"># INPUT_FILE → SOURCE_FILE</span>
  
  - <span style="color: #c62828;">name:</span> "Backup"
    <span style="color: #c62828;">command:</span> "backup.exe --file {FILE_PATH}"
    <span style="color: #c62828;">arguments:</span> []
    <span style="color: #1565c0;">shared_argument_mapping:</span>
      INPUT_FILE: "FILE_PATH"    <span style="color: #666;"># INPUT_FILE → FILE_PATH</span>
</pre>
        <p style="color: #666; margin: 5px 0 20px 0;">
        ✅ L'utilisateur saisit INPUT_FILE une fois<br>
        ✅ Mappé vers SOURCE_FILE pour Import et FILE_PATH pour Backup
        </p>
        
        <h3>🔀 Combinaison : Partagés + Locaux</h3>
        <pre style="background-color: #f5f5f5; padding: 12px; border-radius: 4px; font-size: 13px; border-left: 3px solid #9C27B0;">
<span style="color: #1565c0;">shared_arguments:</span>
  - <span style="color: #c62828;">code:</span> "DATABASE"
    <span style="color: #c62828;">name:</span> "Base de données"
    <span style="color: #c62828;">type:</span> "file"
    <span style="color: #c62828;">required:</span> 1

<span style="color: #c62828;">commands:</span>
  - <span style="color: #c62828;">name:</span> "Export"
    <span style="color: #c62828;">command:</span> "export.exe --db {DATABASE} --format {FORMAT}"
    <span style="color: #c62828;">arguments:</span>
      - <span style="color: #c62828;">code:</span> "FORMAT"        <span style="color: #666;"># ← Argument LOCAL</span>
        <span style="color: #c62828;">name:</span> "Format"
        <span style="color: #c62828;">type:</span> "string"
        <span style="color: #c62828;">required:</span> 0
        <span style="color: #1565c0;">default:</span> "CSV"
</pre>
        <p style="color: #666; margin: 5px 0;">
        ✅ DATABASE = partagé (saisi une fois, utilisé partout)<br>
        ✅ FORMAT = local (spécifique à la commande Export)
        </p>
        """
        self.shared_text.setHtml(content)
    
    def _populate_validation(self):
        """Remplit l'onglet Validation (non utilisé actuellement)."""
        # Onglet supprimé pour simplifier l'aide
        pass
    
    def _populate_examples(self):
        """Remplit l'onglet Exemples Complets."""
        content = """
        <h2>📚 Exemples complets</h2>
        
        <h3>1️⃣ Tâche simple - Une commande</h3>
        <pre style="background-color: #f5f5f5; padding: 12px; border-radius: 4px; font-size: 13px; border-left: 3px solid #00BCD4;">
<span style="color: #c62828;">name:</span> "Export CSV"
<span style="color: #c62828;">description:</span> "Exporte une table vers CSV"
<span style="color: #c62828;">commands:</span>
  - <span style="color: #c62828;">name:</span> "csvexport"
    <span style="color: #c62828;">description:</span> "Export vers fichier CSV"
    <span style="color: #c62828;">command:</span> "csvexport.exe {DATABASE} {TABLE} {OUTPUT}"
    <span style="color: #c62828;">arguments:</span>
      - <span style="color: #c62828;">code:</span> "DATABASE"
        <span style="color: #c62828;">name:</span> "Base de données"
        <span style="color: #c62828;">type:</span> "file"
        <span style="color: #c62828;">required:</span> 1
      
      - <span style="color: #c62828;">code:</span> "TABLE"
        <span style="color: #c62828;">name:</span> "Nom de la table"
        <span style="color: #c62828;">type:</span> "string"
        <span style="color: #c62828;">required:</span> 1
      
      - <span style="color: #c62828;">code:</span> "OUTPUT"
        <span style="color: #c62828;">name:</span> "Fichier de sortie"
        <span style="color: #c62828;">type:</span> "file"
        <span style="color: #c62828;">required:</span> 0
        <span style="color: #1565c0;">default:</span> "output.csv"
</pre>
        
        <h3>2️⃣ Plusieurs commandes - Arguments partagés</h3>
        <pre style="background-color: #f5f5f5; padding: 12px; border-radius: 4px; font-size: 13px; border-left: 3px solid #00BCD4;">
<span style="color: #c62828;">name:</span> "Import TDMS complet"
<span style="color: #c62828;">description:</span> "Import TDMS puis calcul des profils"

<span style="color: #1565c0;">shared_arguments:</span>
  - <span style="color: #c62828;">code:</span> "DATABASE"
    <span style="color: #c62828;">name:</span> "Base de données"
    <span style="color: #c62828;">type:</span> "file"
    <span style="color: #c62828;">required:</span> 1

<span style="color: #c62828;">commands:</span>
  - <span style="color: #c62828;">name:</span> "tdmsimport"
    <span style="color: #c62828;">description:</span> "Import fichier TDMS"
    <span style="color: #c62828;">command:</span> "tdmsimport.exe {TDMS_FILE} {DATABASE}"
    <span style="color: #c62828;">arguments:</span>
      - <span style="color: #c62828;">code:</span> "TDMS_FILE"
        <span style="color: #c62828;">name:</span> "Fichier TDMS"
        <span style="color: #c62828;">type:</span> "file"
        <span style="color: #c62828;">required:</span> 1
  
  - <span style="color: #c62828;">name:</span> "computeprofile"
    <span style="color: #c62828;">description:</span> "Calcul des profils"
    <span style="color: #c62828;">command:</span> "computeprofile.exe {DATABASE}"
    <span style="color: #c62828;">arguments:</span> []
</pre>
        <p style="color: #666; margin: 5px 0 20px 0;">
        ✅ DATABASE saisi <b>une seule fois</b>, utilisé par les 2 commandes<br>
        ✅ Les commandes s'exécutent en séquence
        </p>
        
        <h3>3️⃣ Avec flags et options</h3>
        <pre style="background-color: #f5f5f5; padding: 12px; border-radius: 4px; font-size: 13px; border-left: 3px solid #00BCD4;">
<span style="color: #c62828;">name:</span> "Import avec options"
<span style="color: #c62828;">description:</span> "Import TDMS avec mode debug"
<span style="color: #c62828;">commands:</span>
  - <span style="color: #c62828;">name:</span> "tdmsimport"
    <span style="color: #c62828;">description:</span> "Import TDMS"
    <span style="color: #c62828;">command:</span> "tdmsimport.exe {INPUT} {DATABASE} {DEBUG}"
    <span style="color: #c62828;">arguments:</span>
      - <span style="color: #c62828;">code:</span> "INPUT"
        <span style="color: #c62828;">name:</span> "Fichier TDMS"
        <span style="color: #c62828;">type:</span> "file"
        <span style="color: #c62828;">required:</span> 1
      
      - <span style="color: #c62828;">code:</span> "DATABASE"
        <span style="color: #c62828;">name:</span> "Base de données"
        <span style="color: #c62828;">type:</span> "file"
        <span style="color: #c62828;">required:</span> 1
      
      - <span style="color: #c62828;">code:</span> "DEBUG"
        <span style="color: #c62828;">name:</span> "Mode debug"
        <span style="color: #c62828;">type:</span> "flag"
        <span style="color: #c62828;">required:</span> 0
        <span style="color: #c62828;">value:</span> "--debug"
</pre>
        <p style="color: #666; margin: 5px 0 20px 0;">
        ✅ DEBUG coché → <code>tdmsimport.exe input.tdms data.db --debug</code><br>
        ✅ DEBUG décoché → <code>tdmsimport.exe input.tdms data.db</code>
        </p>
        
        <h3>4️⃣ Mapping avancé (codes différents)</h3>
        <pre style="background-color: #f5f5f5; padding: 12px; border-radius: 4px; font-size: 13px; border-left: 3px solid #00BCD4;">
<span style="color: #c62828;">name:</span> "Pipeline avec mapping"
<span style="color: #c62828;">description:</span> "Commandes avec codes différents"

<span style="color: #1565c0;">shared_arguments:</span>
  - <span style="color: #c62828;">code:</span> "INPUT_FILE"
    <span style="color: #c62828;">name:</span> "Fichier source"
    <span style="color: #c62828;">type:</span> "file"
    <span style="color: #c62828;">required:</span> 1

<span style="color: #c62828;">commands:</span>
  - <span style="color: #c62828;">name:</span> "Import"
    <span style="color: #c62828;">command:</span> "import.exe --source {SOURCE_FILE}"
    <span style="color: #c62828;">arguments:</span> []
    <span style="color: #1565c0;">shared_argument_mapping:</span>
      INPUT_FILE: "SOURCE_FILE"
  
  - <span style="color: #c62828;">name:</span> "Backup"
    <span style="color: #c62828;">command:</span> "backup.exe --file {FILE_PATH}"
    <span style="color: #c62828;">arguments:</span> []
    <span style="color: #1565c0;">shared_argument_mapping:</span>
      INPUT_FILE: "FILE_PATH"
</pre>
        <p style="color: #666; margin: 5px 0;">
        ✅ INPUT_FILE saisi une fois<br>
        ✅ Mappé vers SOURCE_FILE pour Import et FILE_PATH pour Backup
        </p>
        
        <hr style="margin: 25px 0; border: none; border-top: 2px solid #e0e0e0;">
        
        <h3>💡 Conseils pratiques</h3>
        <ul style="line-height: 1.8;">
            <li><b>Noms clairs</b> : Utilisez des noms explicites pour les arguments</li>
            <li><b>Descriptions</b> : Ajoutez toujours une description pour aider l'utilisateur</li>
            <li><b>Valeurs par défaut</b> : Définissez-les quand c'est pertinent</li>
            <li><b>Arguments partagés</b> : Évitez la duplication pour les valeurs communes</li>
            <li><b>Extensions</b> : Utilisez <code>validation: file_extensions</code> pour les fichiers</li>
            <li>Utilisez <code>flag</code> pour les options on/off simples</li>
            <li>Utilisez <code>valued_option</code> pour les options avec valeur</li>
            <li>Testez vos fichiers YAML avant de les déployer</li>
        </ul>
        """
        self.examples_text.setHtml(content)
