# bmb/generator.py
import os
import shutil
from pathlib import Path
from typing import Dict, List

class ProjectGenerator:
    """Générateur de projets BMB"""
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.project_path = Path.cwd() / project_name
        
        # Structure du projet
        self.structure = {
            '': [
                'app.py',
                'requirements.txt',
                '.env',
                'models.bmdb',
                '.gitignore'
            ],
            'models/': [],
            'routes/': [
                '__init__.py',
                'auth.py',
                'api.py'
            ],
            'templates/': [
                'index.html',
                'dashboard.html'
            ],
            'static/': [
                'css/style.css',
                'js/app.js'
            ],
            'uploads/': []
        }
    
    def generate(self):
        """Générer la structure complète du projet"""
        
        # Créer le dossier principal
        if self.project_path.exists():
            raise Exception(f"Le dossier '{self.project_name}' existe déjà")
        
        self.project_path.mkdir()
        os.chdir(self.project_path)
        
        # Créer la structure de dossiers
        for folder in self.structure.keys():
            if folder:
                (self.project_path / folder).mkdir(parents=True, exist_ok=True)
        
        # Créer les fichiers
        self.create_files()
        
        print(f"📁 Projet créé: {self.project_path}")
    
    def create_files(self):
        """Créer tous les fichiers du projet"""
        
        # app.py
        app_content = """# app.py - Application BMB principale
from bmb import create_app
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Créer l'application
app = create_app()

# Importer les routes personnalisées
try:
    from routes import auth, api
    print("✅ Routes personnalisées chargées")
except ImportError as e:
    print(f"⚠ Routes personnalisées non trouvées: {e}")

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')
    
    app.run(host='0.0.0.0', port=port, debug=debug)
"""
        (self.project_path / 'app.py').write_text(app_content)
        
        # requirements.txt
        req_content = """bmb
Flask>=2.0.0
Flask-CORS>=3.0.0
python-dotenv>=0.19.0
bmdb>=1.0.0
"""
        (self.project_path / 'requirements.txt').write_text(req_content)
        
        # .env
        env_content = """# Configuration BMB
DB_CONNECTION=sqlite:///app.db
JWT_SECRET=votre_secret_jwt_tres_securise
DEBUG=True
PORT=5000

# Configuration email (optionnel)
# SMTP_SERVER=smtp.gmail.com
# SMTP_PORT=587
# EMAIL_USER=votre@gmail.com
# EMAIL_PASSWORD=votre_mot_de_passe
"""
        (self.project_path / '.env').write_text(env_content)
        
        # models.bmdb
        models_content = """# Modèles de données BMB
# Documentation: https://github.com/BM-Framework/bmdb

User:
  name: string(100)
  email: string(255) unique
  password: string(255)
  age: integer
  created_at: datetime
  is_active: boolean default:true

# Exemple de modèle produit
Product:
  name: string(100)
  description: text
  price: float
  stock: integer default:0
  category: string(50)
  created_at: datetime

# Exemple de modèle commande
Order:
  user_id: integer
  product_id: integer
  quantity: integer
  total_price: float
  status: string(20) default:'pending'
  created_at: datetime
"""
        (self.project_path / 'models.bmdb').write_text(models_content)
        
        # .gitignore
        gitignore_content = """# Environnement
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Base de données
*.db
*.sqlite
*.sqlite3

# Logs
*.log
logs/

# Uploads
uploads/*

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
"""
        (self.project_path / '.gitignore').write_text(gitignore_content)
        
        # routes/__init__.py
        (self.project_path / 'routes' / '__init__.py').write_text('''# Routes BMB
# Ce package contient les routes personnalisées
''')
        
        # routes/auth.py
        auth_content = '''# routes/auth.py - Routes d'authentification
from flask import request, jsonify
import jwt
import os
from datetime import datetime, timedelta
from bmb import BMB
from models import User

def setup_routes(app):
    """Configurer les routes d'authentification"""
    
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        """Inscription utilisateur"""
        try:
            data = request.json
            
            # Vérifier si l'utilisateur existe déjà
            existing_user = User.first(email=data['email'])
            if existing_user:
                return jsonify({'error': 'Email déjà utilisé'}), 400
            
            # Créer le nouvel utilisateur
            user = User(
                name=data['name'],
                email=data['email'],
                password=data['password'],  # Note: devrait être hashé en production
                age=data.get('age')
            )
            saved_user = user.save()
            
            # Générer le token JWT
            token = jwt.encode({
                'user_id': saved_user.id,
                'email': saved_user.email,
                'exp': datetime.utcnow() + timedelta(days=7)
            }, os.getenv('JWT_SECRET'), algorithm='HS256')
            
            return jsonify({
                'message': 'Inscription réussie',
                'user': saved_user.to_dict(),
                'token': token
            }), 201
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """Connexion utilisateur"""
        try:
            data = request.json
            
            # Trouver l'utilisateur
            user = User.first(email=data['email'])
            if not user or user.password != data['password']:  # Comparaison simple
                return jsonify({'error': 'Email ou mot de passe incorrect'}), 401
            
            # Générer le token JWT
            token = jwt.encode({
                'user_id': user.id,
                'email': user.email,
                'exp': datetime.utcnow() + timedelta(days=7)
            }, os.getenv('JWT_SECRET'), algorithm='HS256')
            
            return jsonify({
                'message': 'Connexion réussie',
                'user': user.to_dict(),
                'token': token
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    @app.route('/api/auth/me', methods=['GET'])
    def get_current_user():
        """Récupérer l'utilisateur actuel"""
        token = request.headers.get('Authorization')
        
        if not token or not token.startswith('Bearer '):
            return jsonify({'error': 'Token manquant'}), 401
        
        try:
            token = token.replace('Bearer ', '')
            payload = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])
            
            user = User.get(payload['user_id'])
            if not user:
                return jsonify({'error': 'Utilisateur non trouvé'}), 404
            
            return jsonify(user.to_dict())
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expiré'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token invalide'}), 401
'''
        (self.project_path / 'routes' / 'auth.py').write_text(auth_content)
        
        # routes/api.py
        api_content = '''# routes/api.py - Routes API personnalisées
from flask import request, jsonify
from models import User, Product, Order

def setup_routes(app):
    """Configurer les routes API personnalisées"""
    
    @app.route('/api/dashboard/stats', methods=['GET'])
    def dashboard_stats():
        """Statistiques du tableau de bord"""
        try:
            total_users = User.count()
            total_products = Product.count()
            total_orders = Order.count()
            
            return jsonify({
                'users': total_users,
                'products': total_products,
                'orders': total_orders,
                'revenue': 0  # À implémenter selon votre logique métier
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/products/search', methods=['GET'])
    def search_products():
        """Rechercher des produits"""
        try:
            query = request.args.get('q', '')
            category = request.args.get('category', '')
            
            # Filtrer les produits
            filters = {}
            if query:
                # Note: BMDB ne supporte pas LIKE directement
                # Cette logique devrait être adaptée
                products = Product.all()
                results = [
                    p for p in products 
                    if query.lower() in p.name.lower() 
                    or query.lower() in (p.description or '').lower()
                ]
            else:
                if category:
                    filters['category'] = category
                results = Product.filter(**filters)
            
            return jsonify([p.to_dict() for p in results])
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/orders/user/<int:user_id>', methods=['GET'])
    def user_orders(user_id):
        """Commandes d'un utilisateur spécifique"""
        try:
            orders = Order.filter(user_id=user_id)
            return jsonify([order.to_dict() for order in orders])
        except Exception as e:
            return jsonify({'error': str(e)}), 500
'''
        (self.project_path / 'routes' / 'api.py').write_text(api_content)
        
        # templates/index.html
        html_content = '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BMB Framework - Application</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 BMB Framework</h1>
            <p>Framework rapide pour applications web</p>
        </header>
        
        <main>
            <section class="hero">
                <h2>Votre application est prête !</h2>
                <p>Backend API avec BMDB ORM fonctionnel</p>
                
                <div class="endpoints">
                    <h3>Endpoints disponibles:</h3>
                    <ul>
                        <li><code>GET /</code> - Page d'accueil</li>
                        <li><code>GET /api/health</code> - Vérification santé</li>
                        <li><code>GET /api/models</code> - Liste des modèles</li>
                        <li><code>GET /api/[model]</code> - CRUD automatique</li>
                        <li><code>POST /api/auth/register</code> - Inscription</li>
                        <li><code>POST /api/auth/login</code> - Connexion</li>
                    </ul>
                </div>
                
                <div class="actions">
                    <button onclick="testAPI()">Tester l'API</button>
                    <button onclick="showModels()">Voir les modèles</button>
                </div>
            </section>
            
            <section id="results" class="results">
                <!-- Résultats API s'afficheront ici -->
            </section>
        </main>
        
        <footer>
            <p>BMB Framework &copy; 2024 - Construit avec ❤️</p>
        </footer>
    </div>
    
    <script src="/static/js/app.js"></script>
