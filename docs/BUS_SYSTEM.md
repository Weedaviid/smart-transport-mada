# 🚍 Système de Bus Public - TransMad

## Vue d'ensemble

TransMad intègre maintenant le **système de bus public d'Antananarivo** avec ses caractéristiques uniques :

- **Tarif unique** : 600 Ar pour tout trajet en bus, quelle que soit la distance
- **Trajets fixes** : Les bus suivent des lignes définies
- **Arrêts obligatoires** : +1 minute à chaque arrêt de bus
- **Connexions piétonnes** : Marche depuis/vers les arrêts de bus
- **Marche à pied** : 50 m/min = 3 km/h

---

## 📊 Données du Système

### 1. Arrêts de Bus (`data/bus_stops.json`)

**8 arrêts de bus** avec coordonnées GPS précises :

| ID | Nom | Latitude | Longitude |
|----|-----|----------|-----------|
| 1 | Analakely Bus Stop | -18.9087 | 47.5253 |
| 2 | Soarano Bus Stop | -18.9073 | 47.5189 |
| 3 | Mahamasina Bus Stop | -18.9130 | 47.5315 |
| 4 | Anosy Bus Stop | -18.9171 | 47.5273 |
| 5 | Kininina Ambohimirary | -18.9007 | 47.5452 |
| 6 | Meteo Ampasapito | -18.8986 | 47.5426 |
| 7 | Rond Point Ampasapito | -18.8979 | 47.5418 |
| 8 | Vingt Trois Ampasampito | -18.8965 | 47.5433 |

---

### 2. Lignes de Bus (`data/bus_routes.json`)

#### Ligne 1 : Analakely - Anosy
```
Analakely Bus Stop → Soarano (0.8 km, +1 min arrêt)
    ↓
Soarano Bus Stop → Mahamasina (1.5 km, +1 min arrêt)
    ↓
Mahamasina Bus Stop → Anosy (0.9 km, +1 min arrêt)
```

**Caractéristiques** :
- Distance totale : 3.2 km
- Temps arrêts : 3 minutes
- Prix : **600 Ar** (tarif unique)

#### Ligne 2 : Kininina - Ampasampito
```
Kininina Ambohimirary → Meteo Ampasapito (0.5 km, +1 min)
    ↓
Meteo Ampasapito → Rond Point (0.4 km, +1 min)
    ↓
Rond Point → Vingt Trois Ampasampito (0.3 km, +1 min)
```

**Caractéristiques** :
- Distance totale : 1.2 km
- Temps arrêts : 3 minutes
- Prix : **600 Ar** (tarif unique)

---

### 3. Connexions Piétonnes (`data/walk_connections.json`)

Les villes sont reliées aux arrêts de bus par la marche :

| Depuis (Ville) | Vers (Arrêt Bus) | Distance | Temps Marche |
|----------------|------------------|----------|--------------|
| Analakely | Analakely Bus Stop | 0.2 km | 4 min |
| Ankorondrano | Soarano Bus Stop | 1.1 km | 22 min |
| Ivandry | Meteo Ampasapito | 1.5 km | 30 min |
| Ambatobe | Vingt Trois Ampasampito | 1.8 km | 36 min |

**Formule temps de marche** :  
```
Temps (minutes) = Distance (mètres) / 50 m/min
Vitesse marche : 50 m/min = 3 km/h
```

---

## 💰 Comparaison Économique

### Exemple : Analakely → Anosy

#### Option 1 : Taxi direct
- Distance : ~2.8 km (via routes)
- Temps : ~7 minutes
- **Prix : 14,000 Ar** (5000 Ar/km)

#### Option 2 : Bus via arrêts
- Marche : Analakely → Analakely Bus Stop (0.2 km, 4 min)
- Bus : Analakely Bus Stop → Anosy Bus Stop (3.2 km, ~12 min)
- Total : 3.4 km, ~16 minutes
- **Prix : 600 Ar** (tarif unique bus)

