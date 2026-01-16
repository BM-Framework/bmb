# bmb/core.py
import os
import sys
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import importlib.util
import json

# Charger les variables d'environnement
load_dotenv()

class BMB:
    """Classe principale du framework BMB"""
    
    def __init__(self, app=None):
        self.app = app
        self.models = {}
        self.routes = {}
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialiser l'application Flask avec BMB"""
        self.app = app
        
        # Configuration par défaut
        app.config['SECRET_KEY'] = os.getenv('JWT_SECRET', 'bmb-secret-key')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_CONNECTION', 'sqlite:///app.db')
        
        # Activer CORS
        CORS(app)
        
        # Charger les modèles BMDB
        self.load_models()
        
        # Configurer les routes par défaut
        self.setup_default_routes()
        
        # Charger les routes personnalisées
        self.load_custom_routes()
    
    def load_models(self):
        """Charger les modèles BMDB générés"""
        try:
            # Ajouter le chemin des modèles générés
            models_path = Path.cwd() / "models" / "generated"
            sys.path.insert(0, str(models_path))
            
            # Importer les modèles
            from models import Base, engine, SessionLocal
            
            # Stocker les références
            self.Base = Base
            self.engine = engine
            self.SessionLocal = SessionLocal
            
            # Récupérer tous les modèles
            for class_name in dir(sys.modules['models']):
                cls = getattr(sys.modules['models'], class_name)
                if isinstance(cls, type) and hasattr(cls, '__tablename__'):
                    self.models[class_name] = cls
            
            print(f"✅ Modèles chargés: {list(self.models.keys())}")
            
        except ImportError as e:
            print(f"⚠ Aucun modèle BMDB trouvé: {e}")
    
    def setup_default_routes(self):
        """Configurer les routes API par défaut"""
        if not self.app:
            return
        
        @self.app.route('/')
        def index():
            return jsonify({
                'message': 'BMB Framework API',
                'version': '1.0.0',
                'endpoints': {
                    'models': '/api/models',
                    'health': '/api/health',
                    'crud': '/api/<model_name>'
                }
            })
        
        @self.app.route('/api/health')
        def health():
            return jsonify({'status': 'healthy', 'database': 'connected'})
        
        @self.app.route('/api/models')
        def list_models():
            return jsonify({'models': list(self.models.keys())})
        
        # Routes CRUD génériques pour chaque modèle
        for model_name, model_class in self.models.items():
            self.create_crud_routes(model_name.lower(), model_class)
    
    def create_crud_routes(self, endpoint, model_class):
        """Créer automatiquement les routes CRUD pour un modèle"""
        
        @self.app.route(f'/api/{endpoint}', methods=['GET'])
        def get_all():
            """Récupérer tous les enregistrements"""
            try:
                items = model_class.all()
                return jsonify([item.to_dict() for item in items])
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route(f'/api/{endpoint}/<int:id>', methods=['GET'])
        def get_one(id):
            """Récupérer un enregistrement par ID"""
            try:
                item = model_class.get(id)
                if not item:
                    return jsonify({'error': 'Non trouvé'}), 404
                return jsonify(item.to_dict())
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route(f'/api/{endpoint}', methods=['POST'])
        def create():
            """Créer un nouvel enregistrement"""
            try:
                data = request.json
                item = model_class(**data)
                saved_item = item.save()
                return jsonify(saved_item.to_dict()), 201
            except Exception as e:
                return jsonify({'error': str(e)}), 400
        
        @self.app.route(f'/api/{endpoint}/<int:id>', methods=['PUT'])
        def update(id):
            """Mettre à jour un enregistrement"""
            try:
                item = model_class.get(id)
                if not item:
                    return jsonify({'error': 'Non trouvé'}), 404
                
                data = request.json
                for key, value in data.items():
                    if hasattr(item, key):
                        setattr(item, key, value)
                
                updated_item = item.save()
                return jsonify(updated_item.to_dict())
            except Exception as e:
                return jsonify({'error': str(e)}), 400
        
        @self.app.route(f'/api/{endpoint}/<int:id>', methods=['DELETE'])
        def delete(id):
            """Supprimer un enregistrement"""
            try:
                item = model_class.get(id)
                if not item:
                    return jsonify({'error': 'Non trouvé'}), 404
                
                item.delete()
                return jsonify({'message': 'Supprimé avec succès'})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        print(f"✅ Routes CRUD créées pour: /api/{endpoint}")
    
    def load_custom_routes(self):
        """Charger les routes personnalisées du dossier routes/"""
        routes_dir = Path.cwd() / "routes"
        
        if routes_dir.exists():
            for route_file in routes_dir.glob("*.py"):
                try:
                    spec = importlib.util.spec_from_file_location(
                        route_file.stem, route_file
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    if hasattr(module, 'setup_routes'):
                        module.setup_routes(self.app)
                        print(f"✅ Routes chargées: {route_file.name}")
                        
                except Exception as e:
                    print(f"⚠ Erreur chargement routes {route_file}: {e}")

def create_app(config=None):
    """Factory pour créer une application Flask avec BMB"""
    app = Flask(__name__)
    
    # Charger la configuration
    if config:
        app.config.from_object(config)
    
    # Initialiser BMB
    bmb = BMB(app)
    
    return app

def create_model(model_name, fields):
    """Créer un nouveau modèle dans le fichier models.bmdb"""
    bmdb_file = Path.cwd() / "models.bmdb"
    
    # Créer le fichier s'il n'existe pas
    if not bmdb_file.exists():
        bmdb_file.write_text(f"{model_name}:\n")
    else:
        content = bmdb_file.read_text()
        if f"{model_name}:" not in content:
            content += f"\n{model_name}:\n"
        bmdb_file.write_text(content)
    
    # Ajouter les champs
    with open(bmdb_file, 'a') as f:
        for field in fields:
            if ':' in field:
                field_name, field_type = field.split(':', 1)
                f.write(f"  {field_name}: {field_type}\n")
    
    # Générer les modèles avec BMDB
    os.system("bmdb generate")
    os.system("bmdb migrate")
    
    return True

def run_server():
    """Démarrer le serveur de développement"""
    app = create_app()
    
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')
    
    print(f"🚀 BMB Framework démarré sur http://localhost:{port}")
    print("📁 Structure de projet BMB active")
    
    app.run(host='0.0.0.0', port=port, debug=debug)