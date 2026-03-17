"""
Algorithme A* pour trouver le chemin le plus court avec heuristique
Implémentation manuelle sans bibliothèques externes
"""

import math

def distance_euclidienne(lat1, lon1, lat2, lon2):
    """
    Calcule la distance euclidienne entre deux points
    (approximation simple pour Madagascar)
    """
    lat_diff = lat2 - lat1
    lon_diff = lon2 - lon1
    return math.sqrt(lat_diff ** 2 + lon_diff ** 2)


class PriorityQueue:
    """File de priorité simple implémentée manuellement"""
    def __init__(self):
        self.items = []
    
    def add(self, item, priority):
        """Ajoute un élément avec sa priorité"""
        self.items.append((priority, item))
        # Trier après chaque ajout
        self._sort()
    
    def _sort(self):
        """Trie les éléments par priorité (très simple, pas optimisé)"""
        for i in range(len(self.items)):
            for j in range(i + 1, len(self.items)):
                if self.items[j][0] < self.items[i][0]:
                    self.items[i], self.items[j] = self.items[j], self.items[i]
    
    def pop(self):
        """Récupère et retire l'élément avec la plus petite priorité"""
        if len(self.items) > 0:
            return self.items.pop(0)[1]
        return None
    
    def is_empty(self):
        """Vérifie si la file est vide"""
        return len(self.items) == 0
    
    def contains(self, item):
        """Vérifie si un élément est dans la file"""
        for priority, i in self.items:
            if i == item:
                return True
        return False


def heuristic_distance(current_node, goal_node, weight='distance'):
    """
    Heuristique pour A*: distance euclidienne approximée
    Utile pour guider la recherche vers l'objectif
    """
    if weight == 'price' or weight == 'duration':
        # Pour le prix et la durée, on peut utiliser la distance comme proxy
        distance_km = distance_euclidienne(
            current_node.latitude, current_node.longitude,
            goal_node.latitude, goal_node.longitude
        )
        if weight == 'price':
            # Approximation: 50 Ar par km (prix moyen)
            return distance_km * 50
        else:  # duration
            # Approximation: 40 km/h moyenne
            return (distance_km / 40) * 60  # en minutes
    else:  # distance
        return distance_euclidienne(
            current_node.latitude, current_node.longitude,
            goal_node.latitude, goal_node.longitude
        )


def astar(graph, start_name, end_name, weight='distance'):
    """
    Algorithme A* pour trouver le chemin le plus court
    
    Args:
        graph: Le graphe de transports
        start_name: Nom du nœud de départ
        end_name: Nom du nœud d'arrivée
        weight: 'distance', 'duration', ou 'price' - métrique à minimiser
    
    Returns:
        dict avec 'path' (liste de nœuds), 'cost', et autres informations
    """
    start_node = graph.get_node(start_name)
    end_node = graph.get_node(end_name)
    
    if start_node is None or end_node is None:
        return {'path': [], 'cost': float('inf'), 'error': 'Nœud non trouvé'}
    
    if start_node == end_node:
        return {'path': [start_node], 'cost': 0}
    
    # Initialiser les structures
    open_set = PriorityQueue()
    closed_set = set()
    came_from = {}
    
    # g_score: coût réel du nœud de départ à ce nœud
    g_score = {}
    # f_score: g_score + heuristique
    f_score = {}
    
    for node in graph.get_all_nodes():
        g_score[node.name] = float('inf')
        f_score[node.name] = float('inf')
    
    g_score[start_name] = 0
    h_score = heuristic_distance(start_node, end_node, weight)
    f_score[start_name] = h_score
    
    open_set.add(start_node, f_score[start_name])
    
    # Boucle principale
    while not open_set.is_empty():
        current = open_set.pop()
        
        if current == end_node:
            # Reconstruire le chemin
            path = [current]
            while current.name in came_from:
                current = came_from[current.name]
                path.insert(0, current)
            
            # Calculer les métriques
            info = graph.get_path_info(path)
            
            result = {
                'path': path,
                'cost': g_score[end_name],
                'distance': info['distance'],
                'duration': info['duration'],
                'price': info['price'],
                'algorithm': 'A*',
                'weight': weight
            }
            return result
        
        closed_set.add(current.name)
        
        # Examiner les voisins
        for neighbor_info in current.get_neighbors():
            neighbor = neighbor_info['node']
            edge_distance = neighbor_info['distance']
            edge_duration = neighbor_info['duration']
            edge_price = neighbor_info['price']
            
            if neighbor.name in closed_set:
                continue
            
            # Sélectionner le coût d'arête basé sur le poids
            if weight == 'duration':
                edge_cost = edge_duration
            elif weight == 'price':
                edge_cost = edge_price
            else:  # distance
                edge_cost = edge_distance
            
            tentative_g_score = g_score[current.name] + edge_cost
            
            if tentative_g_score < g_score[neighbor.name]:
                # Ce chemin est meilleur
                came_from[neighbor.name] = current
                g_score[neighbor.name] = tentative_g_score
                
                h_score = heuristic_distance(neighbor, end_node, weight)
                f_score[neighbor.name] = g_score[neighbor.name] + h_score
                
                if not open_set.contains(neighbor):
                    open_set.add(neighbor, f_score[neighbor.name])
    
    # Pas de chemin trouvé
    return {'path': [], 'cost': float('inf'), 'error': 'Pas de chemin trouvé'}
