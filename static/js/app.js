/* ============================
   APPLICATION TRANSMAD - JAVASCRIPT
   ============================ */

// Configuration
const API_BASE = 'http://localhost:5000/api';
let selectedOptimization = 'distance';
let lastSearchResult = null;
let routeMap = null;
let mapMarkers = [];
let mapPolyline = null;

// Presets de trajets
const PRESETS = {
    'analakely-ivato': { start: 'Analakely', end: 'Ivato' },
    'analakely-ambatobe': { start: 'Analakely', end: 'Ambatobe' },
    'isoraka-ivandry': { start: 'Isoraka', end: 'Ivandry' },
    'anosy-talatamaty': { start: 'Anosy', end: 'Talatamaty' }
};


// ============================
// INITIALISATION
// ============================

document.addEventListener('DOMContentLoaded', () => {
    console.log('Initialisation de TransMad...');
    loadLocalities();
    attachEventListeners();
    checkAPIHealth();
});

function attachEventListeners() {
    // Boutons
    document.getElementById('searchBtn').addEventListener('click', performSearch);
    document.getElementById('newSearchBtn').addEventListener('click', resetSearch);
    document.getElementById('swapBtn').addEventListener('click', swapLocalities);

    // Presets
    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', selectPreset);
    });

    // Options d'optimisation
    document.querySelectorAll('.option-btn').forEach(btn => {
        btn.addEventListener('click', selectOptimization);
    });

    // Champs de saisie
    document.getElementById('departure').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') performSearch();
    });

    document.getElementById('destination').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') performSearch();
    });
}

// ============================
// PRESETS
// ============================

function selectPreset(e) {
    const presetKey = e.target.closest('.preset-btn').dataset.preset;
    const preset = PRESETS[presetKey];
    
    if (preset) {
        document.getElementById('departure').value = preset.start;
        document.getElementById('destination').value = preset.end;
        
        // Marquer le preset comme actif
        document.querySelectorAll('.preset-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        e.target.closest('.preset-btn').classList.add('active');
        
        // Relancer la recherche
        setTimeout(() => performSearch(), 100);
    }
}

// ============================
// CARTOGRAPHIE
// ============================

function initializeMap() {
    // Initialise la carte Leaflet
    if (document.getElementById('routeMap') && !routeMap) {
        // Centrer sur Antananarivo
        routeMap = L.map('routeMap').setView([-18.8829, 47.5241], 13);
        
        // Ajouter OpenStreetMap tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19,
            minZoom: 10
        }).addTo(routeMap);
    }
}

function displayMapRoute(geojsonData, bounds) {
    // Affiche le trajet sur la carte avec OSRM si disponible
    if (!routeMap) {
        initializeMap();
    }
    
    // Nettoyer les marqueurs précédents
    mapMarkers.forEach(marker => routeMap.removeLayer(marker));
    if (mapPolyline) {
        routeMap.removeLayer(mapPolyline);
    }
    mapMarkers = [];
    
    // Extraire les points de passage
    const features = geojsonData.features;
    const waypoints = [];
    const waypointDetails = [];
    
    features.forEach(feature => {
        if (feature.geometry.type === 'Point') {
            const coords = feature.geometry.coordinates;
            const props = feature.properties;
            
            // Stocker les coordonnées pour OSRM [lon, lat]
            waypoints.push([coords[0], coords[1]]);
            waypointDetails.push(props);
            
            // Créer les marqueurs
            let markerEmoji = '📍';
            let markerColor = '#95E1D3';
            
            if (props.type === 'start') {
                markerEmoji = '🟢';
                markerColor = '#4ECDC4';
            } else if (props.type === 'end') {
                markerEmoji = '🔴';
                markerColor = '#FF6B6B';
            } else if (props.type === 'waypoint') {
                markerEmoji = '📌';
                markerColor = '#FFE66D';
            }
            
            const marker = L.marker([coords[1], coords[0]], {
                icon: L.divIcon({
                    className: 'route-marker',
                    html: `<span style="font-size: 24px; filter: drop-shadow(0 0 8px ${markerColor})">${markerEmoji}</span>`,
                    iconSize: [30, 30],
                    iconAnchor: [15, 30]
                })
            }).bindPopup(`
                <strong>${props.name}</strong><br>
                Étape ${props.step}
            `).addTo(routeMap);
            
            mapMarkers.push(marker);
        }
    });
    
    // Tenter d'obtenir la route réelle via OSRM
    if (typeof getBestRoute !== 'undefined' && waypoints.length >= 2) {
        console.log('🗺️ Récupération de la route réelle...');
        
        getBestRoute(waypoints).then(routeResult => {
            if (routeResult && routeResult.source === 'osrm') {
                // Utiliser la géométrie OSRM
                const geometry = routeResult.data.geometry;
                const coordinates = geometry.coordinates.map(coord => [coord[1], coord[0]]);
                
                mapPolyline = L.polyline(coordinates, {
                    color: ROUTING_CONFIG.routeColor,
                    weight: ROUTING_CONFIG.routeWeight,
                    opacity: ROUTING_CONFIG.routeOpacity,
                    smoothFactor: 1.0
                }).addTo(routeMap);
                
                console.log('✅ Route OSRM affichée sur la carte');
                
                // Ajouter un badge OSRM sur la carte
                addRoutingSourceBadge('OSRM');
                
            } else {
                // Fallback: ligne droite entre les points
                displayFallbackRoute(waypoints);
            }
            
            // Ajuster la vue
            adjustMapBounds(bounds);
        }).catch(error => {
            console.warn('Erreur routing:', error);
            displayFallbackRoute(waypoints);
            adjustMapBounds(bounds);
        });
    } else {
        // Pas de service de routing disponible
        displayFallbackRoute(waypoints);
        adjustMapBounds(bounds);
    }
}

