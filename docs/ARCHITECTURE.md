# 🏗️ Architecture du système

Ce document décrit l'architecture globale de TransMad.

## Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────┐
│                     NAVIGATEUR (CLIENT)                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  HTML/CSS/JavaScript                                  │   │
│  │  - Interface utilisateur                              │   │
│  │  - Gestion des événements                             │   │
│  │  - Affichage des résultats                            │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                            ↕️ HTTP/JSON
┌──────────────────────────────────────────────────────────────┐
│                    SERVEUR FLASK (API)                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Routes Flask                                         │   │
│  │  - /api/find-route                                   │   │
│  │  - /api/compare-transports                           │   │
│  │  - /api/optimize-time                                │   │
│  │  - /api/localities                                   │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Moteur de pathfinding                                │   │
│  │  ├─ Dijkstra.py                                      │   │
│  │  └─ A*.py                                            │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Base de données                                      │   │
│  │  ├─ Graph (nœuds + arêtes)                           │   │
│  │  └─ Transports & Localités                           │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

## 📦 Composants

### 1. Frontend (Client-side)

#### Structure
```
templates/
├── index.html          # Page unique (SPA)
│   ├── <header>        # Logo et tagline
│   ├── <main>
│   │   ├── Search section
│   │   ├── Results section
│   │   └── Loading/Error states
│   └── <footer>

static/
├── css/
│   └── style.css       # Styles (moderne, responsive)
├── js/
│   └── app.js          # Logique (fetch, DOM manipulation)
```

#### Responsabilités
- Capturer les entrées utilisateur
- Envoyer les requêtes à l'API
- Afficher les résultats
- Gestion de l'état UI

#### Technologies
- **HTML5**: Sémantique, accessibility
- **CSS3**: Flexbox, Grid, Gradients, Animations
- **JavaScript vanilla**: Pas de framework pour légèreté

### 2. Backend (Server-side)

#### Structure
```
source/
├── app.py              # Application Flask
├── graph.py            # Structure de graphe
├── dijkstra.py         # Algorithme Dijkstra
├── astar.py            # Algorithme A*
└── database.py         # Base de données transports
```

#### Responsabilités
- Servir les fichiers statiques
- Traiter les requêtes API
- Exécuter les algorithmes
- Retourner les résultats

#### Flux principal
```
Requête POST /api/find-route
    ↓
[Validation des paramètres]
    ↓
[Exécution A* ou Dijkstra]
    ↓
[Construction et formatage du résultat]
    ↓
Response JSON 200 OK
```

### 3. Base de données (In-memory)

#### Initialisation
```python
db = TransportDatabase()
graph = db.get_graph()
```

#### Contenu
- **10 nœuds**: Localités d'Antananarivo
- **~40 arêtes**: Connexions avec poids (distance, durée, prix)
- **4 types de transport**: Taxi-brousse, Taxi, Moto-taxi, Pousse-pousse

#### Structure
```
Node {
  name: String,
  latitude: Float,
  longitude: Float,
  edges: [Edge]
}

Edge {
  source: Node,
  destination: Node,
  distance: Float (km),
  duration: Float (minutes),
  price: Float (Ariary),
  transport_types: [String]
}
```

---

## 🔄 Flux de données

### Cas d'usage: Recherche de trajet

```
1. USER INPUT
   ├── Sélectionne départ: "Analakely"
   ├── Sélectionne arrivée: "Ivandry"
   └── Choisit critère: "distance"

2. FRONTEND
   ├── Valide les entrées
   ├── Affiche le spinner de chargement
   └── Envoie POST /api/find-route
      Body: {
        start: "Analakely",
        end: "Ivandry",
        optimization: "distance"
      }

3. BACKEND - FLASK
   ├── Reçoit la requête
   ├── Valide les localités
   └── Appelle astar(graph, start, end, weight)

4. BACKEND - PATHFINDING
   ├── Initialise les structures
   ├── Explore le graphe avec A*
   ├── Retourne le chemin optimal
   └── Calcule distance/durée/prix totaux

5. FLASK RESPONSE
   ├── Formate le résultat JSON
   └── Retourne:
      {
        success: true,
        path: ["Analakely", "Ivandry"],
        distance: 3.2,
        duration: 12,
        price: 15000,
        segments: [...]
      }

6. FRONTEND - REÇOIT
   ├── Parse la réponse JSON
   ├── Affiche le chemin
   ├── Récupère aussi les transports
   ├── Affiche la comparaison
   └── Affiche l'optimisation du temps

7. USER SEES
   ├── Itinéraire sur la carte mentale
   ├── Prix estimés
   ├── Temps estimés
   └── Recommandations
```

---

## 🌐 API REST

### Endpoints principaux

#### 1. GET /api/localities
Récupère toutes les localités disponibles.

**Response:**
```json
{
  "success": true,
  "localities": [
    {"name": "Analakely", "latitude": -18.8829, "longitude": 47.5241},
    {"name": "Ivandry", "latitude": -18.8769, "longitude": 47.5544}
  ]
}
```

#### 2. GET /api/transport-types
Récupère les types de transports.

**Response:**
```json
{
  "success": true,
  "transports": [
    {
      "id": "taxi-brousse",
      "name": "Taxi Brousse",
      "emoji": "🚌",
      "color": "#FF6B6B",
      "price_per_km": 25
    }
  ]
}
```

#### 3. POST /api/find-route
Trouve le meilleur trajet.

**Request:**
```json
{
  "start": "Analakely",
  "end": "Ivandry",
  "optimization": "distance"
}
```

