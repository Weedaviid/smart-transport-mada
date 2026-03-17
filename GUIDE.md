# 📖 Guide complet - TransMad

Guide d'installation, utilisation et test du système de transport TransMad.

---

## 🚀 Installation rapide (2 minutes)

### Prérequis
- Python 3.7+
- pip

### Étapes

```powershell
# 1. Aller dans le dossier
cd E:\project

# 2. Installer les dépendances
pip install flask flask-cors

# 3. Lancer le serveur
py source/app.py
```

Vous verrez:
```
✓ Running on http://127.0.0.1:5000
```

### Ouvrir le site
Navigateur → **http://localhost:5000**

---

## ⚙️ Configuration avancée

### Routes réelles avec OSRM

Le système utilise par défaut **OSRM** (Open Source Routing Machine) pour afficher des routes qui suivent les vraies rues au lieu de lignes droites.

**Fonctionnement automatique** :
- ✅ Activé par défaut
- ✅ Gratuit, sans clé API
- ✅ Routes suivent les rues réelles
- ✅ Fallback automatique si indisponible

**Pour désactiver OSRM** (revenir aux lignes droites) :

Éditer `static/js/routing-config.js` :
```javascript
const ROUTING_CONFIG = {
    useOSRM: false,  // Changer à false
    // ...
};
```

### Google Maps API (optionnel)

Pour une précision maximale avec trafic en temps réel :

**1. Obtenir une clé API**
- Aller sur [Google Cloud Console](https://console.cloud.google.com/)
- Créer un projet
- Activer : Directions API + Maps JavaScript API
- Créer une clé API

**2. Configurer TransMad**

Éditer `static/js/routing-config.js` :
```javascript
googleMaps: {
    enabled: true,  // Activer
    apiKey: 'VOTRE_CLE_API_ICI',  // Votre clé
}
```

**3. Ajouter le script Google Maps**

Éditer `templates/index.html`, ajouter avant `</head>` :
```html
<script src="https://maps.googleapis.com/maps/api/js?key=VOTRE_CLE&libraries=geometry"></script>
```

**Coûts Google Maps** :
- 5 premiers USD/mois : gratuit
- Après : ~5 USD / 1000 requêtes
- [Voir la tarification](https://mapsplatform.google.com/pricing/)

### Modifier les coordonnées des villes

Les coordonnées des 15 villes sont dans `data/cities.json` :

```json
{
  "id": "analakely",
  "name": "Analakely",
  "latitude": -18.9067075792458,  // 8 décimales = précision ±1mm
  "longitude": 47.52638894151368,
  "description": "Centre commercial d'Antananarivo"
}
```

**Pour trouver des coordonnées précises** :
1. Ouvrir [Google Maps](https://maps.google.com)
2. Clic droit sur un lieu → "Plus d'infos sur cet endroit"
3. Copier les coordonnées (latitude, longitude)

**Précision GPS** :
- 4 décimales = ±11 mètres
- 6 décimales = ±11 cm
- 8 décimales = ±1.1 mm ✅ (utilisé actuellement)

---

## 🎮 Utilisation

### Option 1: Présets (recommandé)

Cliquez simplement un des 4 boutons de trajets prédéfinis:
- **Analakely → Ivato** (Aéroport)
- **Analakely → Ambatobe**
- **Isoraka → Ivandry**
- **Anosy → Talatamaty**

Le trajet s'affiche automatiquement avec carte interactive.

### Option 2: Recherche manuelle

1. Sélectionner départ
2. Sélectionner destination
3. Choisir optimisation: **Distance** / **Durée** / **Prix**
4. Cliquer "Trouver mon trajet"

### 🚍 Utiliser le Bus Public (Nouveau!)

Pour trouver un trajet en bus économique :

1. Choisir optimisation : **💰 Prix le moins cher**
2. Le système propose automatiquement le bus si c'est l'option la plus économique

**Exemple** :
- Départ : **Analakely**
- Destination : **Mahamasina Bus Stop**
- Optimisation : **Prix**
- Résultat : Marche + Bus = **1,200 Ar** (vs 15,000 Ar en taxi)

**Économie : 92% !**

### 🚶 Marche à Pied

La marche est intégrée automatiquement :
- **Gratuit** (0 Ar)
- **50 m/min** (3 km/h)
- Utilisé pour connexions vers arrêts de bus
- Peut être un trajet complet pour courtes distances

---

## 🧪 Tests

### Tester les algorithmes

```powershell
# Tous les tests
py source/test.py

# Test spécifique
py source/test.py graph
py source/test.py performance
py source/test.py compare "Analakely" "Ivandry" "distance"
```

### Tester l'API

```powershell
# Health check
Invoke-WebRequest -Uri "http://localhost:5000/api/health" -UseBasicParsing

# Trouver trajet
$body = @{ start = "Analakely"; end = "Ivandry"; optimization = "distance" } | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:5000/api/find-route" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
```

---

## 🌐 API Endpoints

### 1. Liste des localités
```
GET /api/localities
```

### 2. Trouver un trajet
```
POST /api/find-route
Body: { "start": "Analakely", "end": "Ivandry", "optimization": "distance" }
```

### 3. GeoJSON pour carte
```
POST /api/route-geojson
Body: { "path": ["Analakely", "Ivandry"] }
```

### 4. Comparer transports
```
POST /api/compare-transports
Body: { "distance": 5.2 }
```

Voir la liste complète dans [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## 🔧 Dépannage

### Le serveur ne démarre pas

```powershell
# Vérifier Python
py --version

# Réinstaller dépendances
pip install flask flask-cors

# Arrêter anciens processus
Get-Process -Name py | Stop-Process -Force
py source/app.py
```

### Le site ne charge pas

1. Vérifier que le serveur tourne (voir terminal)
2. Tester: http://localhost:5000/api/health
3. Vider le cache: Ctrl+F5

### La carte n'apparaît pas

- Vérifier connexion internet (Leaflet via CDN)
- Ouvrir F12 → Console pour voir erreurs

**Pour plus de détails:** [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

## 📚 Documentation technique

- [ALGORITHMS.md](docs/ALGORITHMS.md) - Dijkstra et A*
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Structure du système
- [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Résolution problèmes

---

## 🎯 Localités disponibles

1. Analakely
2. Ivandry
3. Plateau Haute-Ville
4. Andohalo
5. Ambohiditra
6. Anjary
7. Anosibe
8. Tsimahafotsy
9. Betongitra
10. Antsorohavola

---

## 🚌 Transports disponibles

1. **Taxi-brousse** (long trajet, économique)
2. **Taxi** (confortable, moyen prix)
3. **Moto-taxi** (rapide, court trajet)
4. **Pousse-pousse** (très économique, lent)

---

**TransMad** - Système de transport intelligent pour Madagascar 🇲🇬
