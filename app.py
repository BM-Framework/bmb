# bmb/app.py
"""
BMB - Backend Framework utilisant BMDB ORM
Framework Flask avec authentification JWT et CRUD automatique
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os
from pathlib import Path
import sys

# Configuration du chemin pour importer les modèles BMDB
generated_path = Path.cwd() / "bmdb" / "models" / "generated"
sys.path.insert(0, str(generated_path))
sys.path.insert(0, str(Path.cwd()))

# Import des modèles BMDB générés
try:
    from models import Base, User, engine # type: ignore
except ImportError:
    from bmdb.models.generated.models import Base, User, engine # type: ignore

# Configuration Flask
app = Flask(__name__)
CORS(app)

# Configuration JWT (à mettre dans .env en production)
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
app.config['JWT_EXPIRATION_HOURS'] = int(os.getenv('JWT_EXPIRATION_HOURS', 24))

# ============================================================================
# DECORATORS - Authentification JWT
# ============================================================================

def token_required(f):
    """Décorateur pour protéger les routes avec JWT"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Récupérer le token depuis les headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Format: "Bearer TOKEN"
            except IndexError:
                return jsonify({'message': 'Token format invalide'}), 401
        
        if not token:
            return jsonify({'message': 'Token manquant'}), 401
        
        try:
            # Décoder le token
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.get(data['user_id'])
            
            if not current_user:
                return jsonify({'message': 'Utilisateur introuvable'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expiré'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token invalide'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """
    Inscription d'un nouvel utilisateur
    Body: {name, email, password, age}
    """
    try:
        data = request.get_json()
        
        # Validation des champs requis
        required_fields = ['name', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'Le champ {field} est requis'}), 400
        
        # Vérifier si l'email existe déjà (utilise BMDB filter)
        existing_user = User.first(email=data['email'])
        if existing_user:
            return jsonify({'message': 'Cet email est déjà utilisé'}), 409
        
        # Hasher le mot de passe
        hashed_password = generate_password_hash(data['password'])
        
        # Créer le nouvel utilisateur avec BMDB
        new_user = User(
            name=data['name'],
            email=data['email'],
            password=hashed_password,
            age=data.get('age', None)  # Age optionnel
        )
        
        # Utiliser la méthode save() de BMDB
        saved_user = new_user.save()
        
        # Générer le token JWT
        token = jwt.encode({
            'user_id': saved_user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=app.config['JWT_EXPIRATION_HOURS'])
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({
            'message': 'Utilisateur créé avec succès',
            'token': token,
            'user': saved_user.to_dict()  # Utilise to_dict() de BMDB
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Erreur lors de l\'inscription: {str(e)}'}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    Connexion utilisateur
    Body: {email, password}
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Email et mot de passe requis'}), 400
        
        # Trouver l'utilisateur avec BMDB first()
        user = User.first(email=data['email'])
        
        if not user:
            return jsonify({'message': 'Email ou mot de passe incorrect'}), 401
        
        # Vérifier le mot de passe
        if not check_password_hash(user.password, data['password']):
            return jsonify({'message': 'Email ou mot de passe incorrect'}), 401
        
        # Générer le token JWT
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=app.config['JWT_EXPIRATION_HOURS'])
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({
            'message': 'Connexion réussie',
            'token': token,
            'user': user.to_dict()  # Utilise to_dict() de BMDB
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erreur lors de la connexion: {str(e)}'}), 500


@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Récupérer les informations de l'utilisateur connecté"""
    return jsonify({
        'user': current_user.to_dict()  # Utilise to_dict() de BMDB
    }), 200


@app.route('/api/auth/refresh', methods=['POST'])
@token_required
def refresh_token(current_user):
    """Renouveler le token JWT"""
    try:
        # Générer un nouveau token
        new_token = jwt.encode({
            'user_id': current_user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=app.config['JWT_EXPIRATION_HOURS'])
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({
            'message': 'Token renouvelé',
            'token': new_token
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erreur lors du renouvellement: {str(e)}'}), 500


# ============================================================================
# USER CRUD ENDPOINTS - Utilise toutes les méthodes BMDB
# ============================================================================

@app.route('/api/users', methods=['GET'])
@token_required
def get_users(current_user):
    """
    Récupérer tous les utilisateurs (avec filtres optionnels)
    Query params: age, name, email
    """
    try:
        # Récupérer les paramètres de filtrage
        filters = {}
        if request.args.get('age'):
            filters['age'] = int(request.args.get('age'))
        if request.args.get('name'):
            filters['name'] = request.args.get('name')
        if request.args.get('email'):
            filters['email'] = request.args.get('email')
        
        # Utiliser BMDB filter() ou all()
        if filters:
            users = User.filter(**filters)  # Méthode filter de BMDB
        else:
            users = User.all()  # Méthode all de BMDB
        
        # Compter les utilisateurs avec BMDB count()
        total_count = User.count(**filters) if filters else User.count()
        
        return jsonify({
            'users': [user.to_dict() for user in users],  # to_dict() de BMDB
            'count': total_count
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erreur: {str(e)}'}), 500


@app.route('/api/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(current_user, user_id):
    """Récupérer un utilisateur par ID - Utilise BMDB get()"""
    try:
        user = User.get(user_id)  # Méthode get de BMDB
        
        if not user:
            return jsonify({'message': 'Utilisateur introuvable'}), 404
        
        return jsonify({'user': user.to_dict()}), 200  # to_dict() de BMDB
        
    except Exception as e:
        return jsonify({'message': f'Erreur: {str(e)}'}), 500


@app.route('/api/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user(current_user, user_id):
    """
    Mettre à jour un utilisateur - Utilise BMDB save()
    Body: {name, email, age}
    """
    try:
        # Vérifier les permissions (un utilisateur ne peut modifier que son profil)
        if current_user.id != user_id:
            return jsonify({'message': 'Non autorisé'}), 403
        
        user = User.get(user_id)  # Méthode get de BMDB
        if not user:
            return jsonify({'message': 'Utilisateur introuvable'}), 404
        
        data = request.get_json()
        
        # Mettre à jour les champs
        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            # Vérifier si le nouvel email existe déjà
            existing = User.first(email=data['email'])
            if existing and existing.id != user_id:
                return jsonify({'message': 'Cet email est déjà utilisé'}), 409
            user.email = data['email']
        if 'age' in data:
            user.age = data['age']
        if 'password' in data:
            user.password = generate_password_hash(data['password'])
        
        # Sauvegarder avec BMDB save()
        updated_user = user.save()
        
        return jsonify({
            'message': 'Utilisateur mis à jour',
            'user': updated_user.to_dict()  # to_dict() de BMDB
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erreur: {str(e)}'}), 500


@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, user_id):
    """Supprimer un utilisateur - Utilise BMDB delete()"""
    try:
        # Vérifier les permissions
        if current_user.id != user_id:
            return jsonify({'message': 'Non autorisé'}), 403
        
        user = User.get(user_id)  # Méthode get de BMDB
        if not user:
            return jsonify({'message': 'Utilisateur introuvable'}), 404
        
        # Supprimer avec BMDB delete()
        success = user.delete()
        
        if success:
            return jsonify({'message': 'Utilisateur supprimé avec succès'}), 200
        else:
            return jsonify({'message': 'Échec de la suppression'}), 500
        
    except Exception as e:
        return jsonify({'message': f'Erreur: {str(e)}'}), 500


# ============================================================================
# STATISTICS ENDPOINTS - Utilise BMDB count()
# ============================================================================

@app.route('/api/stats/users', methods=['GET'])
@token_required
def get_user_stats(current_user):
    """Statistiques des utilisateurs - Utilise BMDB count()"""
    try:
        total_users = User.count()  # count() de BMDB
        
        # Compter par tranche d'âge (si applicable)
        stats = {
            'total_users': total_users,
            'users_by_age': {}
        }
        
        # Exemple: compter les utilisateurs de différents âges
        for age_range in [18, 25, 30, 35, 40]:
            count = User.count(age=age_range)  # count() avec filtre
            if count > 0:
                stats['users_by_age'][age_range] = count
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'message': f'Erreur: {str(e)}'}), 500


# ============================================================================
# SEARCH ENDPOINT - Utilise BMDB first()
# ============================================================================

@app.route('/api/users/search', methods=['GET'])
@token_required
def search_user(current_user):
    """
    Rechercher un utilisateur par email - Utilise BMDB first()
    Query param: email
    """
    try:
        email = request.args.get('email')
        if not email:
            return jsonify({'message': 'Paramètre email requis'}), 400
        
        # Utiliser first() de BMDB
        user = User.first(email=email)
        
        if not user:
            return jsonify({'message': 'Utilisateur introuvable'}), 404
        
        return jsonify({'user': user.to_dict()}), 200  # to_dict() de BMDB
        
    except Exception as e:
        return jsonify({'message': f'Erreur: {str(e)}'}), 500


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Vérifier l'état de l'API et de la base de données"""
    try:
        # Tester la connexion DB avec BMDB
        User.count()  # Simple requête pour tester
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'orm': 'BMDB',
            'timestamp': datetime.datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Ressource introuvable'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'message': 'Erreur serveur interne'}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Créer les tables si elles n'existent pas
    try:
        Base.metadata.create_all(engine)
        print("✅ Tables créées avec succès")
    except Exception as e:
        print(f"⚠️ Erreur lors de la création des tables: {e}")
    
    # Lancer l'application
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"🚀 BMB Backend démarré sur http://localhost:{port}")
    print("📊 Utilise BMDB ORM avec toutes ses méthodes CRUD")
    
    app.run(host='0.0.0.0', port=port, debug=debug)