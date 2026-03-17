# Livrable Algorithmique - TransMad

## 1. Problemes algorithmiques du projet

### 1.1 Definition
Le projet TransMad cherche a calculer un meilleur trajet entre un point de depart et un point d'arrivee dans Antananarivo, en prenant en compte plusieurs modes de transport (taxi, taxi-brousse, moto-taxi, pousse-pousse, bus, marche).

Le probleme est un plus court chemin sur graphe pondere multi-critere:
- minimiser la distance totale
- ou minimiser la duree totale
- ou minimiser le prix total

### 1.2 Entrees
- `start`: nom du noeud de depart
- `end`: nom du noeud d'arrivee
- `optimization`: `distance | duration | price`
- graphe de transport construit depuis les donnees JSON (`cities.json`, `roads.json`, `bus_stops.json`, `bus_routes.json`, `walk_connections.json`)

### 1.3 Sorties
- `path`: sequence ordonnee des noeuds
- `distance`: distance totale (km)
- `duration`: duree totale (minutes)
- `price`: cout total (Ar)
- `algorithm`: algorithme utilise (`A*` ou `Dijkstra`)
- en cas d'echec: message d'erreur (`Noeud non trouve`, `Pas de chemin trouve`)

## 2. Modeles

### 2.1 Modele graphe
Le reseau est modele par un graphe oriente pondere `G = (V, E)`:
- `V`: villes + arrets de bus
- `E`: connexions routieres, connexions pietonnes, segments de bus

Chaque arete contient:
- `distance` (km)
- `duration` (minutes)
- `price` (Ar)
- `transport_types` (liste)

### 2.2 Contraintes
- poids non-negatifs (condition necessaire pour Dijkstra)
- lignes de bus fixes (pas de detour libre)
- bus avec tarif fixe (600 Ar)
- temps d'arret bus: +1 minute par arret
- marche a pied: 50 m/min (3 km/h)

### 2.3 Metriques optimisees
- Distance: somme des distances
- Duree: somme des durees
- Prix: somme des prix

### 2.4 Hypotheses
- Donnees JSON coherentes et noms de noeuds valides
- Graphe majoritairement connexe pour les zones cibles
- Conditions trafic deja integrees dans `roads.json` via `traffic_factor`
- Heuristique A* basee sur distance euclidienne (approximation locale)

## 3. Algorithmes choisis

### 3.1 Dijkstra
Utilise pour obtenir le chemin optimal exact sur poids non-negatifs.

Pseudo-code (synthetique):
```text
DIJKSTRA(G, start, end, weight):
  init cost[v] = inf, prev[v] = null, visited[v] = false
  cost[start] = 0
  while il existe un noeud non visite:
    u = noeud non visite avec cout minimal
    marquer u visite
    si u == end: break
    pour chaque voisin v de u:
      new_cost = cost[u] + edge_cost(u, v, weight)
      si new_cost < cost[v]:
        cost[v] = new_cost
        prev[v] = u
  reconstruire le chemin avec prev
  retourner chemin + metriques
```

### 3.2 A*
Utilise par defaut dans l'API pour accelerer la recherche avec une heuristique.

Pseudo-code (synthetique):
```text
ASTAR(G, start, end, weight):
  open_set = file de priorite
  g[start] = 0
  f[start] = h(start, end)
  ajouter start dans open_set
  while open_set non vide:
    u = extraire plus petite priorite
    si u == end: reconstruire chemin et retourner
    pour chaque voisin v de u:
      tentative = g[u] + edge_cost(u, v, weight)
      si tentative < g[v]:
        came_from[v] = u
        g[v] = tentative
        f[v] = g[v] + h(v, end)
        ajouter v si absent
  retourner echec
```

### 3.3 Heuristique A*
- `distance`: distance euclidienne
- `duration`: distance euclidienne convertie en minutes
- `price`: distance euclidienne convertie en cout estime

## 4. Structures de donnees

### 4.1 Definitions
- `Node` (`source/graph.py`): nom, latitude, longitude, liste d'aretes sortantes
- `Edge` (`source/graph.py`): source, destination, distance, duration, price, transport_types
- `Graph` (`source/graph.py`): dictionnaire de noeuds + liste globale d'aretes
- `PriorityQueue` (`source/astar.py`): liste triee manuellement de couples `(priority, item)`

### 4.2 Integration dans le code
- Construction du graphe dans `source/database.py`
- Recherche de chemin dans `source/astar.py` et `source/dijkstra.py`
- Exposition API dans `source/app.py` (`/api/find-route`)

## 5. Complexite (temps/memoire)

### 5.1 Dijkstra actuel
Implementation sans tas binaire:
- Temps: `O(V^2 + E)` (selection lineaire du minimum)
- Memoire: `O(V + E)`

Justification:
- a chaque iteration, recherche du noeud min par balayage de tous les noeuds (`O(V)`), repete `V` fois

### 5.2 A* actuel
`PriorityQueue` est une liste triee a chaque insertion:
- insertion: `O(n^2)` dans le pire cas (tri par doubles boucles)
- pop min: `O(1)`
- complexite globale empirique: superieure a A* standard base tas binaire
- Memoire: `O(V + E)`

Justification:
- la file de priorite actuelle n'utilise pas `heapq`
- malgre cela, l'heuristique reduit souvent le nombre de noeuds explores

### 5.3 Remarque optimisation
Une evolution naturelle serait:
- remplacer la `PriorityQueue` manuelle par un tas binaire (`heapq`)
- passer Dijkstra a `O((V+E) log V)`

## 6. Validation

### 6.1 Tests unitaires
Un dossier `tests/` a ete ajoute avec tests sur:
- structures de donnees du graphe
- Dijkstra et A* en mode nominal
- gestion des erreurs (noeuds invalides, graphe deconnecte)
- coherence des metriques selon `weight`

Commande:
```powershell
py -m unittest discover -s tests -v
```

### 6.2 Tests de charge (petit protocole)
Protocole implemente dans `tests/test_load_algorithms.py`:
1. generation d'un graphe de grille `N x N`
2. execution repetee de Dijkstra et A*
3. mesure des temps moyens
4. verification:
   - chemin trouve
   - couts coherents entre algorithmes
   - temps global de test sous borne raisonnable

## 7. Resultats (baseline vs optimise)

### 7.1 Baseline
- graphe sans bus/marche
- optimisation principalement route directe

### 7.2 Optimise (etat actuel)
- graphe multi-modal (vehicules + bus + marche)
- cout prix plus realiste grace au bus (tarif fixe) et marche gratuite
- visualisation route reelle via OSRM (frontend)

### 7.3 Tableau comparatif

| Critere | Baseline | Optimise |
|---|---|---|
| Noeuds | villes seulement | villes + arrets bus |
| Modes | 4 modes routiers | 6 modes (ajout bus + marche) |
| Prix bus | non gere | tarif unique 600 Ar |
| Arrets bus | non geres | +1 min par arret |
| Connexions pietonnes | non gerees | marche 50 m/min |
| Realisme de tracage carte | segment direct | OSRM (routes reelles) |
| Robustesse testee | limitee | tests unitaires + charge |

## Conclusion
Le systeme satisfait les exigences techniques initiales:
- modelisation graphe multi-critere
- algorithmes explicites (Dijkstra, A*)
- structures de donnees integrees au code
- complexite analysee
- validation par tests unitaires et charge
- comparaison baseline vs version optimisee

Ce livrable sert de reference technique pour la soutenance et la maintenance.
