"""
Test des algorithmes de pathfinding
Script standalone pour tester Dijkstra et A*
"""

import sys
import time
from database import TransportDatabase
from dijkstra import dijkstra
from astar import astar


class AlgorithmTester:
    """Classe pour tester les algorithmes"""
    
    def __init__(self):
        self.db = TransportDatabase()
        self.graph = self.db.get_graph()
        self.test_results = []
    
    def test_dijkstra_vs_astar(self, start, end, weight='distance'):
        """Compare Dijkstra et A* pour un trajet"""
        print(f"\n{'='*70}")
        print(f"TEST: {start} → {end} (Optimisation: {weight})")
        print(f"{'='*70}")
        
        # Test Dijkstra
        start_time = time.time()
        dijkstra_result = dijkstra(self.graph, start, end, weight=weight)
        dijkstra_time = (time.time() - start_time) * 1000  # en ms
        
        # Test A*
        start_time = time.time()
        astar_result = astar(self.graph, start, end, weight=weight)
        astar_time = (time.time() - start_time) * 1000  # en ms
        
        # Afficher résultats Dijkstra
        print(f"\n🔵 DIJKSTRA:")
        if dijkstra_result['path']:
            path_str = " → ".join([node.name for node in dijkstra_result['path']])
            print(f"  Chemin: {path_str}")
            print(f"  Distance: {dijkstra_result['distance']:.1f} km")
            print(f"  Durée: {dijkstra_result['duration']} min")
            print(f"  Prix: {dijkstra_result['price']:,.0f} Ar")
            print(f"  Temps calcul: {dijkstra_time:.2f} ms")
        else:
            print(f"  ❌ Pas de chemin trouvé")
        
        # Afficher résultats A*
        print(f"\n🟢 A* (ALGORITHME PRINCIPAL):")
        if astar_result['path']:
            path_str = " → ".join([node.name for node in astar_result['path']])
            print(f"  Chemin: {path_str}")
            print(f"  Distance: {astar_result['distance']:.1f} km")
            print(f"  Durée: {astar_result['duration']} min")
            print(f"  Prix: {astar_result['price']:,.0f} Ar")
            print(f"  Temps calcul: {astar_time:.2f} ms")
        else:
            print(f"  ❌ Pas de chemin trouvé")
        
        # Comparaison
        print(f"\n📊 COMPARAISON:")
        if dijkstra_result['path'] and astar_result['path']:
            # Vérifier si les chemins sont identiques
            dijkstra_path = [n.name for n in dijkstra_result['path']]
            astar_path = [n.name for n in astar_result['path']]
            
            if dijkstra_path == astar_path:
                print(f"  ✅ Chemin identique pour les deux algorithmes")
            else:
                print(f"  ⚠️ Chemins différents!")
                print(f"     Dijkstra: {' → '.join(dijkstra_path)}")
                print(f"     A*:       {' → '.join(astar_path)}")
            
            # Gain de performance
            speedup = dijkstra_time / astar_time if astar_time > 0 else 0
            print(f"  ⚡ A* est {speedup:.1f}x plus rapide que Dijkstra")
            print(f"     Dijkstra: {dijkstra_time:.2f} ms")
            print(f"     A*:       {astar_time:.2f} ms")
            print(f"     Gain:     {dijkstra_time - astar_time:.2f} ms")
        
        return {
            'start': start,
            'end': end,
            'weight': weight,
            'dijkstra': dijkstra_result,
            'astar': astar_result,
            'dijkstra_time': dijkstra_time,
            'astar_time': astar_time
        }
    
    def test_all_weights(self, start, end):
        """Teste tous les critères d'optimisation pour un trajet"""
        weights = ['distance', 'duration', 'price']
        
        print(f"\n{'*'*70}")
        print(f"TEST TOUS CRITÈRES: {start} → {end}")
        print(f"{'*'*70}")
        
        for weight in weights:
            self.test_dijkstra_vs_astar(start, end, weight=weight)
    
    def test_graph_structure(self):
        """Teste la structure du graphe"""
        print(f"\n{'='*70}")
        print(f"TEST: STRUCTURE DU GRAPHE")
        print(f"{'='*70}")
        
        nodes = self.graph.get_all_nodes()
        print(f"\n📍 Nœuds totaux: {len(nodes)}")
        print(f"   Localités:")
        for node in sorted(nodes, key=lambda n: n.name):
            print(f"   - {node.name} ({len(node.edges)} connexions)")
        
        print(f"\n🛣️  Arêtes totales: {len(self.graph.edges)}")
        
        # Vérifier la connectivité
        print(f"\n🔗 CONNECTIVITÉ:")
        disconnected = []
        for node in nodes:
            if len(node.edges) == 0:
                disconnected.append(node.name)
        
        if disconnected:
            print(f"   ⚠️ Nœuds déconnectés: {', '.join(disconnected)}")
        else:
            print(f"   ✅ Tous les nœuds ont des connexions")
        
        # Statistiques d'arêtes
        print(f"\n📊 STATISTIQUES D'ARÊTES:")
        distances = [edge.distance for edge in self.graph.edges]
        durations = [edge.duration for edge in self.graph.edges]
        prices = [edge.price for edge in self.graph.edges]
        
        print(f"   Distance:")
        print(f"     - Min: {min(distances):.1f} km")
        print(f"     - Max: {max(distances):.1f} km")
        print(f"     - Moyenne: {sum(distances)/len(distances):.1f} km")
        
        print(f"   Durée:")
        print(f"     - Min: {min(durations)} min")
        print(f"     - Max: {max(durations)} min")
        print(f"     - Moyenne: {sum(durations)/len(durations):.1f} min")
        
        print(f"   Prix:")
        print(f"     - Min: {min(prices):,.0f} Ar")
        print(f"     - Max: {max(prices):,.0f} Ar")
        print(f"     - Moyenne: {sum(prices)/len(prices):,.0f} Ar")
    
    def test_performance(self, iterations=10):
        """Test de performance sur plusieurs itérations"""
        print(f"\n{'='*70}")
        print(f"TEST: PERFORMANCE ({iterations} itérations)")
        print(f"{'='*70}")
        
        test_cases = [
            ('Analakely', 'Ivandry', 'distance'),
            ('Analakely', 'Antsorohavola', 'duration'),
            ('Plateau Haute-Ville', 'Betongitra', 'price'),
        ]
        
        for start, end, weight in test_cases:
            dijkstra_times = []
            astar_times = []
            
            for i in range(iterations):
                start_time = time.time()
                dijkstra(self.graph, start, end, weight=weight)
                dijkstra_times.append((time.time() - start_time) * 1000)
                
                start_time = time.time()
                astar(self.graph, start, end, weight=weight)
                astar_times.append((time.time() - start_time) * 1000)
            
            avg_dijkstra = sum(dijkstra_times) / len(dijkstra_times)
            avg_astar = sum(astar_times) / len(astar_times)
            
            print(f"\n{start} → {end}:")
            print(f"  Dijkstra: {avg_dijkstra:.2f} ms (min: {min(dijkstra_times):.2f}, max: {max(dijkstra_times):.2f})")
            print(f"  A*:       {avg_astar:.2f} ms (min: {min(astar_times):.2f}, max: {max(astar_times):.2f})")
            print(f"  Speedup:  {avg_dijkstra/avg_astar:.1f}x")
    
    def run_all_tests(self):
        """Exécute tous les tests"""
        print("\n")
        print("╔" + "="*68 + "╗")
        print("║" + " "*15 + "TRANSMAD - TEST DES ALGORITHMES" + " "*21 + "║")
        print("╚" + "="*68 + "╝")
        
        # Test 1: Structure du graphe
        self.test_graph_structure()
        
        # Test 2: Cas spécifiques
        test_cases = [
            ('Analakely', 'Ivandry'),
            ('Analakely', 'Antsorohavola'),
            ('Plateau Haute-Ville', 'Betongitra'),
        ]
        
        for start, end in test_cases:
            self.test_all_weights(start, end)
        
        # Test 3: Performance
        self.test_performance(iterations=20)
        
        # Résumé
        print(f"\n{'='*70}")
        print(f"RÉSUMÉ")
        print(f"{'='*70}")
        print(f"✅ Tous les tests sont terminés!")
        print(f"💡 Conclusion: A* est l'algorithme recommandé (plus rapide)")
        print(f"📚 Pour plus d'infos: Voir docs/ALGORITHMS.md")


def main():
    """Fonction principale"""
    tester = AlgorithmTester()
    
    # Parser les arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'graph':
            tester.test_graph_structure()
        elif command == 'performance':
            tester.test_performance(iterations=20)
        elif command == 'compare':
            if len(sys.argv) >= 4:
                start = sys.argv[2]
                end = sys.argv[3]
                weight = sys.argv[4] if len(sys.argv) > 4 else 'distance'
                tester.test_dijkstra_vs_astar(start, end, weight=weight)
            else:
                print("Usage: python test.py compare <start> <end> [weight]")
        else:
            print("Commandes disponibles:")
            print("  python test.py              - Tous les tests")
            print("  python test.py graph        - Test structure graphe")
            print("  python test.py performance  - Test performance")
            print("  python test.py compare <start> <end> [weight]")
    else:
        tester.run_all_tests()


if __name__ == '__main__':
    main()
