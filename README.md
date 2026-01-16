# ⚙️ BMB - Bouchettoy Marouan Backend

**Backend Rapide & Génération d'API pour le BM Framework**

[![Retour au Framework Principal](https://img.shields.io/badge/BM-Framework-black)](https://github.com/bm-framework)
[![Built with BMDB](https://img.shields.io/badge/Powered_by-BMDB-blue)](https://github.com/bm-framework/bmdb)

**BMB** est le module backend du **BM Framework**. Basé sur **Flask**, il transforme vos modèles **BMDB** en **API RESTful sécurisée et documentée en quelques secondes**, avec un système d'authentification JWT prêt à l'emploi.

## ✨ Pourquoi BMB ?

*   **⚡ Génération d'API CRUD instantanée** à partir de vos modèles BMDB.
*   **🔐 Authentification JWT prête** (register/login/logout/refresh) sans configuration.
*   **🧩 Architecture modulaire** (controllers, services, middlewares) pour une codebase propre.
*   **🚀 CLI dédiée** pour générer endpoints, services et tests unitaires.
*   **🤝 Conçu pour BMDB** : L'intégration parfaite avec votre couche de données.

## 📦 Installation

```bash
pip install bmb
```
Pré-requis : Avoir un projet BMDB configuré (bmdb init).

🚀 Créer une API Complète en 2 Commandes
Assurez-vous d'avoir un modèle BMDB. Exemple avec bmdb create-model Article title:String content:text.

Générez l'API CRUD complète pour ce modèle :

```bash
bmb create:endpoint /api/articles --model=Article --crud
```
Démarrez le serveur :

```bash
bmb start
```
Votre API est maintenant disponible ! 🎉
```
GET /api/articles - Liste tous les articles

POST /api/articles - Crée un article

GET /api/articles/<id> - Récupère un article

etc.
```

🛠️ Référence de la CLI bmb
Commande	Description	Exemple
```bash
bmb start	Lance le serveur de développement Flask.	bmb start --port=4000
bmb create:endpoint <path>	Génère un nouveau contrôleur et ses routes.	bmb create:endpoint /api/users --model=User
bmb create:service <name>	Génère une classe de logique métier réutilisable.	bmb create:service PaymentService
bmb create:middleware <name>	Génère un middleware (ex: pour le logging).	bmb create:middleware AuthMiddleware
bmb test	Exécute la suite de tests du projet.	bmb test --coverage
bmb make:auth	Régénère les fichiers d'authentification (si personnalisation).	bmb make:auth
```
🏗️ Structure de Projet Générée
```text
votre_projet/
├── app.py                  # Point d'entrée Flask principal
├── controllers/            # Contrôleurs générés (ex: ArticleController.py)
├── services/               # Logique métier (ex: ArticleService.py)
├── middlewares/            # Middlewares (auth, logging)
├── models/                 **Vos modèles BMDB (générés par `bmdb`)**
└── tests/                  # Tests unitaires
```
🔐 Authentification Intégrée
BMB inclut un système d'authentification complet utilisant les JSON Web Tokens (JWT).

Endpoints automatiquement disponibles :
```
POST /api/auth/register - Inscription d'un nouvel utilisateur.

POST /api/auth/login - Connexion et réception d'un token JWT.

POST /api/auth/logout - Déconnexion (invalidation côté client).

GET /api/auth/me - Récupère le profil de l'utilisateur connecté.

POST /api/auth/refresh - Obtient un nouveau token d'accès.
```
Le décorateur @login_required est disponible pour protéger vos routes.

🔌 Intégration avec le Frontend (BMF)
Les API générées par BMB sont conçues pour être consommées directement par BMF, le module frontend du framework.

Exemple de workflow :
```
bmdb create-model Product ...

bmb create:endpoint /api/products --model=Product --crud

bmf create:page Admin/Products --endpoint=/api/products
```

➡️ Vous avez une interface de gestion des produits fonctionnelle.

➡️ Découvrir BMF, le module frontend

📄 Licence
MIT © Marouan Bouchettoy
