"""
Base de données pour les localités et transports à Madagascar
Chargement depuis fichiers JSON avec distances réelles
"""

import json
import os
from graph import Graph


class TransportDatabase:
    """Gestionnaire de la base de données des transports chargés depuis JSON"""
    
    def __init__(self):
        self.graph = Graph()
        self.cities = {}
        self.roads = []
        self.transports = {}
        self.bus_stops = {}
        self.walk_connections = []
        self.bus_routes = []
        self.bus_fare = 600
        
        # Charger les données JSON
        self._load_json_data()
        
        # Configurer le graphe
        self._setup_locations()
        self._setup_routes()
        self._setup_bus_system()
    
    def _load_json_data(self):
        """Charge les données depuis les fichiers JSON"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, 'data')
        
        # Charger cities.json
        cities_path = os.path.join(data_dir, 'cities.json')
        with open(cities_path, 'r', encoding='utf-8') as f:
            cities_data = json.load(f)
            self.cities = {city['id']: city for city in cities_data['cities']}
        
        # Charger roads.json
        roads_path = os.path.join(data_dir, 'roads.json')
        with open(roads_path, 'r', encoding='utf-8') as f:
            roads_data = json.load(f)
            self.roads = roads_data['roads']
        
        # Charger transports.json
        transports_path = os.path.join(data_dir, 'transports.json')
        with open(transports_path, 'r', encoding='utf-8') as f:
            transports_data = json.load(f)
            self.transports = {t['id']: t for t in transports_data['transports']}
        
        # Charger bus_stops.json
        bus_stops_path = os.path.join(data_dir, 'bus_stops.json')
        with open(bus_stops_path, 'r', encoding='utf-8') as f:
            bus_stops_data = json.load(f)
            self.bus_stops = {stop['name']: stop for stop in bus_stops_data['bus_stops']}
        
        # Charger walk_connections.json
        walk_connections_path = os.path.join(data_dir, 'walk_connections.json')
        with open(walk_connections_path, 'r', encoding='utf-8') as f:
            walk_data = json.load(f)
            self.walk_connections = walk_data['walk_connections']
        
        # Charger bus_routes.json
        bus_routes_path = os.path.join(data_dir, 'bus_routes.json')
        with open(bus_routes_path, 'r', encoding='utf-8') as f:
            bus_routes_data = json.load(f)
            self.bus_routes = bus_routes_data['bus_routes']
            self.bus_fare = bus_routes_data['fare']['price_ar']
        
        # Configuration des emojis et couleurs pour compatibilité
        self.TRANSPORT_TYPES = {
            'taxi-brousse': {
                'emoji': '🚌', 
                'color': '#FF6B6B', 
                'price_per_km': self.transports['taxi-brousse']['price_per_km']
            },
            'taxi': {
                'emoji': '🚖', 
                'color': '#4ECDC4', 
                'price_per_km': self.transports['taxi']['price_per_km']
            },
            'moto-taxi': {
                'emoji': '🏍️', 
                'color': '#FFE66D', 
                'price_per_km': self.transports['moto-taxi']['price_per_km']
            },
            'pousse-pousse': {
                'emoji': '🛺', 
                'color': '#95E1D3', 
                'price_per_km': self.transports['pousse-pousse']['price_per_km']
            },
            'bus': {
                'emoji': '🚍',
                'color': '#FFA500',
                'price_per_km': 0,
                'price_fixed': self.bus_fare
            },
            'walk': {
                'emoji': '🚶',
                'color': '#90EE90',
                'price_per_km': 0,
                'price_fixed': 0
            }
        }
    
    def _setup_locations(self):
        """Configure toutes les localités et arrêts de bus dans le graphe"""
        # Ajouter les villes
        for city_id, city in self.cities.items():
            self.graph.add_node(
                city['name'],
                latitude=city['latitude'],
                longitude=city['longitude']
            )
        
        # Ajouter les arrêts de bus
        for stop_name, stop in self.bus_stops.items():
            self.graph.add_node(
                stop_name,
                latitude=stop['lat'],
                longitude=stop['lon']
            )
    
    def _setup_routes(self):
        """Configure les routes entre localités depuis roads.json"""
        # Pour chaque route, créer des arêtes bidirectionnelles pour les transports standards
        for road in self.roads:
            # Récupérer les noms de villes depuis les IDs
            from_city = self.cities[road['from']]['name']
            to_city = self.cities[road['to']]['name']
            distance_km = road['distance_km']
            traffic_factor = road.get('traffic_factor', 1.0)
            
            # Pour chaque type de transport STANDARD (pas bus ni marche)
            for transport_id, transport in self.transports.items():
                # Exclure bus et marche qui ont une logique spéciale
                if transport_id in ['bus', 'walk']:
                    continue
                
                # Calculer le temps de trajet en minutes
                # Formule: distance / vitesse * 60 * facteur_traffic
                base_time = (distance_km / transport['speed_kmh']) * 60
                duration = int(base_time * traffic_factor)
                
                # Calculer le prix
                price = int(distance_km * transport['price_per_km'])
                
                # Ajouter l'arête dans le sens from -> to
                self.graph.add_edge(
                    from_city, to_city,
                    distance=distance_km,
                    duration=duration,
                    price=price,
                    transport_types=[transport_id]
                )
                
                # Ajouter l'arête dans le sens inverse to -> from
                self.graph.add_edge(
                    to_city, from_city,
                    distance=distance_km,
                    duration=duration,
                    price=price,
                    transport_types=[transport_id]
                )
    
    def _setup_bus_system(self):
        """Configure le système de bus et les connexions piétonnes"""
        
        # 1. CONNEXIONS PIÉTONNES (ville <-> arrêt de bus)
        walk_transport = self.transports.get('walk')
        if walk_transport:
            for connection in self.walk_connections:
                from_loc = connection['from']
                to_loc = connection['to']
                distance_km = connection['distance_km']
                
                # Temps de marche: 50 m/min = 0.05 km/min
                walk_time = int((distance_km * 1000) / 50)  # distance en mètres / 50 m/min
                
                # Ajouter connexions bidirectionnelles
                self.graph.add_edge(
                    from_loc, to_loc,
                    distance=distance_km,
                    duration=walk_time,
                    price=0,
                    transport_types=['walk']
                )
                
                self.graph.add_edge(
                    to_loc, from_loc,
                    distance=distance_km,
                    duration=walk_time,
                    price=0,
                    transport_types=['walk']
                )
        
        # 2. ROUTES DE BUS (trajets fixes)
        bus_transport = self.transports.get('bus')
        if bus_transport:
            for bus_line in self.bus_routes:
                segments = bus_line['segments']
                
                # Pour chaque segment de la ligne de bus
                for segment in segments:
                    from_stop = segment['from']
                    to_stop = segment['to']
                    distance_km = segment['distance_km']
                    stop_time = segment.get('stop_time_minutes', 1)
                    
                    # Temps de trajet en bus: distance / vitesse + temps d'arrêt
                    travel_time = int((distance_km / bus_transport['speed_kmh']) * 60)
                    total_time = travel_time + stop_time
                    
                    # Prix: tarif unique du bus
                    price = self.bus_fare
                    
                    # Ajouter connexions bidirectionnelles
                    self.graph.add_edge(
                        from_stop, to_stop,
                        distance=distance_km,
                        duration=total_time,
                        price=price,
                        transport_types=['bus']
                    )
                    
                    self.graph.add_edge(
                        to_stop, from_stop,
                        distance=distance_km,
                        duration=total_time,
                        price=price,
                        transport_types=['bus']
                    )
    
    def get_graph(self):
        """Retourne le graphe des transports"""
        return self.graph
    
    def get_all_localities(self):
        """Retourne la liste de toutes les localités"""
        localities = []
        for node_name, node in self.graph.nodes.items():
            localities.append({
                'name': node_name,
                'latitude': node.latitude,
                'longitude': node.longitude
            })
        return sorted(localities, key=lambda x: x['name'])
    
    def get_transport_info(self, transport_type):
        """Retourne les informations d'un type de transport"""
        return self.TRANSPORT_TYPES.get(transport_type)
    
    def get_all_transport_types(self):
        """Retourne tous les types de transport disponibles"""
        return self.TRANSPORT_TYPES
    
    def get_cheapest_transport(self, distance_km, available_transports=None):
        """
        Retourne le transport le moins cher pour une distance donnée
        
        Args:
            distance_km: Distance en km
            available_transports: Liste des transports disponibles (None = tous)
        
        Returns:
            dict avec le nom du transport et le prix estimé
        """
        if available_transports is None:
            available_transports = list(self.TRANSPORT_TYPES.keys())
        
        cheapest = None
        min_price = float('inf')
        
        for transport in available_transports:
            if transport in self.TRANSPORT_TYPES:
                price = self.TRANSPORT_TYPES[transport]['price_per_km'] * distance_km
                if price < min_price:
                    min_price = price
                    cheapest = transport
        
        return {
            'transport': cheapest,
            'estimated_price': min_price if cheapest else 0
        }
    
    @staticmethod
    def calculate_route_time_optimized(distance_km, transport_type):
        """
        Calcule le temps optimisé pour une route
        Basé sur les vitesses moyennes définies dans transports.json
        """
        # Charger les vitesses depuis transports.json
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, 'data')
        transports_path = os.path.join(data_dir, 'transports.json')
        
        with open(transports_path, 'r', encoding='utf-8') as f:
            transports_data = json.load(f)
            speeds = {t['id']: t['speed_kmh'] for t in transports_data['transports']}
        
        speed = speeds.get(transport_type, 30)
        time_hours = distance_km / speed
        time_minutes = int(time_hours * 60)
        
        return time_minutes


# Singleton pour la base de données
_db = None

def get_database():
    """Retourne l'instance singleton de la base de données"""
    global _db
    if _db is None:
        _db = TransportDatabase()
    return _db