function displayFallbackRoute(waypoints) {
    // Afficher une ligne droite simple entre les points
    const coordinates = waypoints.map(w => [w[1], w[0]]);
    
    if (coordinates.length > 1) {
        mapPolyline = L.polyline(coordinates, {
            color: '#4ECDC4',
            weight: 3,
            opacity: 0.8,
            dashArray: '5, 5'
        }).addTo(routeMap);
        
        addRoutingSourceBadge('Direct');
    }
}

function adjustMapBounds(bounds) {
    if (bounds && routeMap) {
        routeMap.fitBounds([
            [bounds.min_lat, bounds.min_lon],
            [bounds.max_lat, bounds.max_lon]
        ], { padding: [50, 50] });
    }
}

function addRoutingSourceBadge(source) {
    // Ajouter un badge pour indiquer la source du routing
    const existingBadge = document.querySelector('.routing-badge');
    if (existingBadge) {
        existingBadge.remove();
    }
    
    const badge = document.createElement('div');
    badge.className = 'routing-badge';
    badge.innerHTML = `
        <span style="font-size: 12px; padding: 4px 8px; background: rgba(78, 205, 196, 0.9); color: white; border-radius: 4px; position: absolute; top: 10px; right: 10px; z-index: 1000; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
            📍 Route: ${source}
        </span>
    `;
    
    const mapContainer = document.getElementById('routeMap');
    if (mapContainer) {
        mapContainer.appendChild(badge);
    }
}

// ============================
// LOCALITÉS
// ============================


async function loadLocalities() {
    try {
        showMessage('info', '⏳ Chargement des localités...');
        
        const response = await fetch(`${API_BASE}/localities`);
        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || 'Erreur lors du chargement');
        }

        const localities = data.localities;
        const departureSelect = document.getElementById('departure');
        const destinationSelect = document.getElementById('destination');

        // Vider les sélections
        departureSelect.innerHTML = '<option value="">Sélectionnez votre départ...</option>';
        destinationSelect.innerHTML = '<option value="">Sélectionnez votre destination...</option>';

        // Ajouter les localités
        localities.forEach(locality => {
            const option1 = document.createElement('option');
            option1.value = locality.name;
            option1.textContent = locality.name;
            departureSelect.appendChild(option1);

            const option2 = document.createElement('option');
            option2.value = locality.name;
            option2.textContent = locality.name;
            destinationSelect.appendChild(option2);
        });

        hideMessage('info');
        console.log(`${localities.length} localités chargées`);
    } catch (error) {
        showError(`Erreur lors du chargement des localités: ${error.message}`);
    }
}

function swapLocalities() {
    const departure = document.getElementById('departure');
    const destination = document.getElementById('destination');

    const temp = departure.value;
    departure.value = destination.value;
    destination.value = temp;
}

// ============================
// OPTIONS D'OPTIMISATION
// ============================

