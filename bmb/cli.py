"""
CLI BMB - Ligne de commande pour générer des projets et endpoints
"""

import argparse
from pathlib import Path
import shutil
from importlib import resources


class BMBCLIColors:
    """Couleurs pour le terminal"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class BMBCLI:
    """CLI BMB pour générer des projets et endpoints"""
    
    def __init__(self):
        self.colors = BMBCLIColors()
    
    def print_header(self, text):
        """Afficher un header coloré"""
        print(f"\n{self.colors.HEADER}{self.colors.BOLD}{'='*60}")
        print(f"  {text}")
        print(f"{'='*60}{self.colors.ENDC}\n")
    
    def print_success(self, text):
        """Afficher un message de succès"""
        print(f"{self.colors.GREEN}✓ {text}{self.colors.ENDC}")
    
    def print_error(self, text):
        """Afficher un message d'erreur"""
        print(f"{self.colors.FAIL}✗ {text}{self.colors.ENDC}")
    
    def print_info(self, text):
        """Afficher un message d'information"""
        print(f"{self.colors.CYAN}ℹ {text}{self.colors.ENDC}")
    
    def print_warning(self, text):
        """Afficher un avertissement"""
        print(f"{self.colors.WARNING}⚠ {text}{self.colors.ENDC}")
    
    def init_project(self, project_name):
        """Initialiser un nouveau projet BMB en copiant le template"""
        self.print_header(f"Initialisation du projet: {project_name}")
        
        project_path = Path.cwd() / project_name
        
        if project_path.exists():
            self.print_error(f"Le dossier '{project_name}' existe déjà")
            return False
        
        try:
            self.print_info("Copie du template de projet...")
            
            # Use importlib.resources to access the template
            try:
                # Access the template folder inside the package
                template_root = resources.files('bmb') / 'project_template'
                
                # Create a temporary directory to extract files
                import tempfile
                with tempfile.TemporaryDirectory() as tmp_dir:
                    tmp_path = Path(tmp_dir)
                    
                    # Copy all files from template to temp directory
                    self._copy_template_files(template_root, tmp_path)
                    
                    # Copy from temp directory to project
                    shutil.copytree(tmp_path, project_path)
                    
            except Exception as e:
                self.print_error(f"Impossible de localiser le template du projet: {e}")
                # Fallback for development
                dev_template = Path(__file__).parent / 'project_template'
                if dev_template.exists():
                    self.print_info("Utilisation du template de développement...")
                    shutil.copytree(dev_template, project_path)
                else:
                    raise
            
            self.print_success(f"Template copié vers: {project_path}")
            
            # Create additional project files
            self._create_project_files(project_path, project_name)
            
            # Final success message
            self.print_success(f"\n✨ Projet '{project_name}' créé avec succès à partir du template !")
            self._print_next_steps(project_name)
            
            return True
            
        except Exception as e:
            self.print_error(f"Erreur lors de la création du projet: {e}")
            if project_path.exists():
                shutil.rmtree(project_path)
            return False
    def _create_project_files(self, project_path, project_name):
            """Create additional project-specific files"""
            # Create .env.example
            env_content = """# Configuration BMDB
DB_CONNECTION=sqlite:///./database.db

# Configuration BMB
SECRET_KEY=change-this-secret-key
FLASK_ENV=development
DEBUG=True

# JWT
JWT_SECRET=change-this-jwt-secret
JWT_EXPIRATION_HOURS=24

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Server
HOST=0.0.0.0
PORT=5000

# BMDB Options
AUTO_LOAD_MODELS=True
CREATE_TABLES_ON_START=True
"""
            (project_path / ".env.example").write_text(env_content)
            self.print_success("Créé: .env.example")
            
            # Create .gitignore
            gitignore_content = """__pycache__/
    *.py[cod]
    .Python
    venv/
    .env
    .env.local
    *.db
    *.sqlite
    *.log
    .vscode/
    .idea/
    .DS_Store
    """
            (project_path / ".gitignore").write_text(gitignore_content)
            self.print_success("Créé: .gitignore")
            
            # Create requirements.txt
            requirements_content = """Flask>=3.0.0
    flask-cors>=4.0.0
    PyJWT>=2.8.0
    python-dotenv>=1.0.0
    Werkzeug>=3.0.1
    bmdb>=1.0.0
    """
            (project_path / "requirements.txt").write_text(requirements_content)
            self.print_success("Créé: requirements.txt")
            
            # Create run.py - Version avec caractères Unicode
            run_content = f'''"""
Point d'entree de l'application {project_name}
"""

from app import create_app
from config.app_config import AppConfig

if __name__ == '__main__':
    app = create_app()
    
    print("\\n" + "="*60)
    print("[BMB] {project_name} - Backend Framework")
    print("="*60)
    print(f"Server: http://{{AppConfig.HOST}}:{{AppConfig.PORT}}")
    print("="*60 + "\\n")
    
    app.run(
        host=AppConfig.HOST,
        port=AppConfig.PORT,
        debug=AppConfig.DEBUG
    )
    '''
            (project_path / "run.py").write_text(run_content)
            self.print_success("Créé: run.py")
            
            # Create README.md
            readme_content = f"""# {project_name}

    Projet créé avec BMB Backend Framework

    ## Installation

    ```bash
    # Créer un environnement virtuel
    python -m venv venv
    source venv/bin/activate  # Windows: venv\\Scripts\\activate

    # Installer les dépendances
    pip install -r requirements.txt

    # Configuration
    ```bash
    # Copier le fichier d'exemple
cp .env.example .env

# Éditer la configuration
nano .env
    ```

    # Créer les modèles BMDB
    ```bash
    # Créer un modèle User
bmdb create-model User
bmdb add-fields User name:string email:string:unique password:string age:integer

# Générer les modèles Python
bmdb generate
    ```

    # Lancer l'application
    ```bash
python run.py
    ```
    L'API sera disponible sur http://localhost:5000

    #Documentation API
    POST /api/auth/register - Inscription

POST /api/auth/login - Connexion

GET /api/auth/me - Profil (protégé)

GET /api/users - Liste utilisateurs (protégé)

GET /api/health - Health check
"""
            (project_path / "README.md").write_text(readme_content)
            self.print_success("Créé: README.md")

    def _print_next_steps(self, project_name):
            """Print next steps for the user"""
            print(f"\n{self.colors.CYAN}Prochaines étapes:{self.colors.ENDC}")
            print(f" 1. cd {project_name}")
            print(" 2. python -m venv venv")
            print(" 3. source venv/bin/activate (in Mac/linux) | venv/Scripts/activate (in windows)")
            print(" 4. python.exe -m pip install --upgrade pip (Optionel)")
            print(" 5. pip install -r requirements.txt")
            print(" 6. cp .env.example .env")
            print(" 7. bmdb create-model User")
            print(" 8. bmdb add-fields User name:string email:string:unique password:string")
            print(" 9. bmdb generate")
            print(" 10. bmdb migrate-schema")
            print(" 11. python run.py")
            

    def _copy_template_files(self, source, dest):
        """Copy template files recursively + clean relative imports"""
        for item in source.iterdir():
            if item.is_dir():
                new_dir = dest / item.name
                new_dir.mkdir(exist_ok=True)
                self._copy_template_files(item, new_dir)
            else:
                if item.suffix == '.pyc':
                    continue
                    
                target = dest / item.name
                shutil.copy2(item, target)
                
                # Clean relative imports only in .py files
                if item.suffix == '.py':
                    content = target.read_text(encoding='utf-8')
                    content = content.replace('from .', 'from ')
                    target.write_text(content, encoding='utf-8')
                
                self.print_success(f"  Créé: {item.name}")
    
    def generate_crud(self, model_name):
        """
        Générer automatiquement un CRUD pour un modèle
        """
        self.print_header(f"Génération CRUD pour: {model_name}")
        
        routes_dir = Path.cwd() / "bmb" / "routes"
        if not routes_dir.exists():
            self.print_error("Vous devez être dans un projet BMB")
            return False
        
        # Nom du fichier de route
        route_file = routes_dir / f"{model_name.lower()}.py"
        
        if route_file.exists():
            self.print_warning(f"Le fichier {route_file.name} existe déjà")
            overwrite = input("Voulez-vous l'écraser? (o/N): ").lower()
            if overwrite != 'o':
                self.print_info("Opération annulée")
                return False
        
        # Template du CRUD
        crud_template = f'''"""
Routes CRUD pour {model_name}
Généré automatiquement par BMB CLI
"""

from flask import Blueprint, request

from ..models_loader import load_models
from ..utils import JWTManager, success_response, error_response
from ..config import AppConfig

{model_name.lower()}_bp = Blueprint('{model_name.lower()}', __name__)


@{model_name.lower()}_bp.route('', methods=['GET'])
@JWTManager.token_required
def get_{model_name.lower()}s(current_user):
    """Récupérer tous les {model_name}s avec pagination"""
    try:
        models = load_models()
        {model_name} = models.get('{model_name}')
        
        if not {model_name}:
            return error_response("Modèle {model_name} introuvable", 500)
        
        # Pagination
        page = int(request.args.get('page', 1))
        page_size = min(
            int(request.args.get('page_size', AppConfig.DEFAULT_PAGE_SIZE)),
            AppConfig.MAX_PAGE_SIZE
        )
        
        # Récupérer tous les {model_name}s
        items = {model_name}.all()
        total_count = {model_name}.count()
        
        # Pagination manuelle
        start = (page - 1) * page_size
        end = start + page_size
        paginated = items[start:end]
        
        return success_response(
            data={{
                'items': [item.to_dict() for item in paginated],
                'pagination': {{
                    'page': page,
                    'page_size': page_size,
                    'total': total_count,
                    'total_pages': (total_count + page_size - 1) // page_size
                }}
            }}
        )
        
    except Exception as e:
        return error_response(f"Erreur: {{str(e)}}", 500)


@{model_name.lower()}_bp.route('/<int:item_id>', methods=['GET'])
@JWTManager.token_required
def get_{model_name.lower()}(current_user, item_id):
    """Récupérer un {model_name} par ID"""
    try:
        models = load_models()
        {model_name} = models.get('{model_name}')
        
        item = {model_name}.get(item_id)
        
        if not item:
            return error_response("{model_name} introuvable", 404)
        
        return success_response(data={{'item': item.to_dict()}})
        
    except Exception as e:
        return error_response(f"Erreur: {{str(e)}}", 500)


@{model_name.lower()}_bp.route('', methods=['POST'])
@JWTManager.token_required
def create_{model_name.lower()}(current_user):
    """Créer un nouveau {model_name}"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Corps de requête manquant", 400)
        
        models = load_models()
        {model_name} = models.get('{model_name}')
        
        # Créer l'instance
        new_item = {model_name}(**data)
        saved_item = new_item.save()
        
        return success_response(
            data={{'item': saved_item.to_dict()}},
            message="{model_name} créé avec succès",
            status=201
        )
        
    except Exception as e:
        return error_response(f"Erreur: {{str(e)}}", 500)


@{model_name.lower()}_bp.route('/<int:item_id>', methods=['PUT'])
@JWTManager.token_required
def update_{model_name.lower()}(current_user, item_id):
    """Mettre à jour un {model_name}"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Corps de requête manquant", 400)
        
        models = load_models()
        {model_name} = models.get('{model_name}')
        
        item = {model_name}.get(item_id)
        
        if not item:
            return error_response("{model_name} introuvable", 404)
        
        # Mettre à jour les champs
        for key, value in data.items():
            if hasattr(item, key):
                setattr(item, key, value)
        
        updated_item = item.save()
        
        return success_response(
            data={{'item': updated_item.to_dict()}},
            message="{model_name} mis à jour"
        )
        
    except Exception as e:
        return error_response(f"Erreur: {{str(e)}}", 500)


@{model_name.lower()}_bp.route('/<int:item_id>', methods=['DELETE'])
@JWTManager.token_required
def delete_{model_name.lower()}(current_user, item_id):
    """Supprimer un {model_name}"""
    try:
        models = load_models()
        {model_name} = models.get('{model_name}')
        
        item = {model_name}.get(item_id)
        
        if not item:
            return error_response("{model_name} introuvable", 404)
        
        success = item.delete()
        
        if success:
            return success_response(message="{model_name} supprimé avec succès")
        else:
            return error_response("Échec de la suppression", 500)
        
    except Exception as e:
        return error_response(f"Erreur: {{str(e)}}", 500)
'''
        
        try:
            route_file.write_text(crud_template)
            self.print_success(f"CRUD généré: {route_file.name}")
            
            # Instructions pour enregistrer la route
            print(f"\n{self.colors.CYAN}Pour activer ce CRUD:{self.colors.ENDC}")
            print("  1. Ouvrir bmb/routes/__init__.py")
            print(f"  2. Ajouter: from .{model_name.lower()} import {model_name.lower()}_bp")
            print(f"  3. Ajouter: app.register_blueprint({model_name.lower()}_bp, url_prefix='/api/{model_name.lower()}s')")
            
            return True
            
        except Exception as e:
            self.print_error(f"Erreur lors de la génération: {e}")
            return False
    
    def list_routes(self):
        """Lister toutes les routes disponibles"""
        self.print_header("Routes disponibles")
        
        routes_dir = Path.cwd() / "bmb" / "routes"
        
        if not routes_dir.exists():
            self.print_error("Vous devez être dans un projet BMB")
            return False
        
        route_files = [f for f in routes_dir.glob("*.py") if f.name != "__init__.py"]
        
        if not route_files:
            self.print_warning("Aucune route trouvée")
            return True
        
        for route_file in route_files:
            self.print_success(f"📄 {route_file.name}")
        
        return True
    
    def show_info(self):
        """Afficher les informations sur BMB"""
        self.print_header("BMB Backend Framework")
        
        print(f"{self.colors.BOLD}Version:{self.colors.ENDC} 1.0.0")
        print(f"{self.colors.BOLD}ORM:{self.colors.ENDC} BMDB")
        print(f"{self.colors.BOLD}Framework:{self.colors.ENDC} Flask")
        
        print(f"\n{self.colors.BOLD}Commandes disponibles:{self.colors.ENDC}")
        print(f"  {self.colors.CYAN}bmb init <projet>{self.colors.ENDC} - Créer un nouveau projet")
        print(f"  {self.colors.CYAN}bmb generate-crud <Model>{self.colors.ENDC} - Générer un CRUD")
        print(f"  {self.colors.CYAN}bmb list-routes{self.colors.ENDC} - Lister les routes")
        print(f"  {self.colors.CYAN}bmb info{self.colors.ENDC} - Afficher les informations")
        
        print(f"\n{self.colors.BOLD}Documentation:{self.colors.ENDC}")
        print("  GitHub: https://github.com/BM-Framework/bmb")
        print("  PyPI: https://pypi.org/project/bmb")


def main():
    """Point d'entrée du CLI"""
    parser = argparse.ArgumentParser(
        description="BMB CLI - Backend Framework avec BMDB",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Commande init
    init_parser = subparsers.add_parser('init', help='Initialiser un nouveau projet')
    init_parser.add_argument('project_name', help='Nom du projet')
    
    # Commande generate-crud
    crud_parser = subparsers.add_parser('generate-crud', help='Générer un CRUD')
    crud_parser.add_argument('model_name', help='Nom du modèle')
    
    # Commande list-routes
    subparsers.add_parser('list-routes', help='Lister les routes')
    
    # Commande info
    subparsers.add_parser('info', help='Informations sur BMB')
    
    args = parser.parse_args()
    
    cli = BMBCLI()
    
    if args.command == 'init':
        cli.init_project(args.project_name)
    elif args.command == 'generate-crud':
        cli.generate_crud(args.model_name)
    elif args.command == 'list-routes':
        cli.list_routes()
    elif args.command == 'info':
        cli.show_info()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()