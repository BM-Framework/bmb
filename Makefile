.PHONY: help install dev test lint format clean run

help:
	@echo "Commandes disponibles:"
	@echo "  make install    - Installer les dépendances"
	@echo "  make dev        - Installer en mode développement"
	@echo "  make test       - Lancer les tests"
	@echo "  make lint       - Vérifier le code"
	@echo "  make format     - Formater le code"
	@echo "  make clean      - Nettoyer les fichiers temporaires"
	@echo "  make run        - Lancer l'application"

install:
	pip install -r requirements.txt

dev:
	pip install -e ".[dev]"

test:
	pytest

lint:
	flake8 bmb/
	mypy bmb/

format:
	black bmb/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf build/ dist/ *.egg-info .coverage htmlcov/ .pytest_cache/

run:
	python run.py