# Documentation API BMB

## Base URL

```url
http://localhost:5000/api
```

## Authentification

Toutes les routes protégées nécessitent un token JWT dans le header:

```header
Authorization: Bearer <token>
```

---

## Endpoints d'authentification

### POST /auth/register

Inscrire un nouvel utilisateur.

**Body:**

```json
{
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "password": "secure123",
  "age": 25
}
```

**Réponse (201):**

```json
{
  "message": "Utilisateur créé avec succès",
  "data": {
    "token": "eyJhbGc...",
    "user": {
      "id": 1,
      "name": "Alice Johnson",
      "email": "alice@example.com",
      "age": 25
    }
  }
}
```

**Erreurs:**

- `400` - Champs manquants ou invalides
- `409` - Email déjà utilisé

---

### POST /auth/login

Connecter un utilisateur.

**Body:**

```json
{
  "email": "alice@example.com",
  "password": "secure123"
}
```

**Réponse (200):**

```json
{
  "message": "Connexion réussie",
  "data": {
    "token": "eyJhbGc...",
    "user": {
      "id": 1,
      "name": "Alice Johnson",
      "email": "alice@example.com"
    }
  }
}
```

**Erreurs:**

- `400` - Champs manquants
- `401` - Email ou mot de passe incorrect

---

### GET /auth/me 🔒

Récupérer le profil de l'utilisateur connecté.

**Headers:**

```header
Authorization: Bearer <token>
```

**Réponse (200):**

```json
{
  "data": {
    "user": {
      "id": 1,
      "name": "Alice Johnson",
      "email": "alice@example.com",
      "age": 25
    }
  }
}
```

**Erreurs:**

- `401` - Token manquant ou invalide

---

### POST /auth/refresh 🔒

Renouveler le token JWT.

**Réponse (200):**

```json
{
  "message": "Token renouvelé",
  "data": {
    "token": "eyJhbGc..."
  }
}
```

---

## Endpoints Utilisateurs

### GET /users 🔒

Récupérer la liste des utilisateurs avec pagination.

**Query Params:**

- `page` (int, défaut: 1) - Numéro de page
- `page_size` (int, défaut: 20, max: 100) - Taille de page
- `age` (int, optionnel) - Filtrer par âge
- `name` (string, optionnel) - Filtrer par nom
- `email` (string, optionnel) - Filtrer par email

**Réponse (200):**

```json
{
  "data": {
    "users": [
      {
        "id": 1,
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "age": 25
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 42,
      "total_pages": 3
    }
  }
}
```

---

### GET /users/:id 🔒

Récupérer un utilisateur par ID.

**Réponse (200):**

```json
{
  "data": {
    "user": {
      "id": 1,
      "name": "Alice Johnson",
      "email": "alice@example.com",
      "age": 25
    }
  }
}
```

**Erreurs:**

- `404` - Utilisateur introuvable

---

### PUT /users/:id 🔒

Mettre à jour un utilisateur (seulement son propre profil).

**Body:**

```json
{
  "name": "Alice Smith",
  "age": 26
}
```

**Réponse (200):**

```json
{
  "message": "Utilisateur mis à jour",
  "data": {
    "user": {
      "id": 1,
      "name": "Alice Smith",
      "age": 26
    }
  }
}
```

**Erreurs:**

- `403` - Non autorisé
- `404` - Utilisateur introuvable
- `409` - Email déjà utilisé

---

### DELETE /users/:id 🔒

Supprimer un utilisateur (seulement son propre profil).

**Réponse (200):**

```json
{
  "message": "Utilisateur supprimé avec succès"
}
```

**Erreurs:**

- `403` - Non autorisé
- `404` - Utilisateur introuvable

---

### GET /users/search 🔒

Rechercher un utilisateur par email.

**Query Params:**

- `email` (string, requis) - Email à rechercher

**Réponse (200):**

```json
{
  "data": {
    "user": {
      "id": 1,
      "name": "Alice Johnson",
      "email": "alice@example.com"
    }
  }
}
```

**Erreurs:**

- `400` - Paramètre email manquant
- `404` - Utilisateur introuvable

---

### GET /users/stats 🔒

Récupérer des statistiques sur les utilisateurs.

**Réponse (200):**

```json
{
  "data": {
    "stats": {
      "total_users": 42,
      "average_age": 28.5,
      "users_with_age": 40,
      "users_without_age": 2,
      "age_distribution": {
        "18-25": 15,
        "26-35": 20,
        "36-45": 5,
        "46+": 2
      }
    }
  }
}
```

---

## Endpoints de Monitoring

### GET /health

Vérifier l'état de l'API.

**Réponse (200):**

```json
{
  "data": {
    "status": "healthy",
    "timestamp": "2025-01-19T15:30:00",
    "components": {
      "database": {
        "status": "connected",
        "orm": "BMDB"
      },
      "models": {
        "loaded": 1,
        "list": ["User"]
      }
    },
    "metrics": {
      "total_users": 42
    }
  }
}
```

---

### GET /info

Informations sur l'application.

**Réponse (200):**

```json
{
  "data": {
    "name": "BMB Backend Framework",
    "version": "1.0.0",
    "orm": "BMDB",
    "features": [
      "JWT Authentication",
      "CRUD Operations with BMDB",
      "User Management"
    ]
  }
}
```

---

## Codes d'erreur

- `200` - OK
- `201` - Créé
- `400` - Requête invalide
- `401` - Non authentifié
- `403` - Accès refusé
- `404` - Introuvable
- `409` - Conflit (ex: email dupliqué)
- `500` - Erreur serveur
- `503` - Service indisponible

---

## Format des erreurs

```json
{
  "error": "Message d'erreur",
  "errors": {
    "details": "Informations supplémentaires"
  }
}
```
