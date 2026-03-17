# 📋 CHANGELOG - TransMad

Historique des modifications du projet TransMad.

---

## [1.3.0] - 2026-03-09

### 🚍 Intégration Bus Public + Marche à Pied

**Nouvelle fonctionnalité majeure** : Système de transport public avec tarif unique et connexions piétonnes !

#### **Problème résolu**
**AVANT** :
- Seulement 4 modes de transport privés (taxi, taxi-brousse, moto-taxi, pousse-pousse)
- Pas d'option économique pour petits budgets
- Pas de transport en commun
- Impossible de marcher à pied

**APRÈS** :
- ✅ Bus public avec tarif unique 600 Ar (95% moins cher !)
- ✅ 8 arrêts de bus avec coordonnées GPS
- ✅ 2 lignes de bus (Analakely-Anosy, Kininina-Ampasampito)
- ✅ Marche à pied gratuite (50 m/min = 3 km/h)
- ✅ Connexions piétonnes ville ↔ arrêt de bus
- ✅ Trajets multi-modaux automatiques (bus + marche + taxi)

#### **Fichiers créés**
1. **`data/bus_stops.json`** - 8 arrêts de bus avec coordonnées
2. **`data/bus_routes.json`** - 2 lignes de bus avec tarif unique 600 Ar
3. **`data/walk_connections.json`** - 4 connexions piétonnes ville → arrêt
4. **`docs/BUS_SYSTEM.md`** - Documentation complète du système de bus (450+ lignes)

#### **Fichiers modifiés**
1. **`data/transports.json`**
   - Ajout transport "bus" : 20 km/h, 600 Ar fixe, +1 min par arrêt
   - Ajout transport "walk" : 3 km/h (50 m/min), gratuit

2. **`source/database.py`**
   - Chargement des 3 nouveaux fichiers JSON
   - Fonction `_setup_bus_system()` pour configurer bus + marche
   - Arrêts de bus ajoutés comme nœuds dans le graphe
   - Logique spéciale pour tarif fixe bus (600 Ar)
   - Calcul temps marche : distance_m / 50 m/min
   - TRANSPORT_TYPES étendu avec bus 🚍 et marche 🚶

#### **Caractéristiques du Bus**
- **Tarif unique** : 600 Ar peu importe la distance
- **Trajets fixes** : 2 lignes prédéfinies
- **Temps d'arrêt** : +1 minute à chaque arrêt
- **Vitesse** : 20 km/h (plus lent mais économique)
- **Capacité** : 40 personnes

#### **Caractéristiques de la Marche**
- **Prix** : Gratuit (0 Ar)
- **Vitesse** : 50 m/min = 3 km/h
- **Connexions** : Ville ↔ Arrêt de bus
- **Écologique** : 100% zéro émission

#### **Exemple Économique**

**Trajet : Analakely → Anosy**

| Mode | Distance | Temps | Prix | Économie |
|------|----------|-------|------|----------|
| Taxi direct | 2.8 km | 7 min | 14,000 Ar | - |
| Bus (via arrêts) | 3.4 km | 16 min | **600 Ar** | **95%** |

#### **Routing Multi-Modal**

Le système combine intelligemment plusieurs modes :
```
Analakely --[walk 4min, 0Ar]--> Analakely Bus Stop
    --[bus 3min, 600Ar]--> Soarano Bus Stop
    --[walk 22min, 0Ar]--> Ankorondrano  
    --[taxi 4min, 10000Ar]--> Ivandry
Total: 4.1 km, 33 min, 10,600 Ar
```

Vs Taxi direct : 5 km, 8 min, 25,000 Ar

**Économie : 14,400 Ar (58% moins cher)**

---

## [1.2.0] - 2026-03-09

### 🗺️ Intégration OSRM - Routes réelles

**Nouvelle fonctionnalité majeure** : Les routes affichées sur la carte suivent maintenant les vraies rues au lieu de lignes droites !

