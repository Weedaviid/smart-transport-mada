"""
Algorithme de Dijkstra pour trouver le chemin le plus court
Implémentation manuelle sans bibliothèques externes
"""

def dijkstra(graph, start_name, end_name, weight='distance'):
    """
    Algorithme de Dijkstra pour trouver le chemin le plus court
    
    Args:
        graph: Le graphe de transports
        start_name: Nom du nœud de départ
        end_name: Nom du nœud d'arrivée
        weight: 'distance', 'duration', ou 'price' - métrique à minimiser
    
    Returns:
        dict avec 'path' (liste de nœuds) et 'cost' (le coût total)
    """
    start_node = graph.get_node(start_name)
    end_node = graph.get_node(end_name)
    
    if start_node is None or end_node is None:
        return {'path': [], 'cost': float('inf'), 'error': 'Nœud non trouvé'}
    
    if start_node == end_node:
        return {'path': [start_node], 'cost': 0}
    
    # Initialiser les distances, durées, et prix
    distances = {}
    durations = {}
    prices = {}
    visited = {}
    previous = {}
    
    # Initialiser tous les nœuds
    for node_name, node in graph.nodes.items():
        distances[node_name] = float('inf')
        durations[node_name] = float('inf')
        prices[node_name] = float('inf')
        visited[node_name] = False
        previous[node_name] = None
    
    # La distance/durée/prix du nœud de départ est 0
    distances[start_name] = 0
    durations[start_name] = 0
    prices[start_name] = 0
    
    # Sélectionner la métrique à utiliser
    if weight == 'duration':
        costs = durations
    elif weight == 'price':
        costs = prices
    else:  # par défaut 'distance'
        costs = distances
    
    # Boucle principale de Dijkstra
    unvisited_count = len(graph.nodes)
    
    while unvisited_count > 0:
        # Trouver le nœud non visité avec le coût minimum
        min_cost = float('inf')
        current_node_name = None
        
        for node_name in graph.nodes:
            if not visited[node_name] and costs[node_name] < min_cost:
                min_cost = costs[node_name]
                current_node_name = node_name
        
        # Si on n'a pas trouvé de nœud (graphe déconnecté)
        if current_node_name is None:
            break
        
        current_node = graph.nodes[current_node_name]
        visited[current_node_name] = True
        unvisited_count -= 1
        
        # Si on a atteint le nœud de destination
        if current_node_name == end_name:
            break
        
        # Examiner les voisins
        for neighbor_info in current_node.get_neighbors():
            neighbor = neighbor_info['node']
            edge_distance = neighbor_info['distance']
            edge_duration = neighbor_info['duration']
            edge_price = neighbor_info['price']
            
            if not visited[neighbor.name]:
                # Calculer les nouveaux coûts
                new_distance = distances[current_node_name] + edge_distance
                new_duration = durations[current_node_name] + edge_duration
                new_price = prices[current_node_name] + edge_price
                
                # Mettre à jour si on trouve une meilleure route
                if weight == 'duration' and new_duration < durations[neighbor.name]:
                    durations[neighbor.name] = new_duration
                    distances[neighbor.name] = new_distance
                    prices[neighbor.name] = new_price
                    previous[neighbor.name] = current_node
                elif weight == 'price' and new_price < prices[neighbor.name]:
                    prices[neighbor.name] = new_price
                    distances[neighbor.name] = new_distance
                    durations[neighbor.name] = new_duration
                    previous[neighbor.name] = current_node
                elif (weight != 'duration' and weight != 'price') and new_distance < distances[neighbor.name]:
                    distances[neighbor.name] = new_distance
                    durations[neighbor.name] = new_duration
                    prices[neighbor.name] = new_price
                    previous[neighbor.name] = current_node
    
    # Reconstruire le chemin
    path = []
    current = end_node
    
    while current is not None:
        path.insert(0, current)
        current = previous[current.name]
    
    # Vérifier si un chemin a été trouvé
    if path[0] != start_node:
        return {'path': [], 'cost': float('inf'), 'error': 'Pas de chemin trouvé'}
    
    # Récupérer le coût final
    final_cost = costs[end_name]
    
    result = {
        'path': path,
        'cost': final_cost,
        'distance': distances[end_name],
        'duration': durations[end_name],
        'price': prices[end_name],
        'algorithm': 'Dijkstra',
        'weight': weight
    }
    
    return result