function selectOptimization(e) {
    // Désactiver tous les boutons
    document.querySelectorAll('.option-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Activer le bouton cliqué
    e.target.closest('.option-btn').classList.add('active');

    // Storer l'optimisation
    selectedOptimization = e.target.closest('.option-btn').dataset.optimization;
    console.log(`Optimisation sélectionnée: ${selectedOptimization}`);
}

// ============================
// RECHERCHE
// ============================

async function performSearch() {
    const departure = document.getElementById('departure').value;
    const destination = document.getElementById('destination').value;

    // Validation
    if (!departure) {
        showError('Veuillez sélectionner un lieu de départ');
        return;
    }

    if (!destination) {
        showError('Veuillez sélectionner un lieu d\'arrivée');
        return;
    }

    if (departure === destination) {
        showError('Le départ et la destination doivent être différents');
        return;
    }

    // Afficher le chargement
    showLoading();

    try {
        // Étape 1: Trouver le meilleur trajet
        const routeResponse = await fetch(`${API_BASE}/find-route`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                start: departure,
                end: destination,
                optimization: selectedOptimization
            })
        });

        const routeData = await routeResponse.json();

        if (!routeData.success) {
            throw new Error(routeData.error || 'Erreur lors de la recherche');
        }

        // Storer le résultat
        lastSearchResult = routeData;

        // Étape 2: Obtenir les données GeoJSON pour la carte
        const geojsonResponse = await fetch(`${API_BASE}/route-geojson`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({'path': routeData.path })
        });

        const geojsonData = await geojsonResponse.json();

        // Étape 3: Obtenir la comparaison des transports
        const comparisonResponse = await fetch(`${API_BASE}/compare-transports`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                distance: routeData.distance
            })
        });

        const comparisonData = await comparisonResponse.json();

        // Étape 4: Obtenir l'optimisation du temps
        const timeResponse = await fetch(`${API_BASE}/optimize-time`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                distance: routeData.distance,
                available_transports: routeData.segments.length > 0 
                    ? routeData.segments[0].transports 
                    : []
            })
        });

        const timeData = await timeResponse.json();

        // Afficher les résultats
        hideLoading();
        displayResults(routeData, comparisonData, timeData, geojsonData);

    } catch (error) {
        hideLoading();
        showError(`Erreur: ${error.message}`);
    }
}

// ============================
// AFFICHAGE DES RÉSULTATS
// ============================

function displayResults(routeData, comparisonData, timeData, geojsonData) {
    // Afficher la section résultats
    document.getElementById('resultsSection').style.display = 'block';

    // Initialiser la carte
    initializeMap();

    // Afficher la carte
    if (geojsonData && geojsonData.success) {
        displayMapRoute(geojsonData.geojson, geojsonData.bounds);
    }

    // Résumé
    displayRouteSummary(routeData);

    // Chemin
    displayRoutePath(routeData);

    // Transport le moins cher
    displayCheapestTransport(routeData);

    // Comparaison des transports
    if (comparisonData.success) {
        displayTransportComparison(comparisonData);
    }

    // Optimisation du temps
    if (timeData.success) {
        displayTimeOptimization(timeData);
    }

    // Scroller vers les résultats
    setTimeout(() => {
        document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
    }, 100);
}

function displayRouteSummary(data) {
    document.getElementById('totalDistance').textContent = `${data.distance.toFixed(1)} km`;
    document.getElementById('totalDuration').textContent = `${data.duration} min`;
    document.getElementById('totalPrice').textContent = `${formatPrice(data.price)} Ar`;
}

function displayRoutePath(data) {
    const container = document.getElementById('pathContainer');
    container.innerHTML = '';

    data.path.forEach((location, index) => {
        const item = document.createElement('div');
        item.className = 'path-item';

        let segmentInfo = '';
        if (index < data.segments.length) {
            const segment = data.segments[index];
            const transportBadges = segment.transports
                .map(t => `<span class="transport-badge">${t.toUpperCase()}</span>`)
                .join('');
            
            segmentInfo = `
                <div class="path-item-details">
                    <div class="detail-badge">📍 ${segment.distance.toFixed(1)} km</div>
                    <div class="detail-badge">⏱️ ${segment.duration} min</div>
                    <div class="detail-badge">💰 ${formatPrice(segment.price)} Ar</div>
                </div>
                <div class="transport-badges">${transportBadges}</div>
            `;
        }

        item.innerHTML = `
            <div class="path-item-number">${index + 1}</div>
            <div class="path-item-info">
                <div class="path-item-location">${location}</div>
                ${segmentInfo}
            </div>
        `;

        container.appendChild(item);
    });
}

