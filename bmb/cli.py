# bmb/cli.py
import click
import os
import sys
from pathlib import Path
from bmb.generator import ProjectGenerator
from bmb.core import create_app, create_model

@click.group()
def main():
    """BMB Framework - Framework rapide pour applications web avec BMDB"""
    pass

@main.command()
@click.argument('project_name')
def new(project_name):
    """Créer un nouveau projet BMB"""
    try:
        generator = ProjectGenerator(project_name)
        generator.generate()
        click.echo(f"✅ Projet '{project_name}' créé avec succès!")
        click.echo(f"📁 Dossier: {Path.cwd() / project_name}")
        click.echo("\nPour démarrer:")
        click.echo(f"  cd {project_name}")
        click.echo("  pip install -r requirements.txt")
        click.echo("  bmb run")
    except Exception as e:
        click.echo(f"❌ Erreur: {e}", err=True)

@main.command()
@click.argument('model_name')
@click.option('--fields', '-f', multiple=True, 
              help='Champs du modèle (ex: name:string age:integer)')
def create(model_name, fields):
    """Créer un nouveau modèle"""
    try:
        create_model(model_name, fields)
        click.echo(f"✅ Modèle '{model_name}' créé avec succès!")
    except Exception as e:
        click.echo(f"❌ Erreur: {e}", err=True)

@main.command()
def run():
    """Démarrer le serveur de développement"""
    try:
        from bmb.core import run_server
        run_server()
    except Exception as e:
        click.echo(f"❌ Erreur: {e}", err=True)

@main.command()
def init():
    """Initialiser la configuration BMB dans le projet actuel"""
    try:
        # Créer structure de base
        folders = [
            "models",
            "routes", 
            "templates",
            "static",
            "uploads"
        ]
        
        for folder in folders:
            os.makedirs(folder, exist_ok=True)
        
        # Créer fichiers de configuration
        files = {
            ".env": """DB_CONNECTION=sqlite:///app.db
JWT_SECRET=votre_secret_jwt_tres_securise
DEBUG=True
PORT=5000
""",
            "app.py": """from bmb import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
""",
            "requirements.txt": """bmb
Flask
python-dotenv
"""
        }
        
        for filename, content in files.items():
            with open(filename, 'w') as f:
                f.write(content)
        
        click.echo("✅ Projet BMB initialisé avec succès!")
        
    except Exception as e:
        click.echo(f"❌ Erreur: {e}", err=True)

@main.command()
def version():
    """Afficher la version de BMB"""
    from bmb import __version__
    click.echo(f"BMB Framework v{__version__}")

if __name__ == '__main__':
    main()