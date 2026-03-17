"""
Structure de données pour représenter un graphe de transports à Madagascar
Implémentation manuelle sans bibliothèques externes
"""

class Node:
    """Représente un nœud (localité) dans le graphe"""
    def __init__(self, name, latitude=0, longitude=0):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.edges = []  # Liste des arêtes partant de ce nœud
    
    def add_edge(self, edge):
        """Ajoute une arête à ce nœud"""
        self.edges.append(edge)
    
    def get_neighbors(self):
        """Retourne la liste des nœuds voisins avec les coûts"""
        neighbors = []
        for edge in self.edges:
            neighbors.append({
                'node': edge.destination,
                'distance': edge.distance,
                'duration': edge.duration,
                'price': edge.price,
                'transport_types': edge.transport_types
            })
        return neighbors
    
    def __repr__(self):
        return f"Node({self.name})"
    
    def __eq__(self, other):
        return self.name == other.name
    
    def __hash__(self):
        return hash(self.name)


class Edge:
    """Représente une arête (connexion) entre deux nœuds"""
    def __init__(self, source, destination, distance, duration, price, transport_types):
        self.source = source
        self.destination = destination
        self.distance = distance  # en km
        self.duration = duration  # en minutes
        self.price = price  # en ariary
        self.transport_types = transport_types  # liste des types de transport disponibles
    
    def __repr__(self):
        return f"Edge({self.source.name} -> {self.destination.name}, {self.distance}km, {self.duration}min, {self.price}Ar)"


class Graph:
    """Représente le graphe de transports"""
    def __init__(self):
        self.nodes = {}  # Dictionnaire {nom: Node}
        self.edges = []
    
    def add_node(self, name, latitude=0, longitude=0):
        """Ajoute un nœud au graphe"""
        if name not in self.nodes:
            node = Node(name, latitude, longitude)
            self.nodes[name] = node
            return node
        return self.nodes[name]
    
    def add_edge(self, source_name, destination_name, distance, duration, price, transport_types):
        """Ajoute une arête entre deux nœuds"""
        source = self.nodes.get(source_name)
        destination = self.nodes.get(destination_name)
        
        if source is None or destination is None:
            raise ValueError(f"Nœud source ou destination non trouvé")
        
        edge = Edge(source, destination, distance, duration, price, transport_types)
        source.add_edge(edge)
        self.edges.append(edge)
        return edge
    
    def get_node(self, name):
        """Récupère un nœud par son nom"""
        return self.nodes.get(name)
    
    def get_all_nodes(self):
        """Retourne la liste de tous les nœuds"""
        return list(self.nodes.values())
    
    def get_path_info(self, path):
        """Calcule les informations d'un chemin (distance totale, durée, prix)"""
        total_distance = 0
        total_duration = 0
        total_price = 0
        
        for i in range(len(path) - 1):
            current_node = path[i]
            next_node = path[i + 1]
            
            # Trouver l'arête
            for edge in current_node.edges:
                if edge.destination == next_node:
                    total_distance += edge.distance
                    total_duration += edge.duration
                    total_price += edge.price
                    break
        
        return {
            'distance': total_distance,
            'duration': total_duration,
            'price': total_price
        }
    
    def __repr__(self):
        return f"Graph({len(self.nodes)} nodes, {len(self.edges)} edges)"