</body>
</html>
'''
        (self.project_path / 'templates' / 'index.html').write_text(html_content)
        
        # templates/dashboard.html
        (self.project_path / 'templates' / 'dashboard.html').write_text('''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tableau de bord - BMB</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <div class="dashboard">
        <nav class="sidebar">
            <h2>BMB Dashboard</h2>
            <ul>
                <li><a href="/">Accueil</a></li>
                <li><a href="/dashboard">Tableau de bord</a></li>
                <li><a href="#users">Utilisateurs</a></li>
                <li><a href="#products">Produits</a></li>
                <li><a href="#orders">Commandes</a></li>
                <li><a href="#settings">Paramètres</a></li>
            </ul>
        </nav>
        
        <main class="content">
            <header>
                <h1>Tableau de bord</h1>
                <div class="user-info">
                    <span id="userName">Utilisateur</span>
                </div>
            </header>
            
            <div class="stats">
                <div class="stat-card">
                    <h3>Utilisateurs</h3>
                    <p id="userCount">0</p>
                </div>
                <div class="stat-card">
                    <h3>Produits</h3>
                    <p id="productCount">0</p>
                </div>
                <div class="stat-card">
                    <h3>Commandes</h3>
                    <p id="orderCount">0</p>
                </div>
                <div class="stat-card">
                    <h3>Revenu</h3>
                    <p id="revenue">0 €</p>
                </div>
            </div>
            
            <div class="recent-activity">
                <h2>Activité récente</h2>
                <div id="activityList">
                    <p>Chargement...</p>
                </div>
            </div>
        </main>
    </div>
    
    <script src="/static/js/dashboard.js"></script>
