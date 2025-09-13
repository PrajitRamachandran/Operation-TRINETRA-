// =================================================================================
// app.js - Vanilla JS Frontend for Convoy Command System
// =================================================================================

document.addEventListener('DOMContentLoaded', () => {

    // -----------------------------------------------------------------------------
    // SECTION 1: GLOBAL STATE & CONFIGURATION
    // -----------------------------------------------------------------------------
    const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';
    let state = {
        token: null,
        user: null, // { username, role }
        activeView: 'login-view',
        map: null,
        routeMap: null,
        threatHeatLayer: null,
        convoyLayer: null,
        routeLayer: null,
        updateInterval: null,
    };

    // -----------------------------------------------------------------------------
    // SECTION 2: DOM ELEMENT SELECTORS
    // -----------------------------------------------------------------------------
    const loginContainer = document.getElementById('login-container');
    const appContainer = document.getElementById('app-container');
    const loginForm = document.getElementById('login-form');
    const logoutButton = document.getElementById('logout-button');
    const navLinks = document.getElementById('nav-links');
    const usernameDisplay = document.getElementById('username-display');
    const roleDisplay = document.getElementById('role-display');
    const contentViews = document.getElementById('content-views');
    
    // View-specific content containers
    const statsGrid = document.getElementById('stats-grid');
    const alertsList = document.getElementById('alerts-list');
    const convoysList = document.getElementById('convoys-list');
    const threatsList = document.getElementById('threats-list');
    const missionsList = document.getElementById('missions-list');
    const routeForm = document.getElementById('route-form');

    // -----------------------------------------------------------------------------
    // SECTION 3: CORE UTILITIES (API Calls, View Management)
    // -----------------------------------------------------------------------------

    /**
     * A wrapper for the Fetch API to automatically add auth headers and handle responses.
     * @param {string} endpoint - The API endpoint to call (e.g., '/users').
     * @param {object} options - Options for the fetch call (method, body, etc.).
     * @returns {Promise<any>} - The JSON response from the API.
     */
    async function apiFetch(endpoint, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };

        if (state.token) {
            headers['Authorization'] = `Bearer ${state.token}`;
        }

        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers,
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errorData.detail || 'An API error occurred');
        }
        
        // Handle responses with no content
        if (response.status === 204 || response.headers.get("content-length") === "0") {
            return null;
        }
        
        return response.json();
    }

    /**
     * Decodes a JWT token to extract user information.
     * @param {string} token - The JWT token.
     * @returns {object|null} - The decoded payload or null if invalid.
     */
    function decodeJwt(token) {
        try {
            return JSON.parse(atob(token.split('.')[1]));
        } catch (e) {
            return null;
        }
    }

    /**
     * Hides all views and shows the one with the specified ID.
     * @param {string} viewId - The ID of the view to show.
     */
    function showView(viewId) {
        contentViews.querySelectorAll('.view').forEach(view => view.classList.add('hidden'));
        const activeView = document.getElementById(viewId);
        if (activeView) {
            activeView.classList.remove('hidden');
            state.activeView = viewId;
            // Highlight the active nav link
            navLinks.querySelectorAll('a').forEach(a => {
                a.classList.remove('active');
                if (a.dataset.view === viewId) {
                    a.classList.add('active');
                }
            });
            // Fetch data for the new view
            loadDataForView(viewId);
        }
    }
    
    // -----------------------------------------------------------------------------
    // SECTION 4: AUTHENTICATION LOGIC
    // -----------------------------------------------------------------------------

    async function handleLogin(event) {
        event.preventDefault();
        const username = event.target.username.value;
        const password = event.target.password.value;
        const loginError = document.getElementById('login-error');
        loginError.textContent = '';

        try {
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);

            const data = await fetch(`${API_BASE_URL}/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData,
            }).then(res => res.json());

            if (data.detail) throw new Error(data.detail);

            state.token = data.access_token;
            localStorage.setItem('accessToken', state.token);
            
            const payload = decodeJwt(state.token);
            state.user = { username: payload.sub, role: payload.role };
            
            initializeApp();

        } catch (error) {
            loginError.textContent = error.message;
        }
    }

    function handleLogout() {
        state.token = null;
        state.user = null;
        localStorage.removeItem('accessToken');
        clearInterval(state.updateInterval);
        
        loginContainer.classList.remove('hidden');
        appContainer.classList.add('hidden');
    }

    // -----------------------------------------------------------------------------
    // SECTION 5: MAP INITIALIZATION & RENDERING
    // -----------------------------------------------------------------------------

    function initMap(mapId) {
        const map = L.map(mapId).setView([13.0827, 80.2707], 10); // Default to Chennai
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(map);
        return map;
    }
    
    function updateMapLayers(map, convoys = [], threats = [], route = null) {
        // Clear existing layers
        if (state.convoyLayer) state.convoyLayer.clearLayers();
        if (state.threatHeatLayer) map.removeLayer(state.threatHeatLayer);
        if (state.routeLayer) state.routeLayer.clearLayers();

        // Render convoys
        if (!state.convoyLayer) state.convoyLayer = L.layerGroup().addTo(map);
        convoys.forEach(convoy => {
            L.marker([convoy.current_location.lat, convoy.current_location.lon])
                .addTo(state.convoyLayer)
                .bindPopup(`<b>${convoy.call_sign}</b><br>Status: ${convoy.status}`);
        });

        // Render threat heatmap
        const threatPoints = threats
            .filter(t => t.verified_status === 'confirmed')
            .map(t => [t.location.lat, t.location.lon, 0.8]); // lat, lon, intensity
        if (threatPoints.length > 0) {
            state.threatHeatLayer = L.heatLayer(threatPoints, { radius: 25 }).addTo(map);
        }

        // Render route polyline
        if (route) {
            if (!state.routeLayer) state.routeLayer = L.layerGroup().addTo(map);
            L.polyline(route, { color: 'blue' }).addTo(state.routeLayer);
        }
    }

    // -----------------------------------------------------------------------------
    // SECTION 6: DATA FETCHING & UI RENDERING
    // -----------------------------------------------------------------------------

    function loadDataForView(viewId) {
        switch(viewId) {
            case 'dashboard-view':
                fetchDashboardData();
                break;
            case 'convoys-view':
                fetchConvoys();
                break;
            case 'threats-view':
                fetchThreats();
                break;
            case 'alerts-view':
                fetchAlerts();
                break;
            case 'missions-view':
                fetchMissions();
                break;
            // Other views can have their data loaders here
        }
    }
    
    // DASHBOARD
    async function fetchDashboardData() {
        try {
            const [status, convoys, alerts] = await Promise.all([
                apiFetch('/system_status'),
                apiFetch('/convoys'),
                apiFetch('/alerts')
            ]);
            
            // Render Stats
            statsGrid.innerHTML = `
                <div class="card"><h3>Active Convoys</h3><p>${convoys.length}</p></div>
                <div class="card"><h3>Active Alerts</h3><p>${alerts.length}</p></div>
                <div class="card"><h3>System Status</h3><p>${status.status}</p></div>
                <div class="card"><h3>Area Temp</h3><p>${status.weather.temperature_celsius}°C</p></div>
            `;
            
            // Update Map
            if (!state.map) state.map = initMap('dashboard-map');
            updateMapLayers(state.map, convoys);

        } catch (error) {
            console.error('Failed to fetch dashboard data:', error);
        }
    }
    
    // CONVOYS
    async function fetchConvoys() {
        const convoys = await apiFetch('/convoys');
        convoysList.innerHTML = convoys.map(c => `
            <div class="card">
                <h3>${c.call_sign}</h3>
                <p>Status: ${c.status}</p>
                <p>Speed: ${c.speed_kmph} km/h</p>
                <p>ETA: ${new Date(c.eta).toLocaleTimeString()}</p>
                <button class="danger" data-convoy-id="${c.id}" data-action="stop">Stop</button>
            </div>
        `).join('');
    }

    // ALERTS
    async function fetchAlerts() {
        const alerts = await apiFetch('/alerts');
        alertsList.innerHTML = alerts.map(a => `
            <div class="card">
                <h3>${a.severity} Alert</h3>
                <p>${a.message}</p>
                <button data-alert-id="${a.id}" data-action="acknowledge">Acknowledge</button>
            </div>
        `).join('');
    }
    
    // THREATS
    async function fetchThreats() {
        const threats = await apiFetch('/threats');
        threatsList.innerHTML = threats.map(t => `
            <div class="card">
                <h3>${t.classification.toUpperCase()}</h3>
                <p>Status: ${t.verified_status}</p>
                <p>Source: ${t.source_type}</p>
            </div>
        `).join('');
    }

    // MISSIONS
    async function fetchMissions() {
        const missions = await apiFetch('/missions');
        missionsList.innerHTML = missions.map(m => `
            <div class="card">
                <h3>${m.call_sign}</h3>
                <p>Status: ${m.final_status}</p>
                <p>Ended: ${new Date(m.end_time).toLocaleDateString()}</p>
            </div>
        `).join('');
    }

    // ROUTES
    async function handleRouteRequest(event) {
        event.preventDefault();
        const start = document.getElementById('start-coords').value.split(',').map(Number);
        const end = document.getElementById('end-coords').value.split(',').map(Number);
        const mode = document.getElementById('route-mode').value;

        const routeData = await apiFetch('/get_route', {
            method: 'POST',
            body: JSON.stringify({
                start_lat: start[0], start_lon: start[1],
                end_lat: end[0], end_lon: end[1],
                mode: mode
            })
        });

        document.getElementById('route-results').innerHTML = `
            <div class="card">
                <h3>Route Calculated</h3>
                <p>Distance: ${routeData.total_distance_km.toFixed(2)} km</p>
                <p>Est. Fuel: ${routeData.estimated_fuel_liters.toFixed(1)} L</p>
            </div>
        `;
        
        if (!state.routeMap) state.routeMap = initMap('route-map');
        const routeCoords = routeData.path_geometry.coordinates.map(c => [c[1], c[0]]); // Leaflet uses [lat, lon]
        updateMapLayers(state.routeMap, [], [], routeCoords);
    }
    
    // -----------------------------------------------------------------------------
    // SECTION 7: EVENT LISTENERS & INITIALIZATION
    // -----------------------------------------------------------------------------

    function initializeApp() {
        // Show main app, hide login
        loginContainer.classList.add('hidden');
        appContainer.classList.remove('hidden');

        // Set user info in header
        usernameDisplay.textContent = state.user.username;
        roleDisplay.textContent = state.user.role;

        // Start periodic data fetching for dashboard
        fetchDashboardData(); // Initial fetch
        state.updateInterval = setInterval(fetchDashboardData, 10000); // Update every 10 seconds
        
        // Show the default view
        showView('dashboard-view');
    }

    function setupEventListeners() {
        loginForm.addEventListener('submit', handleLogin);
        logoutButton.addEventListener('click', handleLogout);
        routeForm.addEventListener('submit', handleRouteRequest);

        // Navigation
        navLinks.addEventListener('click', (event) => {
            if (event.target.tagName === 'A') {
                event.preventDefault();
                const viewId = event.target.dataset.view;
                if (viewId) {
                    showView(viewId);
                }
            }
        });
        
        // Dynamic event listeners for buttons on cards
        document.body.addEventListener('click', async (event) => {
            const target = event.target;
            const action = target.dataset.action;
            if (!action) return;

            if (action === 'stop') {
                const convoyId = target.dataset.convoyId;
                if (confirm(`Halt convoy ${convoyId}?`)) {
                    await apiFetch(`/convoy/${convoyId}/stop`, { method: 'POST' });
                    fetchConvoys(); // Refresh the list
                }
            }
            if (action === 'acknowledge') {
                const alertId = target.dataset.alertId;
                await apiFetch(`/alerts/acknowledge/${alertId}`, { method: 'POST' });
                fetchAlerts(); // Refresh the list
            }
        });
    }

    // --- App Entry Point ---
    const token = localStorage.getItem('accessToken');
    if (token) {
        state.token = token;
        const payload = decodeJwt(token);
        if (payload && payload.exp * 1000 > Date.now()) {
            state.user = { username: payload.sub, role: payload.role };
            initializeApp();
        }
    }
    
    setupEventListeners();
});