#### **Problème résolu**
**AVANT** :
- La carte affichait des lignes droites entre les villes (vol d'oiseau)
- Les trajets ne suivaient pas les routes réelles
- Peu réaliste pour l'utilisateur

**APRÈS** :
- ✅ Les routes suivent les vraies rues via OSRM
- ✅ Basé sur OpenStreetMap (données actualisées)
- ✅ Gratuit et sans clé API requise
- ✅ Fallback automatique si OSRM indisponible

#### **Fichiers créés**
1. **`static/js/routing-config.js`** - Configuration du routing
   - Support OSRM (activé par défaut)
   - Support Google Maps API (optionnel)
   - Paramètres de visualisation
   - Fonction `getBestRoute()` avec priorités

#### **Fichiers modifiés**
1. **`static/js/app.js`**
   - Fonction `displayMapRoute()` refactorisée
   - Intégration appel OSRM
   - Nouvelles fonctions : `displayFallbackRoute()`, `adjustMapBounds()`, `addRoutingSourceBadge()`
   - Badge visuel indiquant la source du routing

2. **`templates/index.html`**
   - Chargement de `routing-config.js` avant `app.js`

3. **`data/cities.json`**
   - Coordonnées GPS mises à jour avec précision ±1mm (8-9 décimales)
   - Exemple : `"latitude": -18.9067075792458` au lieu de `-18.9087`

#### **Documentation**
1. **`RESTRUCTURATION.md`**
   - Section "Intégration OSRM (Routes Réelles)"
   - Section "Google Maps API (Optionnel)"
   - Section "Coordonnées Précises"
   - Comparaison OSRM vs Google Maps

2. **`GUIDE.md`**
   - Nouvelle section "Configuration avancée"
   - Instructions OSRM
   - Instructions Google Maps API
   - Guide modification coordonnées

#### **Fonctionnement technique**

**Flux de routing** :
```
1. Utilisateur cherche un trajet
2. Frontend récupère les coordonnées GPS
3. Appel OSRM: https://router.project-osrm.org/route/v1/driving/{coords}
4. OSRM retourne la géométrie de la route réelle
5. Leaflet affiche la route sur la carte
6. Si échec OSRM → Fallback ligne droite
```

**Configuration** :
```javascript
// static/js/routing-config.js
const ROUTING_CONFIG = {
    useOSRM: true,  // Activer OSRM
    osrmServer: 'https://router.project-osrm.org',
    routingProfile: 'driving',  // driving, walking, cycling
    useFallback: true  // Ligne droite si OSRM échoue
};
```

#### **Avantages**
- ✅ **Gratuit** : Pas de clé API nécessaire
- ✅ **Précis** : Données OpenStreetMap
- ✅ **Rapide** : Réponse <1 seconde
- ✅ **Fiable** : Fallback automatique
- ✅ **Réaliste** : Routes suivent vraies rues
- ✅ **Open Source** : Peut être hébergé localement

#### **Google Maps API (optionnel)**

Pour une précision maximale avec trafic en temps réel :
1. Obtenir clé API sur Google Cloud Console
2. Activer Directions API + Maps JavaScript API
3. Configurer dans `routing-config.js`
4. Ajouter script dans `index.html`

**Coût** : ~5 USD / 1000 requêtes après crédit gratuit

**Priorité de routing** :
1. OSRM (gratuit, par défaut)
2. Google Maps (si activé)
3. Fallback (ligne droite)

---

## [1.0.1] - 2026-03-09

### 🐛 Corrections critiques

#### **Erreur: `_build_segments` not defined**

**Problème:**
```
NameError: name '_build_segments' is not defined
File "E:\project\source\app.py", line 129, in find_route
    'segments': _build_segments(result['path'])
```

**Cause:**
- La fonction `_build_segments()` était **appelée** 3 fois dans le code (lignes 129, 173, 392)
- Mais la **déclaration** `def _build_segments(path):` était **manquante**
- Le code de la fonction existait (lignes 455-477) mais sans la ligne `def` qui déclare la fonction

**Impact:**
- ❌ Endpoint `/api/find-route` retournait erreur 500
- ❌ Frontend ne pouvait pas afficher les trajets
- ❌ Présets ne fonctionnaient pas
- ❌ Carte n'affichait aucune donnée

**Correction:**

Ajout de la déclaration de fonction dans `source/app.py` (ligne ~455):

```python
def _build_segments(path):
    """
    Construit les segments d'un trajet à partir d'un chemin
    Args:
        path: Liste de nodes (nœuds du graphe)
    Returns:
        Liste de dictionnaires représentant chaque segment
    """
    segments = []
    
    for i in range(len(path) - 1):
        current = path[i]
        next_node = path[i + 1]
        
        # Trouver l'arête
        for edge in current.edges:
            if edge.destination == next_node:
                segments.append({
                    'from': current.name,
                    'to': next_node.name,
                    'distance': edge.distance,
                    'duration': edge.duration,
                    'price': edge.price,
                    'transports': edge.transport_types
                })
                break
    
    return segments
```

**Résultat:**
- ✅ `/api/find-route` retourne maintenant JSON correct avec segments
- ✅ Frontend affiche les trajets
- ✅ Présets fonctionnent correctement
- ✅ Carte affiche les routes avec marqueurs

**Test de vérification:**
```powershell
$body = @{ start = "Analakely"; end = "Ivandry"; optimization = "distance" } | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:5000/api/find-route" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing

# Réponse attendue (200 OK):
# {
#   "success": true,
#   "segments": [{ "from": "Analakely", "to": "Ivandry", ... }],
#   ...
# }
```

---

### 📚 Documentation ajoutée

#### **Nouveau: docs/TROUBLESHOOTING.md**

Guide complet de dépannage avec:
- ✅ Solution détaillée pour l'erreur `_build_segments`
- ✅ Problèmes de démarrage du serveur
- ✅ Problèmes CSS/JavaScript non chargés
- ✅ Carte Leaflet ne s'affichant pas
- ✅ Présets non fonctionnels
- ✅ Erreurs 500 diverses
- ✅ Outils de diagnostic (F12, logs Flask, tests API)
- ✅ Checklist de vérification complète

**Fichier:** [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

#### **Nouveau: docs/MAPPING.md**

Documentation complète de l'API cartographique:
- ✅ 4 endpoints cartographiques détaillés
- ✅ Exemples de code Leaflet.js
- ✅ Format GeoJSON expliqué
- ✅ Coordonnées GPS des 10 localités
- ✅ Guide d'intégration frontend

**Fichier:** [docs/MAPPING.md](docs/MAPPING.md)

#### **Nouveau: docs/PRESETS.md**

Documentation du système de présets:
- ✅ Description des 4 présets disponibles
- ✅ Coordonnées GPS et caractéristiques de chaque preset
- ✅ Implémentation HTML/CSS/JavaScript
- ✅ Flux d'utilisation complet
- ✅ Guide pour ajouter de nouveaux présets

**Fichier:** [docs/PRESETS.md](docs/PRESETS.md)

#### **Nouveau: QUICKSTART.md**

Guide de démarrage ultra-rapide:
- ✅ Démarrage en 30 secondes
- ✅ Utilisation des présets
- ✅ Tests CLI des algorithmes
- ✅ Exemples d'API avec curl/PowerShell
- ✅ Section dépannage intégrée

**Fichier:** [QUICKSTART.md](QUICKSTART.md)

---

### 🔄 Mises à jour

#### **README.md**

- ✅ Ajout section "Problème résolu: `_build_segments`"
- ✅ Référence vers docs/TROUBLESHOOTING.md
- ✅ Amélioration section Support
- ✅ Commandes PowerShell pour Windows

#### **QUICKSTART.md**

- ✅ Ajout section "Problèmes fréquents"
- ✅ Référence vers docs/TROUBLESHOOTING.md
- ✅ Tests de vérification rapides

---

### ✅ Tests effectués

#### **Backend**

```powershell
# Test 1: Health check
✅ GET /api/health → 200 OK
   Response: {"success": true, "localities_count": 10, ...}

# Test 2: Find route (erreur corrigée)
✅ POST /api/find-route → 200 OK
   Body: {"start": "Analakely", "end": "Ivandry", "optimization": "distance"}
   Response: {"success": true, "segments": [...], ...}

# Test 3: GeoJSON
✅ POST /api/route-geojson → 200 OK
   Response: {"success": true, "geojson": {...}, ...}
```

#### **Frontend**

```
✅ Chargement page index.html → 200 OK
✅ Chargement CSS style.css → 200 OK
✅ Chargement JS app.js → 200 OK
✅ Chargement Leaflet CDN → 200 OK
✅ Présets cliquables → Trajets affichés
✅ Carte Leaflet → Marqueurs + polyline visibles
✅ Console navigateur → Aucune erreur
```

---

## [1.0.0] - 2026-03-08

### 🎉 Version initiale

#### Fonctionnalités principales

- ✅ Backend Flask avec 8 endpoints API
- ✅ Algorithmes Dijkstra et A* implémentés manuellement
- ✅ Base de données 10 localités + 40 routes + 4 transports
- ✅ Frontend HTML/CSS/JS responsive
- ✅ Carte interactive Leaflet.js
- ✅ 4 présets de trajets rapides
- ✅ Système de tests automatisés (test.py)
- ✅ Documentation complète (8 fichiers markdown)

#### Structure du projet

```
E:\project\
├── source/              # Backend Python
├── templates/           # Frontend HTML
├── static/
│   ├── css/            # Styles
│   └── js/             # JavaScript
├── docs/               # Documentation
└── requirements.txt    # Dépendances
```

#### Technologies utilisées

- Python 3.7+
- Flask + Flask-CORS
- Leaflet.js 1.9.4
- HTML5 + CSS3 + JavaScript vanilla

---

## Convention de versionnement

Ce projet suit le versionnement sémantique (SemVer):
- **MAJOR**: Changements incompatibles avec versions précédentes
- **MINOR**: Nouvelles fonctionnalités rétrocompatibles
- **PATCH**: Corrections de bugs rétrocompatibles

Format: `MAJOR.MINOR.PATCH` (ex: 1.0.1)

---

## Légende

- 🎉 Nouvelle version majeure
- ✨ Nouvelle fonctionnalité
- 🐛 Correction de bug
- 📚 Documentation
- 🔄 Mise à jour
- ⚡ Amélioration performance
- 🔒 Sécurité
- ⚠️ Dépréciation
- 💥 Breaking change

---

**Dernière mise à jour:** 2026-03-09
