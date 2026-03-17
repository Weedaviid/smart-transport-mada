/* ============================
   CONFIGURATION ROUTING
   ============================ */

const ROUTING_CONFIG = {
    // Activer/désactiver OSRM
    useOSRM: true,
    
    // URL du serveur OSRM (API publique ou serveur local)
    osrmServer: 'https://router.project-osrm.org',
    
    // Configuration Google Maps (optionnel - nécessite une clé API)
    googleMaps: {
        enabled: false,  // Mettre à true pour activer Google Maps
        apiKey: 'VOTRE_CLE_API_GOOGLE_MAPS',  // À remplacer par votre clé
        directionsService: null  // Sera initialisé automatiquement
    },
    
    // Paramètres de routing
    routingProfile: 'driving',  // driving, walking, cycling
    
    // Options de visualisation
    routeColor: '#4ECDC4',
    routeWeight: 4,
    routeOpacity: 0.7,
    
    // Fallback en cas d'échec OSRM
    useFallback: true
};

/**
 * Récupère une route depuis OSRM
 * @param {Array} waypoints - Tableau de points [lon, lat]
 * @returns {Promise} - Route OSRM ou null en cas d'erreur
 */
async function getOSRMRoute(waypoints) {
    if (!ROUTING_CONFIG.useOSRM || waypoints.length < 2) {
        return null;
    }
    
    try {
        // Construire la requête OSRM
        // Format: /route/v1/{profile}/{coordinates}
        const coordinates = waypoints.map(w => `${w[0]},${w[1]}`).join(';');
        const url = `${ROUTING_CONFIG.osrmServer}/route/v1/${ROUTING_CONFIG.routingProfile}/${coordinates}?overview=full&geometries=geojson&steps=true`;
        
        console.log('🚗 Récupération de la route OSRM:', url);
        
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`OSRM API error: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.code !== 'Ok' || !data.routes || data.routes.length === 0) {
            throw new Error('Aucune route trouvée par OSRM');
        }
        
        const route = data.routes[0];
        console.log('✅ Route OSRM récupérée:', {
            distance: (route.distance / 1000).toFixed(2) + ' km',
            duration: Math.round(route.duration / 60) + ' min',
            steps: route.legs[0].steps.length
        });
        
        return {
            geometry: route.geometry,
            distance: route.distance,  // en mètres
            duration: route.duration,  // en secondes
            legs: route.legs
        };
        
    } catch (error) {
        console.warn('⚠️ Erreur OSRM:', error.message);
        if (ROUTING_CONFIG.useFallback) {
            console.log('↩️ Utilisation du tracé direct (fallback)');
        }
        return null;
    }
}

/**
 * Récupère une route depuis Google Maps Directions API
 * @param {Array} waypoints - Tableau de points {lat, lng}
 * @returns {Promise} - Route Google Maps ou null
 */
async function getGoogleMapsRoute(waypoints) {
    if (!ROUTING_CONFIG.googleMaps.enabled || waypoints.length < 2) {
        return null;
    }
    
    // Note: Pour utiliser Google Maps, il faut charger l'API dans index.html
    // <script src="https://maps.googleapis.com/maps/api/js?key=VOTRE_CLE&libraries=geometry"></script>
    
    if (typeof google === 'undefined' || !google.maps) {
        console.warn('⚠️ Google Maps API non chargée');
        return null;
    }
    
    try {
        // Initialiser le service si nécessaire
        if (!ROUTING_CONFIG.googleMaps.directionsService) {
            ROUTING_CONFIG.googleMaps.directionsService = new google.maps.DirectionsService();
        }
        
        const origin = waypoints[0];
        const destination = waypoints[waypoints.length - 1];
        const waypointsArray = waypoints.slice(1, -1).map(w => ({
            location: new google.maps.LatLng(w.lat, w.lng),
            stopover: true
        }));
        
        return new Promise((resolve, reject) => {
            ROUTING_CONFIG.googleMaps.directionsService.route({
                origin: new google.maps.LatLng(origin.lat, origin.lng),
                destination: new google.maps.LatLng(destination.lat, destination.lng),
                waypoints: waypointsArray,
                travelMode: google.maps.TravelMode.DRIVING
            }, (result, status) => {
                if (status === 'OK') {
                    console.log('✅ Route Google Maps récupérée');
                    resolve(result);
                } else {
                    reject(new Error(`Google Maps error: ${status}`));
                }
            });
        });
        
    } catch (error) {
        console.warn('⚠️ Erreur Google Maps:', error.message);
        return null;
    }
}

/**
 * Récupère la meilleure route disponible
 * @param {Array} waypoints - Points de passage
 * @returns {Promise} - Route ou null
 */
async function getBestRoute(waypoints) {
    // Essayer OSRM d'abord (gratuit)
    if (ROUTING_CONFIG.useOSRM) {
        const osrmRoute = await getOSRMRoute(waypoints);
        if (osrmRoute) {
            return { source: 'osrm', data: osrmRoute };
        }
    }
    
    // Essayer Google Maps si activé
    if (ROUTING_CONFIG.googleMaps.enabled) {
        const gmapsRoute = await getGoogleMapsRoute(waypoints);
        if (gmapsRoute) {
            return { source: 'google', data: gmapsRoute };
        }
    }
    
    // Aucune route externe disponible
    return null;
}