</body>
</html>
''')
        
        # static/css/style.css
        css_content = '''/* static/css/style.css - Styles BMB */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    color: #333;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

header {
    text-align: center;
    padding: 40px 20px;
    color: white;
}

header h1 {
    font-size: 3em;
    margin-bottom: 10px;
}

header p {
    font-size: 1.2em;
    opacity: 0.9;
}

.hero {
    background: white;
    border-radius: 15px;
    padding: 40px;
    margin: 20px 0;
    box-shadow: 0 20px 60px rgba(0,0,0,0.1);
}

.hero h2 {
    color: #667eea;
    margin-bottom: 20px;
    font-size: 2em;
}

.endpoints {
    background: #f7f7f9;
    border-radius: 10px;
    padding: 20px;
    margin: 30px 0;
}

.endpoints h3 {
    color: #764ba2;
    margin-bottom: 15px;
}

.endpoints ul {
    list-style: none;
}

.endpoints li {
    padding: 8px 0;
    border-bottom: 1px solid #eee;
    font-family: 'Courier New', monospace;
}

.endpoints li:last-child {
    border-bottom: none;
}

.actions {
    display: flex;
    gap: 15px;
    margin-top: 30px;
}

button {
    background: #667eea;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 8px;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.3s ease;
}

button:hover {
    background: #764ba2;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.results {
    background: white;
    border-radius: 15px;
    padding: 30px;
    margin: 20px 0;
    min-height: 200px;
}

footer {
    text-align: center;
    color: white;
    padding: 30px;
    opacity: 0.8;
}

/* Dashboard styles */
.dashboard {
    display: flex;
    min-height: 100vh;
    background: #f5f7fa;
}

.sidebar {
    width: 250px;
    background: white;
    box-shadow: 2px 0 10px rgba(0,0,0,0.1);
    padding: 20px;
}

.sidebar h2 {
    color: #667eea;
    margin-bottom: 30px;
}

.sidebar ul {
    list-style: none;
}

.sidebar li {
    padding: 12px 15px;
    margin: 5px 0;
    border-radius: 8px;
    cursor: pointer;
}

.sidebar li:hover {
    background: #f0f4ff;
}

.sidebar a {
    text-decoration: none;
    color: #333;
    display: block;
}

.content {
    flex: 1;
    padding: 30px;
}

.content header {
    text-align: left;
    padding: 0;
    color: #333;
    margin-bottom: 30px;
}

.stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 40px;
}

.stat-card {
    background: white;
    padding: 25px;
    border-radius: 12px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    text-align: center;
}

.stat-card h3 {
    color: #764ba2;
    margin-bottom: 10px;
}

.stat-card p {
    font-size: 2em;
    font-weight: bold;
    color: #667eea;
}

.recent-activity {
    background: white;
    border-radius: 12px;
    padding: 25px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.05);
}

/* Responsive */
@media (max-width: 768px) {
    .dashboard {
        flex-direction: column;
    }
    
    .sidebar {
        width: 100%;
    }
    
    .actions {
        flex-direction: column;
    }
    
    header h1 {
        font-size: 2em;
    }
}
'''
        (self.project_path / 'static' / 'css' / 'style.css').write_text(css_content)
        
        # static/js/app.js
        js_content = '''// static/js/app.js - JavaScript principal
function testAPI() {
    fetch('/api/health')
        .then(response => response.json())
        .then(data => {
            showResult('Test API:', data);
        })
        .catch(error => {
            showResult('Erreur:', error);
        });
}

function showModels() {
    fetch('/api/models')
        .then(response => response.json())
        .then(data => {
            showResult('Modèles disponibles:', data.models);
            
            // Afficher un exemple pour chaque modèle
            data.models.forEach(model => {
                fetch(`/api/${model.toLowerCase()}`)
                    .then(res => res.json())
                    .then(items => {
                        const count = Array.isArray(items) ? items.length : 1;
                        console.log(`✅ ${model}: ${count} enregistrement(s)`);
                    })
                    .catch(err => console.log(`⚠ ${model}: ${err.message}`));
            });
        })
        .catch(error => {
            showResult('Erreur:', error);
        });
}

function showResult(title, data) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = `
        <h3>${title}</h3>
        <pre>${JSON.stringify(data, null, 2)}</pre>
    `;
    resultsDiv.scrollIntoView({ behavior: 'smooth' });
}

// Tester l'API au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    console.log('BMB Framework - Application chargée');
    testAPI();
});
'''
        (self.project_path / 'static' / 'js' / 'app.js').write_text(js_content)