**Response:**
```json
{
  "success": true,
  "path": ["Analakely", "Ivandry"],
  "distance": 3.2,
  "duration": 12,
  "price": 15000,
  "cheapest_transport": "moto-taxi",
  "estimated_price": 12000,
  "algorithm": "A*",
  "optimization": "distance",
  "segments": [...]
}
```

#### 4. POST /api/compare-transports
Compare les trajectoires pour les différents transports.

**Request:**
```json
{
  "distance": 5.2
}
```

**Response:**
```json
{
  "success": true,
  "distance": 5.2,
  "transports": [
    {
      "name": "Pousse Pousse",
      "emoji": "🛺",
      "color": "#95E1D3",
      "estimated_price": 26000,
      "estimated_time": 15,
      "price_per_km": 5
    }
  ]
}
```

#### 5. POST /api/optimize-time
Trouve le transport le plus rapide.

**Request:**
```json
{
  "distance": 5.2,
  "available_transports": ["taxi", "moto-taxi"]
}
```

**Response:**
```json
{
  "success": true,
  "distance": 5.2,
  "best_transport": "taxi",
  "optimized_time": 7,
  "emoji": "🚖"
}
```

---

## 🔌 Modèle de déploiement

### Développement (Actuel)

```
Local Machine:
  Port 5000: Flask développement
  
Accès: http://localhost:5000
```

### Production (Recommandé)

```
Serveur web (Nginx/Apache)
  ↓
Serveur d'application (Gunicorn)
  ↓ Python process
  ↓ Flask app
  ↓
Base de données MongoDB/PostgreSQL
```

**Configuration Gunicorn:**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 🔒 Sécurité

### Contexte actuel (Développement)

⚠️ **Non sécurisé pour production!**

### Protection à implémenter

1. **Validation entrées**
   ```python
   # Actuellement: vérification basique
   # À faire: utiliser Marshmallow ou Pydantic
   ```

2. **Rate limiting**
   ```python
   from flask_limiter import Limiter
   # Limiter à X requêtes/minute
   ```

3. **HTTPS**
   - Certificat SSL/TLS obligatoire

4. **CORS sécurisé**
   ```python
   CORS(app, origins=['https://example.com'])
   ```

5. **Authentification**
   - JWT tokens pour les utilis

ateurs

---

## 📊 Performance et scalabilité

### Métriques actuelles

```
Latence API:
  - find-route:        ~10ms (A* calculation)
  - compare-transports: ~5ms
  - optimize-time:      ~2ms
  - Total round-trip:   ~100ms (avec réseau)

Mémoire:
  - Base de données: ~1MB (en mémoire)
  - Processus Flask: ~50MB

Concurrence:
  - Requêtes/seconde: ~100 (développement)
  - Utilisateurs simultanés: ~10
```

### Goulot d'étranglement

1. **Mémoire**: Base de données en mémoire (pas de persistance)
2. **CPU**: Calcul Dijkstra/A* lié au CPU (pas d'optimisation GPU)
3. **Concurrence**: Flask par défaut est monothread

### Solutions de scalabilité

1. **Base de données réelle**
   ```
   PostgreSQL + Redis pour cache
   ```

2. **Plusieurs workers**
   ```bash
   gunicorn -w 8 app:app
   ```

3. **Caching**
   ```python
   @app.route('/api/find-route')
   @cache.cached(timeout=300)
   def find_route():
       # ...
   ```

4. **Load balancing**
   ```
   Nginx → [API1, API2, API3]
   ```

---

## 📝 Diagramme de classes

```
         Graph
         ├─ nodes: Dict[str, Node]
         ├─ edges: List[Edge]
         ├─ add_node()
         ├─ add_edge()
         ├─ get_node()
         └─ get_path_info()
              ↑
              │
      ┌───────┴────────┬───────────────┐
      │                │               │
    Node             Edge          TransportDB
    ├─ name          ├─ source      ├─ graph
    ├─ edges         ├─ dest        ├─ localities
    └─ neighbors()   ├─ distance    ├─ transport_types
                     ├─ duration    └─ methods
                     └─ price

      PriorityQueue              Algorithm Functions
      ├─ items                   ├─ dijkstra()
      ├─ add()                   └─ astar()
      ├─ pop()
      └─ contains()
```

---

## 🚀 Pipeline de déploiement

```
1. DÉVELOPPEMENT
   └─ Code local
      ├─ Test localement
      └─ Commit git

2. STAGING
   └─ Copie sur serveur test
      ├─ Tests automatisés
      └─ Vérification de performance

3. PRODUCTION
   └─ Déployer sur serveur
      ├─ Database backups
      ├─ Monitoring
      └─ Logging
```

---

## 📚 Technologies détaillées

### Backend Stack

| Composant | Technologie | Raison |
|-----------|-------------|---------|
| Framework web | Flask | Léger, flexible, Python |
| Serveur WSGI | Gunicorn | Production-ready |
| Base données | In-memory | Prototype rapide |
| API | REST + JSON | Standard web |
| Algorithmes | Python pur | Éducation, sans deps |

### Frontend Stack

| Composant | Technologie | Raison |
|-----------|-------------|---------|
| Structure | HTML5 | Sémantique |
| Styles | CSS3 | Moderne, animations |
| Logique | JavaScript vanilla | Zéro dépendances |
| API Client | Fetch | Natif navigateur |
| Fonts | Google Fonts | Gratuit, web-safe |

---

## 🎓 Points d'apprentissage

Cette architecture démontre:

1. **Architecture client-serveur** classique
2. **API REST** bien conçue
3. **Algorithmes** implémentés manuellement
4. **Frontend moderne** sans frameworks
5. **Backend minimaliste** scalable
6. **Séparation des responsabilités** claire
7. **Structures de données** manuelles

---

**TransMad Architecture** - Conception simple et éducative d'un système réel
