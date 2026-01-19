# 🚀 BMB - Guide d'utilisation complet

## 📚 Table des matières

1. [Installation rapide](#-installation-rapide)
2. [Structure du projet](#-structure-du-projet)
3. [Configuration](#-configuration)
4. [Utilisation avec BMDB](#-utilisation-avec-bmdb)
5. [Exemples concrets](#-exemples-concrets)
6. [CLI BMB](#-cli-bmb)
7. [Déploiement](#-déploiement)
8. [Bonnes pratiques](#-bonnes-pratiques)

---

## 🎯 Installation rapide

### Méthode 1 : Utiliser le CLI BMB (recommandé)

```bash
# Installer BMB
pip install bmb

# Créer un nouveau projet
bmb init mon-projet

# Suivre les instructions
cd mon-projet
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

### Méthode 2 : Installation manuelle

```bash
# Créer un projet
mkdir mon-projet && cd mon-projet

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate

# Installer BMB et BMDB
pip install bmb bmdb

# Créer les dossiers
mkdir -p bmb/{config,routes,utils,middleware}
mkdir -p bmdb/models/generated
```

---

## 📁 Structure du projet

```text
mon-projet/
│
├── bmdb/                          # BMDB ORM
│   ├── models/
│   │   ├── models.bmdb           # Définition des modèles
│   │   └── generated/
│   │       └── models.py         # Généré automatiquement
│   └── __init__.py
│
├── bmb/                           # BMB Backend
│   ├── __init__.py
│   ├── app.py                    # Factory Flask
│   ├── models_loader.py          # Chargement modèles
│   ├── database.py               # Gestionnaire DB
│   │
│   ├── config/                   # Configuration
│   │   ├── app_config.py         # Config Flask/JWT
│   │   └── bmdb_config.py        # Config BMDB
│   │
│   ├── routes/                   # Routes API
│   │   ├── auth.py               # Authentification
│   │   ├── users.py              # CRUD users
│   │   └── health.py             # Monitoring
│   │
│   ├── utils/                    # Utilitaires
│   │   ├── jwt_utils.py
│   │   ├── validators.py
│   │   └── responses.py
│   │
│   └── middleware/               # Middleware
│       ├── logging.py
│       └── error_handlers.py
│
├── tests/                        # Tests unitaires
├── .env                          # Configuration (ne pas commiter!)
├── .env.example                  # Exemple de configuration
├── requirements.txt              # Dépendances
└── run.py                        # Point d'entrée
```

---

## ⚙️ Configuration

### Fichier .env

```env
# ============================================================================
# Configuration BMDB (Base de données)
# ============================================================================

# SQLite (développement)
DB_CONNECTION=sqlite:///./database.db

# PostgreSQL (production)
# DB_CONNECTION=postgresql://user:password@localhost:5432/mydatabase

# MySQL
# DB_CONNECTION=mysql+pymysql://user:password@localhost:3306/mydatabase

# ============================================================================
# Configuration BMB (Application)
# ============================================================================

# Sécurité
SECRET_KEY=votre-clé-secrète-ultra-sécurisée
JWT_SECRET=votre-jwt-secret-différent
JWT_EXPIRATION_HOURS=24

# Flask
FLASK_ENV=development
DEBUG=True

# CORS (séparer par des virgules)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080

# Serveur
HOST=0.0.0.0
PORT=5000

# Pagination
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100

# Options BMDB
AUTO_LOAD_MODELS=True
CREATE_TABLES_ON_START=True
```

### Configuration des bases de données

#### PostgreSQL

```bash
# Installer le driver
pip install psycopg2-binary

# Configuration .env
DB_CONNECTION=postgresql://user:password@localhost:5432/mydatabase
```

#### MySQL

```bash
# Installer le driver
pip install pymysql

# Configuration .env
DB_CONNECTION=mysql+pymysql://user:password@localhost:3306/mydatabase
```

#### SQLite (par défaut)

```bash
# Aucune installation nécessaire
DB_CONNECTION=sqlite:///./database.db
```

---

## 🗄️ Utilisation avec BMDB

### Créer vos modèles

```bash
# Créer un modèle User
bmdb create-model User

# Ajouter des champs
bmdb add-fields User name:string email:string:unique password:string age:integer

# Créer un modèle Post
bmdb create-model Post

# Ajouter des champs au Post
bmdb add-fields Post title:string content:text user_id:integer

# Générer les modèles Python
bmdb generate
```

### Fichier models.bmdb généré

```yaml
models:
  User:
    fields:
      - name: name
        type: string
      - name: email
        type: string
        unique: true
      - name: password
        type: string
      - name: age
        type: integer

  Post:
    fields:
      - name: title
        type: string
      - name: content
        type: text
      - name: user_id
        type: integer
```

### Charger et utiliser les modèles dans BMB

```python
from bmb import load_models

# Charger tous les modèles
models = load_models()

# Accéder aux modèles
User = models['User']
Post = models['Post']

# Utiliser les méthodes BMDB
# CREATE
new_user = User(name="Alice", email="alice@example.com", password="hashed", age=25)
saved_user = new_user.save()

# READ
user = User.get(1)                    # Par ID
all_users = User.all()                # Tous
filtered = User.filter(age=25)        # Avec filtre
first_user = User.first(email="x@y")  # Premier résultat
count = User.count()                  # Compter

# UPDATE
user.age = 26
user.save()

# DELETE
user.delete()

# SERIALIZE
user_dict = user.to_dict()
```

---

## 💡 Exemples concrets

### Exemple 1 : Créer un endpoint personnalisé

```python
# bmb/routes/posts.py
from flask import Blueprint, request
from ..models_loader import load_models
from ..utils import JWTManager, success_response, error_response

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('', methods=['GET'])
@JWTManager.token_required
def get_posts(current_user):
    """Récupérer tous les posts"""
    models = load_models()
    Post = models.get('Post')
    
    posts = Post.all()
    
    return success_response(
        data={'posts': [post.to_dict() for post in posts]}
    )

@posts_bp.route('', methods=['POST'])
@JWTManager.token_required
def create_post(current_user):
    """Créer un nouveau post"""
    data = request.get_json()
    
    models = load_models()
    Post = models.get('Post')
    
    new_post = Post(
        title=data['title'],
        content=data['content'],
        user_id=current_user.id
    )
    
    saved_post = new_post.save()
    
    return success_response(
        data={'post': saved_post.to_dict()},
        message="Post créé avec succès",
        status=201
    )
```

Enregistrer la route :

```python
# bmb/routes/__init__.py
def register_routes(app):
    from .auth import auth_bp
    from .users import users_bp
    from .health import health_bp
    from .posts import posts_bp  # Nouveau
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(posts_bp, url_prefix='/api/posts')  # Nouveau
    app.register_blueprint(health_bp, url_prefix='/api')
```

### Exemple 2 : Ajouter une validation personnalisée

```python
# bmb/utils/validators.py
class PostValidator(Validator):
    @staticmethod
    def validate_post(data):
        """Valider un post"""
        errors = []
        
        # Titre requis
        if not data.get('title'):
            errors.append("Le titre est requis")
        elif len(data['title']) < 5:
            errors.append("Le titre doit contenir au moins 5 caractères")
        
        # Contenu requis
        if not data.get('content'):
            errors.append("Le contenu est requis")
        elif len(data['content']) < 20:
            errors.append("Le contenu doit contenir au moins 20 caractères")
        
        if errors:
            return False, errors
        
        return True, "Post valide"
```

Utilisation :

```python
@posts_bp.route('', methods=['POST'])
@JWTManager.token_required
def create_post(current_user):
    data = request.get_json()
    
    # Valider
    is_valid, result = PostValidator.validate_post(data)
    if not is_valid:
        return error_response("Données invalides", 400, errors=result)
    
    # Créer le post...
```

### Exemple 3 : Ajouter des relations entre modèles

```python
# Après avoir créé les modèles avec bmdb, vous pouvez ajouter des relations

from bmb import load_models

models = load_models()
User = models['User']
Post = models['Post']

# Récupérer un utilisateur et ses posts
user = User.get(1)

# Récupérer les posts de cet utilisateur
user_posts = Post.filter(user_id=user.id)

# Créer une méthode helper dans votre route
def get_user_with_posts(user_id):
    user = User.get(user_id)
    if not user:
        return None
    
    posts = Post.filter(user_id=user.id)
    user_dict = user.to_dict()
    user_dict['posts'] = [post.to_dict() for post in posts]
    
    return user_dict
```

---

## 🛠️ CLI BMB

### Commandes disponibles

```bash
# Créer un nouveau projet
bmb init mon-projet

# Générer un CRUD automatiquement
bmb generate-crud Post

# Lister les routes disponibles
bmb list-routes

# Afficher les informations
bmb info
```

### Générer un CRUD automatiquement

```bash
# Créer d'abord le modèle avec BMDB
bmdb create-model Product
bmdb add-fields Product name:string price:float stock:integer
bmdb generate

# Générer le CRUD avec BMB
bmb generate-crud Product

# Le fichier bmb/routes/product.py est créé avec tous les endpoints :
# GET    /api/products
# GET    /api/products/:id
# POST   /api/products
# PUT    /api/products/:id
# DELETE /api/products/:id
```

---

## 🚀 Déploiement

### Déploiement sur Heroku

```bash
# Créer un Procfile
echo "web: gunicorn run:app" > Procfile

# Créer runtime.txt
echo "python-3.11.0" > runtime.txt

# Installer gunicorn
pip install gunicorn
pip freeze > requirements.txt

# Déployer
heroku create mon-app-bmb
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set SECRET_KEY=votre-clé
heroku config:set JWT_SECRET=votre-jwt-secret
git push heroku main
```

### Déploiement sur VPS (Ubuntu)

```bash
# Sur votre serveur
sudo apt update
sudo apt install python3-pip python3-venv nginx

# Cloner votre projet
git clone https://github.com/user/mon-projet.git
cd mon-projet

# Créer l'environnement
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configurer .env
nano .env

# Installer Gunicorn
pip install gunicorn

# Tester
gunicorn -w 4 -b 0.0.0.0:5000 run:app

# Créer un service systemd
sudo nano /etc/systemd/system/bmb.service
```

Contenu du service :

```ini
[Unit]
Description=BMB Backend Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/mon-projet
Environment="PATH=/path/to/mon-projet/venv/bin"
ExecStart=/path/to/mon-projet/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 run:app

[Install]
WantedBy=multi-user.target
```

```bash
# Démarrer le service
sudo systemctl start bmb
sudo systemctl enable bmb

# Configurer Nginx
sudo nano /etc/nginx/sites-available/bmb
```

Configuration Nginx :

```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Activer le site
sudo ln -s /etc/nginx/sites-available/bmb /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## ✅ Bonnes pratiques

### 1. Sécurité

```python
# ❌ Ne jamais faire
SECRET_KEY = "password123"
DEBUG = True  # en production

# ✅ Toujours utiliser .env
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('FLASK_ENV') == 'development'
```

### 2. Validation des données

```python
# ❌ Sans validation
@app.route('/create')
def create():
    data = request.get_json()
    user = User(**data).save()  # Dangereux !

# ✅ Avec validation
@app.route('/create')
def create():
    data = request.get_json()
    
    # Valider les champs requis
    is_valid, msg = Validator.validate_required_fields(data, ['name', 'email'])
    if not is_valid:
        return error_response(msg, 400)
    
    # Valider l'email
    if not Validator.validate_email(data['email']):
        return error_response("Email invalide", 400)
    
    user = User(**data).save()
```

### 3. Gestion des erreurs

```python
# ✅ Toujours utiliser try/catch
@app.route('/users/<int:user_id>')
@JWTManager.token_required
def get_user(current_user, user_id):
    try:
        user = User.get(user_id)
        
        if not user:
            return error_response("Utilisateur introuvable", 404)
        
        return success_response(data={'user': user.to_dict()})
        
    except Exception as e:
        app.logger.error(f"Erreur get_user: {e}")
        return error_response("Erreur serveur", 500)
```

### 4. Tests

```python
# Toujours écrire des tests
# tests/test_users.py
def test_create_user(client):
    response = client.post('/api/auth/register', json={
        'name': 'Test',
        'email': 'test@example.com',
        'password': 'pass123'
    })
    
    assert response.status_code == 201
    data = response.get_json()
    assert 'token' in data['data']
```

### 5. Documentation

```python
# ✅ Documenter vos endpoints
@users_bp.route('', methods=['GET'])
@JWTManager.token_required
def get_users(current_user):
    """
    Récupérer la liste des utilisateurs
    
    Query params:
        - page (int): Numéro de page
        - page_size (int): Taille de page
        - age (int): Filtrer par âge
    
    Returns:
        200: Liste des utilisateurs
        401: Non authentifié
        500: Erreur serveur
    """
    # Code...
```

### 6. Organisation du code

```python
# ✅ Séparer les responsabilités

# bmb/services/user_service.py
class UserService:
    @staticmethod
    def create_user(data):
        # Logique métier
        pass
    
    @staticmethod
    def get_user_with_posts(user_id):
        # Logique métier
        pass

# bmb/routes/users.py
@users_bp.route('', methods=['POST'])
@JWTManager.token_required
def create_user(current_user):
    data = request.get_json()
    
    # Utiliser le service
    user = UserService.create_user(data)
    
    return success_response(data={'user': user.to_dict()}, status=201)
```

---

## 📦 Publier votre package

```bash
# Build
python setup.py sdist bdist_wheel

# Upload sur PyPI
pip install twine
twine upload dist/*

# Upload sur TestPyPI (pour tester)
twine upload --repository testpypi dist/*
```

---

## 🆘 Troubleshooting

### Erreur : "Modèles BMDB introuvables"

```bash
# Solution
bmdb generate  # Régénérer les modèles
```

### Erreur : "Database connection failed"

```bash
# Vérifier le .env
cat .env | grep DB_CONNECTION

# Tester la connexion
python -c "from bmb.database import Database; print(Database.test_connection())"
```

### Erreur : "Token invalide"

```bash
# Vérifier JWT_SECRET dans .env
# Régénérer un token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "pass"}'
```

---

## 📚 Ressources

- **Documentation BMDB** : <https://github.com/BM-Framework/bmdb>
- **Documentation BMB** : <https://github.com/BM-Framework/bmb>
- **Exemples** : <https://github.com/BM-Framework/examples>
- **Discord** : <https://discord.gg/bm-framework>

---

Développé avec ❤️ par **BM Framework**
