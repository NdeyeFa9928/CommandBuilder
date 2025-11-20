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
        <h2>Qu'est-ce qu'un fichier YAML de tâche ?</h2>
        <p>
        Un fichier YAML de tâche permet de définir une séquence de commandes Windows CLI 
        qui seront exécutées dans un ordre précis. C'est un format simple et lisible pour 
        créer des workflows automatisés.
        </p>
        
        <h3>Avantages</h3>
        <ul>
            <li><b>Simplicité</b> : Format texte facile à lire et à modifier</li>
            <li><b>Réutilisabilité</b> : Définissez une fois, exécutez plusieurs fois</li>
            <li><b>Arguments partagés</b> : Évitez la duplication avec des variables communes</li>
            <li><b>Validation</b> : Vérification automatique des valeurs saisies</li>
            <li><b>Documentation intégrée</b> : Descriptions et noms explicites</li>
        </ul>
        
        <h3>Emplacement des fichiers</h3>
        <p>
        Les fichiers YAML doivent être placés dans le dossier : 
        <code>command_builder/data/tasks/</code>
        </p>
        <p>
        L'application charge automatiquement tous les fichiers <code>.yaml</code> ou <code>.yml</code> 
        présents dans ce dossier au démarrage.
        </p>
        
        <h3>Rechargement</h3>
        <p>
        Après avoir créé ou modifié un fichier YAML, redémarrez l'application pour voir les changements.
        </p>
        """
        self.intro_text.setHtml(content)
    
    def _populate_structure(self):
        """Remplit l'onglet Structure."""
        content = """
        <h2>Structure d'un fichier YAML</h2>
        
        <h3>Champs obligatoires</h3>
        <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
            <tr style="background-color: #e3f2fd;">
                <th>Champ</th>
                <th>Type</th>
                <th>Description</th>
            </tr>
            <tr>
                <td><code>name</code></td>
                <td>string</td>
                <td>Nom de la tâche (affiché dans la liste)</td>
            </tr>
            <tr>
                <td><code>description</code></td>
                <td>string</td>
                <td>Description détaillée de la tâche</td>
            </tr>
            <tr>
                <td><code>commands</code></td>
                <td>list</td>
                <td>Liste des commandes à exécuter</td>
            </tr>
        </table>
        
        <h3>Champs optionnels</h3>
        <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
            <tr style="background-color: #e3f2fd;">
                <th>Champ</th>
                <th>Type</th>
                <th>Description</th>
            </tr>
            <tr>
                <td><code>shared_arguments</code></td>
                <td>list</td>
                <td>Arguments communs à plusieurs commandes</td>
            </tr>
        </table>
        
        <h3>Exemple minimal</h3>
        <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; border-left: 4px solid #2196F3;">
name: "Ma première tâche"
description: "Une tâche simple avec une commande"
commands:
  - name: "Afficher un message"
    description: "Affiche Hello World"
    command: "echo Hello World"
    arguments: []
        </pre>
        
        <h3>Structure d'une commande</h3>
        <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
            <tr style="background-color: #e3f2fd;">
                <th>Champ</th>
                <th>Type</th>
                <th>Obligatoire</th>
                <th>Description</th>
            </tr>
            <tr>
                <td><code>name</code></td>
                <td>string</td>
                <td>Oui</td>
                <td>Nom de la commande</td>
            </tr>
            <tr>
                <td><code>description</code></td>
                <td>string</td>
                <td>Oui</td>
                <td>Description de la commande</td>
            </tr>
            <tr>
                <td><code>command</code></td>
                <td>string</td>
                <td>Oui</td>
                <td>Commande CLI à exécuter</td>
            </tr>
            <tr>
                <td><code>arguments</code></td>
                <td>list</td>
                <td>Oui</td>
                <td>Liste des arguments (peut être vide [])</td>
            </tr>
        </table>
        """
        self.structure_text.setHtml(content)
    
    def _populate_arguments(self):
        """Remplit l'onglet Arguments."""
        content = """
        <h2>Définition des arguments</h2>
        
        <h3>Champs d'un argument</h3>
        <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
            <tr style="background-color: #e3f2fd;">
                <th>Champ</th>
                <th>Type</th>
                <th>Obligatoire</th>
                <th>Description</th>
            </tr>
            <tr>
                <td><code>code</code></td>
                <td>string</td>
                <td>Oui</td>
                <td>Identifiant unique de l'argument (ex: DATABASE_FILE)</td>
            </tr>
            <tr>
                <td><code>name</code></td>
                <td>string</td>
                <td>Oui</td>
                <td>Nom affiché dans l'interface (ex: "Base de données")</td>
            </tr>
            <tr>
                <td><code>required</code></td>
                <td>int</td>
                <td>Oui</td>
                <td>0 = optionnel, 1 = obligatoire</td>
            </tr>
            <tr>
                <td><code>type</code></td>
                <td>string</td>
                <td>Non</td>
                <td>"file", "folder", "text" (par défaut: "text")</td>
            </tr>
            <tr>
                <td><code>default</code></td>
                <td>string</td>
                <td>Non</td>
                <td>Valeur par défaut</td>
            </tr>
            <tr>
                <td><code>validation</code></td>
                <td>dict</td>
                <td>Non</td>
                <td>Règles de validation (voir onglet Validation)</td>
            </tr>
        </table>
        
        <h3>Types d'arguments</h3>
        
        <h4>1. Type "text" (par défaut)</h4>
        <p>Champ de saisie libre pour du texte.</p>
        <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; border-left: 4px solid #4CAF50;">
arguments:
  - code: "TABLE_NAME"
    name: "Nom de la table"
    required: 1
    type: "text"
    default: "ma_table"
        </pre>
        
        <h4>2. Type "file"</h4>
        <p>Champ avec bouton "Parcourir" pour sélectionner un fichier.</p>
        <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; border-left: 4px solid #4CAF50;">
arguments:
  - code: "INPUT_FILE"
    name: "Fichier d'entrée"
    required: 1
    type: "file"
        </pre>
        
        <h4>3. Type "folder"</h4>
        <p>Champ avec bouton "Parcourir" pour sélectionner un dossier.</p>
        <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; border-left: 4px solid #4CAF50;">
arguments:
  - code: "OUTPUT_DIR"
    name: "Dossier de sortie"
    required: 1
    type: "folder"
        </pre>
        
        <h3>Arguments obligatoires vs optionnels</h3>
        <p>
        Les arguments obligatoires (<code>required: 1</code>) sont marqués d'une astérisque rouge <span style="color: red;">*</span> 
        dans l'interface. L'application empêche l'exécution si un champ obligatoire est vide.
        </p>
        
        <h3>Utilisation dans la commande</h3>
        <p>
        Utilisez le <code>code</code> de l'argument entre accolades <code>{}</code> dans la commande :
        </p>
        <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; border-left: 4px solid #FF9800;">
command: "python script.py --input {INPUT_FILE} --output {OUTPUT_DIR}"
        </pre>
        """
        self.arguments_text.setHtml(content)
    
    def _populate_shared(self):
        """Remplit l'onglet Arguments Partagés."""
        content = """
        <h2>🔗 Arguments partagés</h2>
        
        <h3>Qu'est-ce qu'un argument partagé ?</h3>
        <p>
        Un argument partagé est une valeur commune utilisée par plusieurs commandes. 
        Au lieu de définir le même argument pour chaque commande, vous le définissez 
        une seule fois au niveau de la tâche.
        </p>
        
        <h3>Avantages</h3>
        <ul>
            <li>Évite la duplication</li>
            <li>L'utilisateur saisit la valeur une seule fois</li>
            <li>Facilite la maintenance</li>
            <li>Réduit les erreurs de saisie</li>
        </ul>
        
        <h3>Définition</h3>
        <p>Les arguments partagés se définissent au niveau de la tâche :</p>
        <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; border-left: 4px solid #9C27B0;">
name: "Traitement de données"
description: "Import et validation"
shared_arguments:
  - code: "DATABASE_FILE"
    name: "Base de données"
    required: 1
    type: "file"
  
  - code: "LOG_LEVEL"
    name: "Niveau de log"
    required: 0
    type: "text"
    default: "INFO"

commands:
  - name: "Import"
    description: "Importe les données"
    command: "import.exe --db {DATABASE_FILE} --log {LOG_LEVEL}"
    arguments: []
  
  - name: "Validation"
    description: "Valide les données"
    command: "validate.exe --db {DATABASE_FILE} --log {LOG_LEVEL}"
    arguments: []
        </pre>
        
        <h3>Mapping vers les commandes</h3>
        <p>
        Si les codes ne correspondent pas exactement, utilisez le champ <code>shared_argument_mapping</code> :
        </p>
        <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; border-left: 4px solid #9C27B0;">
shared_arguments:
  - code: "INPUT_FILE"
    name: "Fichier source"
    required: 1
    type: "file"

commands:
  - name: "Import"
    command: "import.exe --source {SOURCE_FILE}"
    arguments: []
    shared_argument_mapping:
      INPUT_FILE: "SOURCE_FILE"
  
  - name: "Backup"
    command: "backup.exe --file {FILE_PATH}"
    arguments: []
    shared_argument_mapping:
      INPUT_FILE: "FILE_PATH"
        </pre>
        
        <h3>Combinaison avec arguments locaux</h3>
        <p>Une commande peut avoir à la fois des arguments partagés et des arguments locaux :</p>
        <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; border-left: 4px solid #9C27B0;">
shared_arguments:
  - code: "DATABASE"
    name: "Base de données"
    required: 1
    type: "file"

commands:
  - name: "Export"
    command: "export.exe --db {DATABASE} --format {FORMAT}"
    arguments:
      - code: "FORMAT"
        name: "Format de sortie"
        required: 1
        type: "text"
        default: "CSV"
        </pre>
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
        
        <h3>💡 Conseils</h3>
        <ul>
            <li>Utilisez des noms explicites pour les arguments</li>
            <li>Ajoutez des descriptions claires</li>
            <li>Définissez des valeurs par défaut quand c'est pertinent</li>
            <li>Utilisez la validation pour éviter les erreurs</li>
            <li>Privilégiez les arguments partagés pour éviter la duplication</li>
            <li>Testez vos fichiers YAML avant de les déployer</li>
        </ul>
        """
        self.examples_text.setHtml(content)