**Économie : 13,400 Ar (95% moins cher !)**

---

## 🔄 Fonctionnement Algorithmique

### Graphe de Transport

Le système crée un **graphe unifié** avec :
- **Nœuds villes** : 15 localités d'Antananarivo
- **Nœuds arrêts** : 8 arrêts de bus
- **Arêtes routes** : Connexions entre villes (taxi, taxi-brousse, moto-taxi, pousse-pousse)
- **Arêtes piétonnes** : Connexions ville ↔ arrêt bus (walk)
- **Arêtes bus** : Connexions arrêt ↔ arrêt (bus)

### Exemple de Routing Multi-Modal

**Trajet : Analakely → Ivandry**

Le système compare automatiquement :

1. **Taxi direct** :
   ```
   Analakely --[taxi, 5km, 8min, 25000Ar]--> Ivandry
   ```

2. **Bus + Marche** :
   ```
   Analakely --[walk, 0.2km, 4min, 0Ar]--> Analakely Bus Stop
   Analakely Bus Stop --[bus, 0.8km, 3min, 600Ar]--> Soarano Bus Stop
   Soarano Bus Stop --[walk, 1.1km, 22min, 0Ar]--> Ankorondrano
   Ankorondrano --[taxi, 2km, 4min, 10000Ar]--> Ivandry
   Total: 4.1km, 33min, 10,600Ar
   ```

3. **Marche complète** (courtes distances) :
   ```
   Analakely --[walk, 5km, 100min, 0Ar]--> Ivandry
   ```

L'algorithme **Dijkstra** ou **A*** choisit automatiquement le meilleur selon l'optimisation :
- **Distance** : Taxi direct (5 km)
- **Temps** : Taxi direct (8 min)
- **Prix** : Bus + Marche (10,600 Ar)

---

## 🚶 Spécifications Techniques

### Transport : Bus
```json
{
  "id": "bus",
  "name": "Bus public",
  "speed_kmh": 20,
  "price_fixed": 600,
  "stop_time_minutes": 1
}
```

**Calcul temps total** :
```python
travel_time = (distance_km / 20) * 60  # minutes
total_time = travel_time + 1  # +1 minute d'arrêt
```

### Transport : Marche à Pied
```json
{
  "id": "walk",
  "name": "À pied",
  "speed_kmh": 3,
  "speed_m_per_min": 50,
  "price_fixed": 0
}
```

**Calcul temps** :
```python
walk_time = (distance_km * 1000) / 50  # minutes
```

---

## 📍 Cas d'Usage

### 1. Étudiant (Budget Limité)

**Besoin** : Analakely → Université Anosy  
**Optimisation** : Prix le moins cher

**Résultat** :
- Marche 4 min vers arrêt Analakely Bus Stop
- Bus Ligne 1 jusqu'à Anosy Bus Stop (600 Ar)
- Arrivée en 16 minutes pour **600 Ar**

---

### 2. Professionnel Pressé

**Besoin** : Analakely → Meeting Ivandry  
**Optimisation** : Temps optimisé

**Résultat** :
- Taxi direct
- Arrivée en 8 minutes pour **25,000 Ar**

---

### 3. Promenade Écologique

**Besoin** : Analakely → Parc proche (1 km)  
**Optimisation** : Gratuit + Écologique

**Résultat** :
- Marche à pied (50 m/min)
- Arrivée en 20 minutes pour **0 Ar**
- ✅ Écologique

---

## 🎮 Utilisation dans l'Interface

### Automatique (Recommandé)

1. Choisir départ et destination
2. Sélectionner optimisation (Distance / Temps / Prix)
3. Le système intègre **automatiquement** bus et marche si c'est optimal

### Exemple : Prix le moins cher

Si l'utilisateur cherche "Analakely → Anosy" avec optimisation **Prix** :
- Le système propose automatiquement le bus (600 Ar)
- Alternative taxi affichée (14,000 Ar)
- Économie de 13,400 Ar mise en évidence

---

