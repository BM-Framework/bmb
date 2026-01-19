"""
Point d'entrée principal de l'application BMB
"""

from bmb import create_app
from bmb.config import AppConfig

if __name__ == '__main__':
    app = create_app()
    
    print("\n" + "="*60)
    print("🚀 BMB Backend Framework")
    print("="*60)
    print(f"🌐 Serveur: http://{AppConfig.HOST}:{AppConfig.PORT}")
    print("🗄️  Base de données: Connectée via BMDB")
    print("🔐 JWT: Configuré")
    print(f"📊 Modèles disponibles: {', '.join(app.bmdb_models.get('models', {}).keys())}")
    print("="*60 + "\n")
    
    app.run(
        host=AppConfig.HOST,
        port=AppConfig.PORT,
        debug=AppConfig.DEBUG
    )