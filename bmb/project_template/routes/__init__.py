"""
Enregistrement des routes
"""
from routes.auth import auth_bp
from routes.users import users_bp
from routes.health import health_bp


def register_routes(app):
    """Enregistrer toutes les routes"""
    
    # Enregistrer les blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(health_bp, url_prefix='/api')
    
    print("✅ Routes enregistrées:")
    print("   - /api/auth/*")
    print("   - /api/users/*")
    print("   - /api/health")