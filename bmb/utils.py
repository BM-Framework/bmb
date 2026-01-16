# bmb/utils.py
import os
import sys
import subprocess
from pathlib import Path
import json
import yaml

def run_command(command, cwd=None):
    """Exécuter une commande shell"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def load_config():
    """Charger la configuration depuis bmb.config.yml"""
    config_file = Path.cwd() / "bmb.config.yml"
    
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"⚠ Erreur chargement config: {e}")
    
    return {}

def save_config(config):
    """Sauvegarder la configuration"""
    config_file = Path.cwd() / "bmb.config.yml"
    
    try:
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        return True
    except Exception as e:
        print(f"❌ Erreur sauvegarde config: {e}")
        return False

def get_project_info():
    """Récupérer les informations du projet BMB"""
    app_py = Path.cwd() / "app.py"
    requirements = Path.cwd() / "requirements.txt"
    
    info = {
        'is_bmb_project': app_py.exists() and requirements.exists(),
        'has_models': (Path.cwd() / "models.bmdb").exists(),
        'has_routes': (Path.cwd() / "routes").exists(),
    }
    
    if info['is_bmb_project']:
        try:
            # Lire la configuration
            config = load_config()
            info.update(config)
        except:  # noqa: E722
            pass
    
    return info

def ensure_bmb_project():
    """Vérifier que nous sommes dans un projet BMB"""
    info = get_project_info()
    
    if not info['is_bmb_project']:
        print("❌ Ce n'est pas un projet BMB.")
        print("   Exécutez 'bmb init' dans un projet vide,")
        print("   ou 'bmb new <nom>' pour créer un nouveau projet.")
        return False
    
    return True