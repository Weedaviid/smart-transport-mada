"""
Application Flask pour le système de transport à Madagascar
API backend pour le calcul des trajets optimisés
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dijkstra import dijkstra
from astar import astar
from database import get_database
import json

app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')

CORS(app)

# Charger la base de données
db = get_database()
graph = db.get_graph()


@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')


@app.route('/api/localities', methods=['GET'])
def get_localities():
    """Retourne la liste de toutes les localités"""
    localities = db.get_all_localities()
    return jsonify({
        'success': True,
        'localities': localities
    })


@app.route('/api/transport-types', methods=['GET'])
def get_transport_types():
    """Retourne les types de transports disponibles"""
    transports = db.get_all_transport_types()
    formatted = []
    for name, info in transports.items():
        formatted.append({
            'id': name,
            'name': name.replace('-', ' ').title(),
            'emoji': info['emoji'],
            'color': info['color'],
            'price_per_km': info['price_per_km']
        })
    return jsonify({
        'success': True,
        'transports': formatted
    })


@app.route('/api/find-route', methods=['POST'])
def find_route():
    """
    Trouve le meilleur trajet entre deux localités
    Body: {
        "start": "Analakely",
        "end": "Ivandry",
        "optimization": "distance|duration|price"
    }
    """
    data = request.get_json()
    start = data.get('start')
    end = data.get('end')
    optimization = data.get('optimization', 'distance')
    
    if not start or not end:
        return jsonify({
            'success': False,
            'error': 'Départ et destination requis'
        }), 400
    
    if start == end:
        return jsonify({
            'success': False,
            'error': 'Le départ et la destination doivent être différents'
        }), 400
    
    # Mapper l'optimisation au poids Dijkstra/A*
    weight_map = {
        'distance': 'distance',
        'duration': 'duration',
        'price': 'price',
        'temps': 'duration',
        'prix': 'price'
    }
    weight = weight_map.get(optimization, 'distance')
    
    # Utiliser A* par défaut (plus efficace)
    result = astar(graph, start, end, weight=weight)
    
    if not result['path']:
        return jsonify({
            'success': False,
            'error': f"Pas de chemin trouvé entre {start} et {end}"
        }), 404
    
    # Formater le résultat
    path_names = [node.name for node in result['path']]
    
    # Obtenir le transport le moins cher pour la distance totale
    available_transports = None
    if len(result['path']) > 1:
        # Récupérer les transports disponibles pour le premier segment
        first_node = result['path'][0]
        neighbors = first_node.get_neighbors()
        if neighbors:
            available_transports = neighbors[0]['transport_types']
    
    cheapest = db.get_cheapest_transport(result['distance'], available_transports)
    
    return jsonify({
        'success': True,
        'path': path_names,
        'distance': result['distance'],
        'duration': result['duration'],
        'price': result['price'],
        'cheapest_transport': cheapest['transport'],
        'estimated_price': int(cheapest['estimated_price']),
        'algorithm': result['algorithm'],
        'optimization': weight,
        'segments': _build_segments(result['path'])
    })


@app.route('/api/route-info', methods=['POST'])
def get_route_info():
    """
    Retourne les informations détaillées d'un trajet
    Body: {
        "path": ["Analakely", "Ivandry"]
    }
    """
    data = request.get_json()
    path_names = data.get('path', [])
    
    if len(path_names) < 2:
        return jsonify({
            'success': False,
            'error': 'Au moins 2 localités requises'
        }), 400
    
    # Convertir les noms en nœuds
    path = []
    for name in path_names:
        node = graph.get_node(name)
        if node is None:
            return jsonify({
                'success': False,
                'error': f'Localité {name} non trouvée'
            }), 404
        path.append(node)
    
    info = graph.get_path_info(path)
    
    return jsonify({
        'success': True,
        'path': path_names,
        'distance': info['distance'],
        'duration': info['duration'],
        'price': info['price'],
        'segments': _build_segments(path)
    })


@app.route('/api/compare-transports', methods=['POST'])
def compare_transports():
    """
    Compare les différents types de transports pour un trajet
    Body: {
        "distance": 5.2
    }
    """
    data = request.get_json()
    distance = data.get('distance')
    
    if distance is None or distance <= 0:
        return jsonify({
            'success': False,
            'error': 'Distance valide requise'
        }), 400
    
    transports = db.get_all_transport_types()
    comparison = []
    
    for name, info in transports.items():
        estimated_price = info['price_per_km'] * distance
        estimated_time = db.calculate_route_time_optimized(distance, name)
        
        comparison.append({
            'name': name.replace('-', ' ').title(),
            'emoji': info['emoji'],
            'color': info['color'],
            'estimated_price': int(estimated_price),
            'estimated_time': estimated_time,
            'price_per_km': info['price_per_km']
        })
    
    # Trier par prix
    comparison.sort(key=lambda x: x['estimated_price'])
    
    return jsonify({
        'success': True,
        'distance': distance,
        'transports': comparison
    })


@app.route('/api/optimize-time', methods=['POST'])
def optimize_time():
    """
    Optimise le temps de trajet en sélectionnant le meilleur transport
    Body: {
        "distance": 5.2,
        "available_transports": ["taxi", "moto-taxi"]
    }
    """
    data = request.get_json()
    distance = data.get('distance')
    available = data.get('available_transports', list(db.get_all_transport_types().keys()))
    
    if distance is None or distance <= 0:
        return jsonify({
            'success': False,
            'error': 'Distance valide requise'
        }), 400
    
    best_time = float('inf')
    best_transport = None
    
    for transport in available:
        if transport in db.get_all_transport_types():
            time = db.calculate_route_time_optimized(distance, transport)
            if time < best_time:
                best_time = time
                best_transport = transport
    
    if best_transport is None:
        return jsonify({
            'success': False,
            'error': 'Aucun transport disponible'
        }), 404
    
    return jsonify({
        'success': True,
        'distance': distance,
        'best_transport': best_transport,
        'optimized_time': best_time,
        'emoji': db.get_transport_info(best_transport)['emoji']
    })


@app.route('/api/route-geojson', methods=['POST'])
def get_route_geojson():
    """
    Retourne les données GeoJSON pour afficher le trajet sur une carte
    Body: {
        "path": ["Analakely", "Ivandry"]
    }
    """
    data = request.get_json()
    path_names = data.get('path', [])
    
    if len(path_names) < 2:
        return jsonify({
            'success': False,
            'error': 'Au moins 2 localités requises'
        }), 400
    
    # Construire GeoJSON
    coordinates = []
    features = []
    
    for i, name in enumerate(path_names):
        node = graph.get_node(name)
        if node is None:
            return jsonify({
                'success': False,
                'error': f'Localité {name} non trouvée'
            }), 404
        
        # Ajouter au trajet
        coordinates.append([node.longitude, node.latitude])
        
        # Créer un feature pour chaque point
        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [node.longitude, node.latitude]
            },
            'properties': {
                'name': name,
                'step': i + 1,
                'type': 'start' if i == 0 else 'end' if i == len(path_names) - 1 else 'waypoint'
            }
        }
        features.append(feature)
    
    # Créer la ligne du trajet
    line_feature = {
        'type': 'Feature',
        'geometry': {
            'type': 'LineString',
            'coordinates': coordinates
        },
        'properties': {
            'name': f'{path_names[0]} → {path_names[-1]}',
            'type': 'route'
        }
    }
    features.insert(0, line_feature)
    
    geojson = {
        'type': 'FeatureCollection',
        'features': features,
        'bounds': {
            'min_lat': min([c[1] for c in coordinates]),
            'max_lat': max([c[1] for c in coordinates]),
            'min_lon': min([c[0] for c in coordinates]),
            'max_lon': max([c[0] for c in coordinates]),
        }
    }
    
    return jsonify({
        'success': True,
        'geojson': geojson,
        'bounds': geojson['bounds']
    })


@app.route('/api/route-details', methods=['POST'])
def get_route_details():
    """
    Retourne tous les détails du trajet avec coordonnées GPS
    """
    data = request.get_json()
    start = data.get('start')
    end = data.get('end')
    optimization = data.get('optimization', 'distance')
    
    if not start or not end:
        return jsonify({'success': False, 'error': 'Départ et destination requis'}), 400
    
    # Trouver le trajet optimal
    weight_map = {'distance': 'distance', 'duration': 'duration', 'price': 'price', 'temps': 'duration', 'prix': 'price'}
    weight = weight_map.get(optimization, 'distance')
    
    result = astar(graph, start, end, weight=weight)
    
    if not result['path']:
        return jsonify({'success': False, 'error': f'Pas de chemin trouvé entre {start} et {end}'}), 404
    
    # Construire les détails avec coordonnées
    route_details = {
        'success': True,
        'start': {
            'name': start,
            'latitude': graph.get_node(start).latitude,
            'longitude': graph.get_node(start).longitude
        },
        'end': {
            'name': end,
            'latitude': graph.get_node(end).latitude,
            'longitude': graph.get_node(end).longitude
        },
        'path': [node.name for node in result['path']],
        'waypoints': [
            {
                'name': node.name,
                'latitude': node.latitude,
                'longitude': node.longitude,
                'step': i + 1
            }
            for i, node in enumerate(result['path'])
        ],
        'distance': result['distance'],
        'duration': result['duration'],
        'price': result['price'],
        'algorithm': result['algorithm'],
        'optimization': weight,
        'segments': _build_segments(result['path'])
    }
    
    return jsonify(route_details)


@app.route('/api/transport-journey', methods=['POST'])
def get_transport_journey():
    """
    Retourne un voyage complet avec tous les détails
    Body: {
        "start": "Analakely",
        "end": "Ivandry",
        "optimization": "distance",
        "transport": "taxi"
    }
    """
    data = request.get_json()
    start = data.get('start')
    end = data.get('end')
    optimization = data.get('optimization', 'distance')
    transport = data.get('transport')
    
    if not start or not end:
        return jsonify({'success': False, 'error': 'Départ et destination requis'}), 400
    
    # Obtenir le trajet
    weight_map = {'distance': 'distance', 'duration': 'duration', 'price': 'price'}
    weight = weight_map.get(optimization, 'distance')
    
    result = astar(graph, start, end, weight=weight)
    
    if not result['path']:
        return jsonify({'success': False, 'error': 'Pas de chemin trouvé'}), 404
    
    # Si transport spécifié, calculer le temps
    estimated_time = result['duration']
    if transport:
        estimated_time = db.calculate_route_time_optimized(result['distance'], transport)
    
    journey = {
        'success': True,
        'journey': {
            'start': start,
            'end': end,
            'distance': result['distance'],
            'price': result['price'],
            'estimated_time': estimated_time,
            'transport': transport or 'non spécifié',
            'path': [node.name for node in result['path']],
            'coordinates': [
                {
                    'location': node.name,
                    'latitude': node.latitude,
                    'longitude': node.longitude
                }
                for node in result['path']
            ]
        }
    }
    
    return jsonify(journey)


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


@app.route('/api/health', methods=['GET'])
def health():
    """Vérification de la santé de l'API"""
    return jsonify({
        'success': True,
        'status': 'API running',
        'localities_count': len(db.get_all_localities()),
        'transport_types_count': len(db.get_all_transport_types())
    })


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint non trouvé'
    }), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        'success': False,
        'error': 'Erreur serveur'
    }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
