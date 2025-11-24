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
        self.validation_text = self.findChild(QTextBrowser, "validationText")
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
        self._populate_validation()
        self._populate_examples()
    
    def _populate_intro(self):
        """Remplit l'onglet Introduction."""
        content = """
        <h2> Guide rapide YAML</h2>
        
        <div style="background-color: #e3f2fd; padding: 20px; border-radius: 8px; margin: 15px 0;">
            <h3 style="margin-top: 0;"> En bref</h3>
            <p style="font-size: 14px; line-height: 1.6;">
            Les fichiers YAML permettent de créer des <b>tâches automatisées</b> avec plusieurs commandes CLI.<br>
            Placez vos fichiers <code>.yaml</code> dans <code>command_builder/data/tasks/</code> et redémarrez l'application.
            </p>
        </div>
        
        <h3> Emplacement</h3>
        <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; border-left: 4px solid #2196F3;">
command_builder/data/tasks/ma_tache.yaml
        </pre>
        
        <h3> Code couleur dans cette aide</h3>
        <table border="0" cellpadding="10" cellspacing="0" style="width: 100%; margin: 15px 0;">
            <tr>
                <td style="background-color: #ffebee; border-radius: 4px; width: 50%;">
                    <b style="color: #c62828;"> ROUGE = OBLIGATOIRE</b><br>
                    <span style="font-size: 12px;">Ces champs doivent toujours être présents</span>
                </td>
                <td style="background-color: #e3f2fd; border-radius: 4px; width: 50%;">
                    <b style="color: #1565c0;">🔵 BLEU = OPTIONNEL</b><br>
                    <span style="font-size: 12px;">Ces champs peuvent être omis</span>
                </td>
            </tr>
        </table>
        
        <h3>📖 Navigation</h3>
        <ul style="line-height: 1.8;">
            <li><b>Structure</b> → Templates prêts à copier</li>
            <li><b>Arguments</b> → Les 5 types disponibles avec exemples</li>
            <li><b>Arguments Partagés</b> → Éviter la duplication</li>
            <li><b>Validation</b> → Vérifier les valeurs saisies</li>
            <li><b>Exemples</b> → Cas d'usage complets</li>
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
        
        <div style="background-color: #fff3e0; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #ff9800;">
            <b>💡 Astuce :</b> Utilisez le <code>code</code> entre accolades dans votre commande : <code>{CODE}</code>
        </div>
        
        <table border="0" cellpadding="15" cellspacing="10" style="width: 100%;">
            <tr>
                <td style="background-color: #e8f5e9; border-radius: 8px; width: 50%;">
                    <h3 style="margin-top: 0;"> Type "string"</h3>
                    <p><b>Interface :</b> Champ de texte</p>
                    <p><b>Usage :</b> Texte libre, noms, identifiants</p>
                    <pre style="background-color: #f5f5f5; padding: 10px; border-radius: 4px; font-size: 12px;">
- <span style="color: #c62828;">code:</span> "PROJECT_NAME"
  <span style="color: #c62828;">name:</span> "Nom du projet"
  <span style="color: #c62828;">type:</span> "string"
  <span style="color: #c62828;">required:</span> 0
  <span style="color: #1565c0;">default:</span> ""</pre>
                </td>
                <td style="background-color: #e8f5e9; border-radius: 8px; width: 50%;">
                    <h3 style="margin-top: 0;">Type "file"</h3>
                    <p><b>Interface :</b> Champ + Bouton Parcourir</p>
                    <p><b>Usage :</b> Sélection de fichiers</p>
                    <pre style="background-color: #f5f5f5; padding: 10px; border-radius: 4px; font-size: 12px;">
- <span style="color: #c62828;">code:</span> "INPUT_FILE"
  <span style="color: #c62828;">name:</span> "Fichier d'entrée"
  <span style="color: #c62828;">type:</span> "file"
  <span style="color: #c62828;">required:</span> 1
  <span style="color: #1565c0;">validation:</span>
    file_extensions: [".csv"]</pre>
                </td>
            </tr>
            <tr>
                <td style="background-color: #e8f5e9; border-radius: 8px;">
                    <h3 style="margin-top: 0;">Type "directory"</h3>
                    <p><b>Interface :</b> Champ + Bouton Parcourir</p>
                    <p><b>Usage :</b> Sélection de dossiers</p>
                    <pre style="background-color: #f5f5f5; padding: 10px; border-radius: 4px; font-size: 12px;">
- <span style="color: #c62828;">code:</span> "OUTPUT_DIR"
  <span style="color: #c62828;">name:</span> "Dossier de sortie"
  <span style="color: #c62828;">type:</span> "directory"
  <span style="color: #c62828;">required:</span> 0</pre>
                </td>
                <td style="background-color: #e3f2fd; border-radius: 8px;">
                    <h3 style="margin-top: 0;">Type "flag"</h3>
                    <p><b>Interface :</b> Case à cocher seule</p>
                    <p><b>Usage :</b> Options on/off (--debug, -v)</p>
                    <pre style="background-color: #f5f5f5; padding: 10px; border-radius: 4px; font-size: 12px;">
- <span style="color: #c62828;">code:</span> "DEBUG"
  <span style="color: #c62828;">name:</span> "Mode debug"
  <span style="color: #c62828;">type:</span> "flag"
  <span style="color: #c62828;">required:</span> 0
  <span style="color: #c62828;">value:</span> "--debug"</pre>
                    <p style="font-size: 12px;">⚠️ Champ <code>value</code> obligatoire</p>
                </td>
            </tr>
            <tr>
                <td colspan="2" style="background-color: #e3f2fd; border-radius: 8px;">
                    <h3 style="margin-top: 0;">Type "valued_option"</h3>
                    <p><b>Interface :</b> Case à cocher + Champ de saisie</p>
                    <p><b>Usage :</b> Options avec valeur (--log-level INFO, --threads 4)</p>
                    <pre style="background-color: #f5f5f5; padding: 10px; border-radius: 4px; font-size: 12px;">
- <span style="color: #c62828;">code:</span> "LOG_LEVEL"
  <span style="color: #c62828;">name:</span> "Niveau de log"
  <span style="color: #c62828;">type:</span> "valued_option"
  <span style="color: #c62828;">required:</span> 0
  <span style="color: #1565c0;">default:</span> "INFO"</pre>
                </td>
            </tr>
        </table>
        
        <h3>Champs disponibles pour un argument</h3>
        <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%; margin: 15px 0;">
            <tr style="background-color: #e3f2fd;">
                <th>Champ</th>
                <th>Obligatoire</th>
                <th>Description</th>
            </tr>
            <tr style="background-color: #ffebee;">
                <td><code>code</code></td>
                <td>🔴 OUI</td>
                <td>Identifiant unique (ex: INPUT_FILE)</td>
            </tr>
            <tr style="background-color: #ffebee;">
                <td><code>name</code></td>
                <td>🔴 OUI</td>
                <td>Nom affiché (ex: "Fichier d'entrée")</td>
            </tr>
            <tr style="background-color: #ffebee;">
                <td><code>type</code></td>
                <td>🔴 OUI</td>
                <td>"string", "file", "directory", "flag", "valued_option"</td>
            </tr>
            <tr style="background-color: #ffebee;">
                <td><code>required</code></td>
                <td>🔴 OUI</td>
                <td>0 = optionnel, 1 = obligatoire</td>
            </tr>
            <tr>
                <td><code>default</code></td>
                <td>🔵 Non</td>
                <td>Valeur par défaut</td>
            </tr>
            <tr>
                <td><code>value</code></td>
                <td>🔴 Pour flag</td>
                <td>Valeur à insérer si coché (ex: "--debug")</td>
            </tr>
            <tr>
                <td><code>validation</code></td>
                <td>🔵 Non</td>
                <td>Règles de validation (voir onglet Validation)</td>
            </tr>
        </table>
        
        <div style="background-color: #fff3e0; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #ff9800;">
            <b>⚠️ Important :</b>
            <ul style="margin: 5px 0;">
                <li>Les types <code>flag</code> et <code>valued_option</code> doivent toujours avoir <code>required: 0</code></li>
                <li>Pour <code>flag</code>, le champ <code>value</code> est obligatoire</li>
                <li>Les placeholders vides sont automatiquement supprimés de la commande</li>
            </ul>
        </div>
        """
        self.arguments_text.setHtml(content)
    
    def _populate_shared(self):
        """Remplit l'onglet Arguments Partagés."""
        content = """
        <h2>🔗 Arguments partagés</h2>
        
        <div style="background-color: #e8f5e9; padding: 20px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #4caf50;">
            <h3 style="margin-top: 0;">Pourquoi utiliser des arguments partagés ?</h3>
            <p style="font-size: 14px; line-height: 1.6;">
            Quand plusieurs commandes utilisent <b>la même valeur</b> (ex: une base de données), 
            définissez-la une seule fois au lieu de la répéter pour chaque commande.<br>
            <b>Résultat :</b> L'utilisateur saisit la valeur une seule fois ✅
            </p>
        </div>
        
        <h3>📝 Exemple simple</h3>
        <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; border-left: 4px solid #9C27B0;">
<span style="color: #c62828; font-weight: bold;">name:</span> "Pipeline de traitement"
<span style="color: #c62828; font-weight: bold;">description:</span> "Import et validation"

<span style="color: #1565c0; font-weight: bold;">shared_arguments:</span>
  - <span style="color: #c62828;">code:</span> "DATABASE"
    <span style="color: #c62828;">name:</span> "Base de données"
    <span style="color: #c62828;">type:</span> "file"
    <span style="color: #c62828;">required:</span> 1

<span style="color: #c62828; font-weight: bold;">commands:</span>
  - <span style="color: #c62828;">name:</span> "Import"
    <span style="color: #c62828;">description:</span> "Importe les données"
    <span style="color: #c62828;">command:</span> "import.exe --db {DATABASE}"
    <span style="color: #c62828;">arguments:</span> []
  
  - <span style="color: #c62828;">name:</span> "Validation"
    <span style="color: #c62828;">description:</span> "Valide les données"
    <span style="color: #c62828;">command:</span> "validate.exe --db {DATABASE}"
    <span style="color: #c62828;">arguments:</span> []
        </pre>
        <p style="color: #666; font-size: 13px;">
        L'utilisateur saisit DATABASE une seule fois<br>
        Les deux commandes utilisent la même valeur automatiquement
        </p>
        
        <h3>🔄 Mapping (codes différents)</h3>
        <p>Si vos commandes utilisent des codes différents, utilisez <code>shared_argument_mapping</code> :</p>
        <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; border-left: 4px solid #9C27B0;">
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
        <p style="color: #666; font-size: 13px;">
        INPUT_FILE est mappé vers SOURCE_FILE pour la première commande et FILE_PATH pour la seconde
        </p>
        
        <h3>Combinaison avec arguments locaux</h3>
        <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; border-left: 4px solid #9C27B0;">
<span style="color: #1565c0;">shared_arguments:</span>
  - <span style="color: #c62828;">code:</span> "DATABASE"
    <span style="color: #c62828;">name:</span> "Base de données"
    <span style="color: #c62828;">type:</span> "file"
    <span style="color: #c62828;">required:</span> 1

<span style="color: #c62828;">commands:</span>
  - <span style="color: #c62828;">name:</span> "Export"
    <span style="color: #c62828;">command:</span> "export.exe --db {DATABASE} --format {FORMAT}"
    <span style="color: #c62828;">arguments:</span>
      - <span style="color: #c62828;">code:</span> "FORMAT"
        <span style="color: #c62828;">name:</span> "Format de sortie"
        <span style="color: #c62828;">type:</span> "string"
        <span style="color: #c62828;">required:</span> 0
        <span style="color: #1565c0;">default:</span> "CSV"
        </pre>
        <p style="color: #666; font-size: 13px;">
        DATABASE est partagé (saisi une fois)<br>
        FORMAT est local à la commande Export
        </p>
        """
        self.shared_text.setHtml(content)
    
    def _populate_validation(self):
        """Remplit l'onglet Validation."""
        content = """
        <h2>Validation des arguments</h2>
        
        <h3>Types de validation disponibles</h3>
        
        <h4>1. Pattern (expression régulière)</h4>
        <p>Valide que la valeur correspond à un motif regex.</p>
        <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; border-left: 4px solid #F44336;">
arguments:
  - code: "EMAIL"
    name: "Adresse email"
    required: 1
    validation:
      pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
      message: "Format d'email invalide"
        </pre>
        
        <h4>2. Min / Max (longueur)</h4>
        <p>Valide la longueur minimale et/ou maximale d'une chaîne.</p>
        <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; border-left: 4px solid #F44336;">
arguments:
  - code: "PASSWORD"
    name: "Mot de passe"
    required: 1
    validation:
      min: 8
      max: 32
      message: "Le mot de passe doit contenir entre 8 et 32 caractères"
        </pre>
        
        <h4>3. Allowed values (valeurs autorisées)</h4>
        <p>Limite les valeurs possibles à une liste prédéfinie.</p>
        <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; border-left: 4px solid #F44336;">
arguments:
  - code: "LOG_LEVEL"
    name: "Niveau de log"
    required: 1
    validation:
      allowed_values: ["DEBUG", "INFO", "WARNING", "ERROR"]
      message: "Valeur autorisée : DEBUG, INFO, WARNING, ERROR"
        </pre>
        
        <h4>4. File exists (fichier existe)</h4>
        <p>Vérifie que le fichier spécifié existe sur le disque.</p>
        <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; border-left: 4px solid #F44336;">
arguments:
  - code: "CONFIG_FILE"
    name: "Fichier de configuration"
    required: 1
    type: "file"
    validation:
      file_exists: true
      message: "Le fichier doit exister"
        </pre>
        
        <h3>Combinaison de validations</h3>
        <p>Vous pouvez combiner plusieurs règles de validation :</p>
        <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; border-left: 4px solid #F44336;">
arguments:
  - code: "USERNAME"
    name: "Nom d'utilisateur"
    required: 1
    validation:
      min: 3
      max: 20
      pattern: "^[a-zA-Z0-9_]+$"
      message: "3-20 caractères alphanumériques et underscore uniquement"
        </pre>
        
        <h3>Messages d'erreur</h3>
        <p>
        Le champ <code>message</code> est optionnel mais recommandé. Il affiche un message 
        clair à l'utilisateur en cas d'erreur de validation.
        </p>
        
        <h3>Validation automatique</h3>
        <p>
        La validation est effectuée automatiquement :
        </p>
        <ul>
            <li>Avant l'exécution de la tâche</li>
            <li>Une boîte de dialogue affiche toutes les erreurs</li>
            <li>L'exécution est bloquée tant qu'il y a des erreurs</li>
        </ul>
        """
        self.validation_text.setHtml(content)
    
    def _populate_examples(self):
        """Remplit l'onglet Exemples Complets."""
        content = """
        <h2>Exemples complets</h2>
        
        <h3>Exemple 1 : Tâche simple</h3>
        <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; border-left: 4px solid #00BCD4;">
name: "Sauvegarde de fichiers"
description: "Copie des fichiers vers un dossier de backup"
commands:
  - name: "Créer le dossier"
    description: "Crée le dossier de destination"
    command: "mkdir {BACKUP_DIR}"
    arguments:
      - code: "BACKUP_DIR"
        name: "Dossier de backup"
        required: 1
        type: "folder"
  
  - name: "Copier les fichiers"
    description: "Copie les fichiers"
    command: "xcopy {SOURCE} {BACKUP_DIR} /E /I"
    arguments:
      - code: "SOURCE"
        name: "Dossier source"
        required: 1
        type: "folder"
      - code: "BACKUP_DIR"
        name: "Dossier de backup"
        required: 1
        type: "folder"
        </pre>
        
        <h3>Exemple 2 : Avec arguments partagés</h3>
        <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; border-left: 4px solid #00BCD4;">
name: "Pipeline de traitement"
description: "Import, validation et export de données"
shared_arguments:
  - code: "DATABASE"
    name: "Base de données"
    required: 1
    type: "file"
    validation:
      file_exists: true
      message: "La base de données doit exister"
  
  - code: "VERBOSE"
    name: "Mode verbeux"
    required: 0
    type: "text"
    default: "false"
    validation:
      allowed_values: ["true", "false"]
      message: "Valeur : true ou false"

commands:
  - name: "Import"
    description: "Importe les données CSV"
    command: "import.exe --db {DATABASE} --source {CSV_FILE} --verbose {VERBOSE}"
    arguments:
      - code: "CSV_FILE"
        name: "Fichier CSV"
        required: 1
        type: "file"
  
  - name: "Validation"
    description: "Valide les données importées"
    command: "validate.exe --db {DATABASE} --verbose {VERBOSE}"
    arguments: []
  
  - name: "Export"
    description: "Export vers Excel"
    command: "export.exe --db {DATABASE} --output {OUTPUT} --verbose {VERBOSE}"
    arguments:
      - code: "OUTPUT"
        name: "Fichier de sortie"
        required: 1
        type: "file"
        default: "output.xlsx"
        </pre>
        
        <h3>Exemple 3 : Avec validation avancée</h3>
        <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; border-left: 4px solid #00BCD4;">
name: "Configuration serveur"
description: "Configure un serveur avec validation"
commands:
  - name: "Configuration"
    description: "Configure le serveur"
    command: "configure.exe --host {HOST} --port {PORT} --user {USER} --pass {PASS}"
    arguments:
      - code: "HOST"
        name: "Adresse du serveur"
        required: 1
        type: "text"
        validation:
          pattern: "^([0-9]{1,3}\\.){3}[0-9]{1,3}$|^[a-zA-Z0-9.-]+$"
          message: "Adresse IP ou nom de domaine valide requis"
      
      - code: "PORT"
        name: "Port"
        required: 1
        type: "text"
        default: "8080"
        validation:
          pattern: "^[0-9]{1,5}$"
          message: "Port entre 1 et 65535"
      
      - code: "USER"
        name: "Nom d'utilisateur"
        required: 1
        type: "text"
        validation:
          min: 3
          max: 20
          pattern: "^[a-zA-Z0-9_]+$"
          message: "3-20 caractères alphanumériques"
      
      - code: "PASS"
        name: "Mot de passe"
        required: 1
        type: "text"
        validation:
          min: 8
          message: "Minimum 8 caractères"
        </pre>
        
        <h3>Exemple 4 : Mapping d'arguments partagés</h3>
        <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; border-left: 4px solid #00BCD4;">
name: "Traitement multi-outils"
description: "Utilise plusieurs outils avec des noms d'arguments différents"
shared_arguments:
  - code: "INPUT_FILE"
    name: "Fichier d'entrée"
    required: 1
    type: "file"
  
  - code: "OUTPUT_DIR"
    name: "Dossier de sortie"
    required: 1
    type: "folder"

commands:
  - name: "Conversion"
    description: "Convertit le fichier"
    command: "convert.exe --source {SRC} --destination {DST}"
    arguments: []
    shared_argument_mapping:
      INPUT_FILE: "SRC"
      OUTPUT_DIR: "DST"
  
  - name: "Validation"
    description: "Valide le résultat"
    command: "validate.exe --file {FILE} --outdir {OUT}"
    arguments: []
    shared_argument_mapping:
      INPUT_FILE: "FILE"
      OUTPUT_DIR: "OUT"
        </pre>
        
        <h3>Exemple 5 : Avec flags et options</h3>
        <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; border-left: 4px solid #00BCD4;">
name: "Traitement de données"
description: "Traite des données avec options avancées"
commands:
  - name: "Process"
    description: "Traite les données"
    command: "process {INPUT} {OUTPUT} {DEBUG} {VERBOSE} --log-level {LOG_LEVEL} --threads {THREADS}"
    arguments:
      # Fichier obligatoire
      - code: "INPUT"
        name: "Fichier d'entrée"
        type: "file"
        required: 1
        validation:
          file_extensions: [".csv", ".json"]
      
      # Fichier optionnel
      - code: "OUTPUT"
        name: "Fichier de sortie"
        type: "file"
        required: 0
      
      # Flags simples (checkbox seule)
      - code: "DEBUG"
        name: "Mode debug"
        type: "flag"
        required: 0
        value: "--debug"
      
      - code: "VERBOSE"
        name: "Mode verbeux"
        type: "flag"
        required: 0
        value: "-v"
      
      # Options avec valeur (checkbox + champ)
      - code: "LOG_LEVEL"
        name: "Niveau de log"
        type: "valued_option"
        required: 0
        default: "INFO"
      
      - code: "THREADS"
        name: "Nombre de threads"
        type: "valued_option"
        required: 0
        default: "4"
        </pre>
        <p><b>Résultat avec DEBUG coché, VERBOSE décoché :</b></p>
        <pre style="background-color: #e8f5e9; padding: 10px; border-radius: 4px;">
process input.csv output.csv --debug --log-level INFO --threads 4
        </pre>
        
        <h3>💡 Conseils</h3>
        <ul>
            <li>Utilisez des noms explicites pour les arguments</li>
            <li>Ajoutez des descriptions claires</li>
            <li>Définissez des valeurs par défaut quand c'est pertinent</li>
            <li>Utilisez la validation pour éviter les erreurs</li>
            <li>Privilégiez les arguments partagés pour éviter la duplication</li>
            <li>Utilisez <code>flag</code> pour les options on/off simples</li>
            <li>Utilisez <code>valued_option</code> pour les options avec valeur</li>
            <li>Testez vos fichiers YAML avant de les déployer</li>
        </ul>
        """
        self.examples_text.setHtml(content)
