# bmb/__init__.py
"""
BMB Framework - Framework rapide pour applications web
Utilise BMDB comme ORM backend
"""

__version__ = "1.0.0"
__author__ = "Votre Nom"

from bmb.core import create_app, create_model, generate_project
from bmb.cli import main

__all__ = [
    "create_app",
    "create_model", 
    "generate_project",
    "main"
]