function displayCheapestTransport(data) {
    const container = document.getElementById('cheapestTransportInfo');
    const transport = data.cheapest_transport || 'Non disponible';
    const price = data.estimated_price || 0;

    const transportInfo = {
        'taxi': '🚖',
        'taxi-brousse': '🚌',
        'moto-taxi': '🏍️',
        'pousse-pousse': '🛺'
    };

    const emoji = transportInfo[transport] || '🚗';
    const displayName = transport.replace('-', ' ').toUpperCase();

    container.innerHTML = `
        <div class="cheapest-transport-info">
            <div class="cheapest-emoji">${emoji}</div>
            <div class="cheapest-details">
                <div class="cheapest-name">${displayName}</div>
                <div class="cheapest-price">Estimation: ${formatPrice(price)} Ar</div>
            </div>
        </div>
    `;
}

function displayTransportComparison(data) {
    const container = document.getElementById('transportComparison');
    container.innerHTML = '';

    const comparisonDiv = document.createElement('div');
    comparisonDiv.className = 'transport-comparison';

    data.transports.forEach((transport, index) => {
        const item = document.createElement('div');
        item.className = 'transport-item';
        item.style.borderLeftColor = transport.color;

        item.innerHTML = `
            <div class="transport-left">
                <div class="transport-emoji">${transport.emoji}</div>
                <div class="transport-info">
                    <div class="transport-name">${transport.name}</div>
                    <div class="transport-details">
                        <span>Par km: ${transport.price_per_km} Ar</span>
                    </div>
                </div>
            </div>
            <div class="transport-right">
                <div class="transport-price">${formatPrice(transport.estimated_price)} Ar</div>
                <div class="transport-time">⏱️ ${transport.estimated_time} min</div>
            </div>
        `;

        if (index === 0) {
            item.style.boxShadow = `0 4px 12px ${transport.color}40`;
        }

        comparisonDiv.appendChild(item);
    });

    container.appendChild(comparisonDiv);
}

function displayTimeOptimization(data) {
    const container = document.getElementById('timeOptimization');

    const transportInfo = {
        'taxi': '🚖',
        'taxi-brousse': '🚌',
        'moto-taxi': '🏍️',
        'pousse-pousse': '🛺'
    };

    const emoji = transportInfo[data.best_transport] || '🚗';
    const displayName = data.best_transport.replace('-', ' ').toUpperCase();

    container.innerHTML = `
        <div class="optimal-time-result">
            <div class="optimal-time-left">
                <div class="optimal-emoji">${emoji}</div>
                <div class="optimal-text">
                    <div class="optimal-label">Meilleur temps avec</div>
                    <div class="optimal-time">${displayName}</div>
                </div>
            </div>
            <div style="font-weight: 700; font-size: 24px; color: #4ECDC4;">
                ${data.optimized_time} min
            </div>
        </div>
    `;
}

// ============================
// RÉINITIALISATION
// ============================

function resetSearch() {
    document.getElementById('departure').value = '';
    document.getElementById('destination').value = '';
    document.getElementById('resultsSection').style.display = 'none';
    lastSearchResult = null;
    hideError();
    hideMessage('info');
    document.querySelector('.option-btn[data-optimization="distance"]').classList.add('active');
    selectedOptimization = 'distance';
}

// ============================
// UTILITAIRES - MESSAGES
// ============================

function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = '❌ ' + message;
    errorDiv.style.display = 'block';
    console.error(message);
}

function hideError() {
    document.getElementById('errorMessage').style.display = 'none';
}

function showMessage(type, message) {
    const messageDiv = document.getElementById(`${type}Message`);
    messageDiv.textContent = message;
    messageDiv.style.display = 'block';
}

function hideMessage(type) {
    document.getElementById(`${type}Message`).style.display = 'none';
}

function showLoading() {
    document.getElementById('loadingSpinner').style.display = 'flex';
    document.getElementById('resultsSection').style.display = 'none';
}

function hideLoading() {
    document.getElementById('loadingSpinner').style.display = 'none';
}

// ============================
// UTILITAIRES - FORMATAGE
// ============================

function formatPrice(price) {
    return Math.round(price).toLocaleString('fr-MG');
}

// ============================
// SANTÉ DE L'API
// ============================

async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        
        if (data.success) {
            console.log('✅ API saine', data);
        }
    } catch (error) {
        console.warn('⚠️ Impossible de se connecter à l\'API:', error.message);
        showError('⚠️ Connexion à l\'API impossible. Assurez-vous que le serveur est lancé (python app.py)');
    }
}