## 📊 Statistiques

### Économies Potentielles

| Trajet | Taxi | Bus | Économie | % |
|--------|------|-----|----------|---|
| Analakely → Anosy | 14,000 Ar | 600 Ar | 13,400 Ar | 95% |
| Analakely → Soarano | 7,000 Ar | 600 Ar | 6,400 Ar | 91% |
| Ivandry → Ampasapito | 12,000 Ar | 600 Ar | 11,400 Ar | 95% |

### Temps de Trajet

| Distance | Taxi | Bus + Marche | Différence |
|----------|------|--------------|------------|
| < 2 km | 4 min | 12 min | +8 min |
| 2-5 km | 8 min | 20 min | +12 min |
| 5-10 km | 15 min | 35 min | +20 min |

**Trade-off** : Le bus est **20-30 minutes plus lent** mais **90%+ moins cher**

---

## 🔧 Configuration Avancée

### Ajouter une Ligne de Bus

**Fichier** : `data/bus_routes.json`

```json
{
  "line_id": "line_3",
  "line_name": "Ligne 3: Nouveau Trajet",
  "segments": [
    {
      "from": "Arrêt A",
      "to": "Arrêt B",
      "distance_km": 1.2,
      "stop_time_minutes": 1
    }
  ]
}
```

### Ajouter un Arrêt de Bus

**Fichier** : `data/bus_stops.json`

```json
{
  "id": 9,
  "name": "Nouvel Arrêt",
  "lat": -18.xxxx,
  "lon": 47.xxxx,
  "description": "Description"
}
```

### Ajouter une Connexion Piétonne

**Fichier** : `data/walk_connections.json`

```json
{
  "from": "Ville",
  "to": "Arrêt Bus",
  "distance_km": 0.5,
  "description": "Marche depuis Ville vers Arrêt"
}
```

---

## ✅ Tests

### Test 1 : Vérifier les arrêts de bus

```bash
GET /api/localities
```

**Résultat attendu** :
- 15 villes
- 8 arrêts de bus (noms avec "Bus Stop")

### Test 2 : Trajet avec bus

```bash
POST /api/find-route
{
  "start": "Analakely",
  "end": "Anosy",
  "transport": "bus"
}
```

**Résultat attendu** :
- Chemin : Analakely → Analakely Bus Stop (walk) → ... → Anosy
- Prix : 600 Ar (tarif bus unique)

---

## 🎯 Améliorations Futures

1. **Horaires de bus** : Ajouter les heures de passage
2. **Temps d'attente** : Intégrer le temps d'attente moyen (5-15 min)
3. **Lignes de bus réelles** : Importer les données officielles d'Antananarivo
4. **Cartes de bus** : Afficher les lignes de bus sur la carte avec couleurs distinctes
5. **Multi-modal intelligent** : Combiner plusieurs modes (bus + moto-taxi)
6. **Prix variable** : Tarifs différents selon les lignes (si applicable)

---

## 📚 Référence API

### Nouveaux Transports

```python
# Bus
{
  'id': 'bus',
  'emoji': '🚍',
  'price_fixed': 600,  # Ar
  'speed_kmh': 20,
  'stop_time_minutes': 1
}

# Marche
{
  'id': 'walk',
  'emoji': '🚶',
  'price_fixed': 0,  # Gratuit
  'speed_m_per_min': 50,  # 3 km/h
}
```

---

## 🎉 Conclusion

Le système de bus public est maintenant **intégré** dans TransMad ! Les utilisateurs peuvent :

✅ Économiser jusqu'à **95%** en utilisant le bus  
✅ Combiner marche + bus pour trajets économiques  
✅ Optimiser par prix, temps ou distance  
✅ Routes réelles via OSRM  
✅ Graphe unifié multi-modal

**Le transport public malgache est maintenant accessible dans TransMad ! 🚍**

---

*Documentation créée le 9 mars 2026*  
*Version TransMad : 1.3.0 - Intégration Bus Public*
