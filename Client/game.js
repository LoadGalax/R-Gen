/**
 * R-Gen Web Game Client
 * Handles API communication, WebSocket, and game state management
 */

class RGenGame {
    constructor() {
        this.apiUrl = window.location.origin;
        this.socket = null;
        this.currentLocation = null;
        this.worldInfo = null;
        this.locations = [];
        this.npcs = [];
        this.events = [];
        this.selectedNPC = null;

        // Initialize
        this.init();
    }

    async init() {
        console.log('Initializing R-Gen Game Client...');

        // Connect to WebSocket
        this.connectWebSocket();

        // Load initial data
        await this.loadWorldInfo();
        await this.loadLocations();
        await this.loadNPCs();
        await this.loadEvents();

        // Set initial location
        if (this.locations.length > 0) {
            await this.setLocation(this.locations[0].id);
        }

        // Start simulation
        await this.startSimulation();

        console.log('Game client initialized!');
    }

    // ========================================================================
    // WebSocket Connection
    // ========================================================================

    connectWebSocket() {
        console.log('Connecting to WebSocket...');

        // Use Socket.IO client
        this.socket = io(this.apiUrl);

        this.socket.on('connect', () => {
            console.log('WebSocket connected!');
            this.showNotification('Connected to game server', 'success');
        });

        this.socket.on('disconnect', () => {
            console.log('WebSocket disconnected');
            this.showNotification('Disconnected from server', 'warning');
        });

        this.socket.on('connected', (data) => {
            console.log('Server says:', data.message);
        });

        this.socket.on('world_update', (data) => {
            console.log('World update received:', data);
            this.handleWorldUpdate(data);
        });

        this.socket.on('player_moved', (data) => {
            console.log('Player moved:', data);
            this.showNotification(`Traveled to ${data.location_name}`, 'info');
        });
    }

    handleWorldUpdate(data) {
        // Update time display
        if (data.time) {
            this.updateTimeDisplay(data.time);
        }

        // Add new events
        if (data.recent_events && data.recent_events.length > 0) {
            data.recent_events.forEach(event => {
                this.addEvent(event);
            });
        }
    }

    // ========================================================================
    // API Calls
    // ========================================================================

    async apiGet(endpoint) {
        try {
            const response = await fetch(`${this.apiUrl}/api${endpoint}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error(`API GET error (${endpoint}):`, error);
            this.showNotification(`Error loading data: ${error.message}`, 'error');
            return null;
        }
    }

    async apiPost(endpoint, data) {
        try {
            const response = await fetch(`${this.apiUrl}/api${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error(`API POST error (${endpoint}):`, error);
            this.showNotification(`Error: ${error.message}`, 'error');
            return null;
        }
    }

    async loadWorldInfo() {
        const data = await this.apiGet('/world/info');
        if (data) {
            this.worldInfo = data;
            console.log('World info loaded:', data);
        }
    }

    async loadLocations() {
        const data = await this.apiGet('/locations');
        if (data && data.locations) {
            this.locations = data.locations;
            console.log(`Loaded ${this.locations.length} locations`);
        }
    }

    async loadNPCs() {
        const data = await this.apiGet('/npcs');
        if (data && data.npcs) {
            this.npcs = data.npcs;
            console.log(`Loaded ${this.npcs.length} NPCs`);
        }
    }

    async loadEvents() {
        const data = await this.apiGet('/events?limit=20');
        if (data && data.events) {
            this.events = data.events;
            this.updateEventsDisplay();
        }
    }

    async startSimulation() {
        const data = await this.apiPost('/simulation/start', {});
        if (data && data.success) {
            console.log('Simulation started');
        }
    }

    async stopSimulation() {
        const data = await this.apiPost('/simulation/stop', {});
        if (data && data.success) {
            console.log('Simulation stopped');
        }
    }

    // ========================================================================
    // Location Management
    // ========================================================================

    async setLocation(locationId) {
        const data = await this.apiGet(`/location/${locationId}`);
        if (data) {
            this.currentLocation = data;
            this.updateLocationDisplay();
            console.log('Current location:', data.name);
        }
    }

    async travelToLocation(locationId) {
        const data = await this.apiPost('/player/travel', { location_id: locationId });
        if (data && data.success) {
            await this.setLocation(locationId);
            this.showNotification(data.message, 'success');
        }
    }

    updateLocationDisplay() {
        if (!this.currentLocation) return;

        // Update page title
        const pageTitle = document.querySelector('[data-page="world"] .page-title');
        if (pageTitle) {
            pageTitle.textContent = `⚔ ${this.currentLocation.name} ⚔`;
        }

        // Update subtitle
        const subtitle = document.querySelector('[data-page="world"] .page-subtitle');
        if (subtitle) {
            const time = this.worldInfo?.current_time;
            subtitle.textContent = time ?
                `~ ${this.currentLocation.name}, Day ${time.day} of ${time.season} ~` :
                `~ ${this.currentLocation.name} ~`;
        }

        // Update weather/info
        this.updateLocationInfo();

        // Update description
        const descEl = document.querySelector('[data-page="world"] .description');
        if (descEl) {
            descEl.textContent = this.currentLocation.description || 'A mysterious place...';
        }

        // Update NPCs
        this.updateNPCsList();

        // Update travel options
        this.updateTravelOptions();
    }

    updateLocationInfo() {
        const infoBox = document.querySelector('[data-page="world"] .info-box');
        if (!infoBox) return;

        const time = this.worldInfo?.current_time;
        const weather = this.currentLocation.weather || 'Clear';

        infoBox.innerHTML = `
            <div class="info-row">
                <span class="label">🕐 Time:</span>
                <span id="time-display">${time?.time || '12:00'} (${time?.is_day ? 'Day' : 'Night'})</span>
            </div>
            <div class="info-row">
                <span class="label">☀️ Weather:</span>
                <span>${weather}</span>
            </div>
            <div class="info-row">
                <span class="label">🏠 Type:</span>
                <span>${this.currentLocation.template || 'Unknown'}</span>
            </div>
        `;
    }

    updateTimeDisplay(timeData) {
        const timeEl = document.getElementById('time-display');
        if (timeEl && timeData) {
            timeEl.textContent = `${timeData.time_string} (${timeData.is_day ? 'Day' : 'Night'})`;
        }

        // Update subtitle with current day/season
        const subtitle = document.querySelector('[data-page="world"] .page-subtitle');
        if (subtitle && timeData) {
            subtitle.textContent = `~ ${this.currentLocation?.name || 'Unknown'}, Day ${timeData.day} of ${timeData.season} ~`;
        }
    }

    updateNPCsList() {
        const npcList = document.querySelector('[data-page="world"] .npc-list');
        if (!npcList || !this.currentLocation) return;

        const npcsHere = this.currentLocation.npcs || [];

        if (npcsHere.length === 0) {
            npcList.innerHTML = '<div class="npc-card"><div class="npc-name">No one is here...</div></div>';
            return;
        }

        npcList.innerHTML = npcsHere.map(npcData => `
            <div class="npc-card" data-npc-id="${npcData.id}" onclick="game.showNPCDialogue('${npcData.id}')">
                <div class="npc-name">${this.getNPCIcon(npcData.profession)} ${npcData.name}</div>
                <div class="npc-detail">Level ${npcData.level || 1} ${npcData.profession} • ${npcData.current_activity || 'Idle'}</div>
            </div>
        `).join('');
    }

    getNPCIcon(profession) {
        const icons = {
            'blacksmith': '⚔️',
            'merchant': '💰',
            'innkeeper': '🍺',
            'wizard': '🧙‍♂️',
            'guard': '🛡️',
            'farmer': '🌾',
            'bard': '🎵',
            'priest': '✨',
            'hunter': '🏹'
        };
        return icons[profession?.toLowerCase()] || '👤';
    }

    updateTravelOptions() {
        const actionGrid = document.querySelector('[data-page="world"] .action-grid');
        if (!actionGrid) return;

        actionGrid.innerHTML = `
            <button class="btn" onclick="game.showTravelDialog()">🗺️ Journey</button>
            <button class="btn" onclick="game.showRestDialog()">🛏️ Rest</button>
            <button class="btn" onclick="game.showMarketDialog()">🏪 Market</button>
            <button class="btn" onclick="game.refreshLocation()">🔄 Refresh</button>
        `;
    }

    // ========================================================================
    // NPC Dialogue System
    // ========================================================================

    async showNPCDialogue(npcId) {
        const data = await this.apiGet(`/npc/${npcId}/dialogue`);
        if (!data) return;

        this.selectedNPC = data;

        // Create dialogue modal
        const modal = this.createModal('NPC Conversation', `
            <div class="dialogue-container">
                <div class="npc-portrait">
                    <div style="font-size: 48px; text-align: center; margin-bottom: 10px;">
                        ${this.getNPCIcon(data.profession)}
                    </div>
                    <h3 style="text-align: center; color: #d4af37;">${data.npc_name}</h3>
                    <p style="text-align: center; color: #b8a485; font-style: italic;">
                        ${data.profession} • Mood: ${data.mood}
                    </p>
                </div>

                <div class="dialogue-box">
                    <p class="dialogue-text">"${data.dialogues.greeting}"</p>
                </div>

                <div class="dialogue-options">
                    <button class="btn" onclick="game.showDialogueOption('mood')">
                        💭 How are you feeling?
                    </button>
                    <button class="btn" onclick="game.showDialogueOption('profession')">
                        💼 Tell me about your work
                    </button>
                    <button class="btn" onclick="game.closeModal()">
                        👋 Farewell
                    </button>
                </div>
            </div>
        `);

        document.body.appendChild(modal);
    }

    showDialogueOption(option) {
        if (!this.selectedNPC) return;

        const dialogueText = document.querySelector('.dialogue-text');
        if (dialogueText) {
            dialogueText.textContent = `"${this.selectedNPC.dialogues[option]}"`;
        }
    }

    // ========================================================================
    // Travel Dialog
    // ========================================================================

    async showTravelDialog() {
        if (!this.currentLocation || !this.currentLocation.connections) {
            this.showNotification('No destinations available', 'warning');
            return;
        }

        const connections = this.currentLocation.connections;

        if (connections.length === 0) {
            this.showNotification('No connected locations', 'warning');
            return;
        }

        const modal = this.createModal('Choose Destination', `
            <div class="travel-container">
                <p style="margin-bottom: 20px; color: #b8a485;">
                    Where would you like to travel from ${this.currentLocation.name}?
                </p>
                <div class="location-list">
                    ${connections.map(conn => `
                        <div class="npc-card" onclick="game.selectTravel('${conn.id}')">
                            <div class="npc-name">📍 ${conn.name}</div>
                            <div class="npc-detail">Type: ${conn.template}</div>
                        </div>
                    `).join('')}
                </div>
                <button class="btn" onclick="game.closeModal()" style="margin-top: 20px; width: 100%;">
                    ❌ Cancel
                </button>
            </div>
        `);

        document.body.appendChild(modal);
    }

    async selectTravel(locationId) {
        this.closeModal();
        await this.travelToLocation(locationId);
    }

    // ========================================================================
    // Modal System
    // ========================================================================

    createModal(title, content) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>${title}</h2>
                    <button class="modal-close" onclick="game.closeModal()">✕</button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
            </div>
        `;
        return modal;
    }

    closeModal() {
        const modal = document.querySelector('.modal-overlay');
        if (modal) {
            modal.remove();
        }
    }

    showRestDialog() {
        const modal = this.createModal('Rest', `
            <p style="text-align: center; color: #b8a485; margin: 20px 0;">
                Would you like to rest here and restore your energy?
            </p>
            <div style="display: flex; gap: 10px;">
                <button class="btn" onclick="game.rest(); game.closeModal();" style="flex: 1;">
                    ✅ Rest
                </button>
                <button class="btn" onclick="game.closeModal()" style="flex: 1;">
                    ❌ Cancel
                </button>
            </div>
        `);
        document.body.appendChild(modal);
    }

    showMarketDialog() {
        const modal = this.createModal('Market', `
            <p style="text-align: center; color: #b8a485; margin: 20px 0;">
                Market system coming soon!
            </p>
            <button class="btn" onclick="game.closeModal()" style="width: 100%;">
                Close
            </button>
        `);
        document.body.appendChild(modal);
    }

    rest() {
        this.showNotification('You rest and restore your energy...', 'success');
    }

    async refreshLocation() {
        if (this.currentLocation) {
            await this.setLocation(this.currentLocation.id);
            this.showNotification('Location refreshed', 'info');
        }
    }

    // ========================================================================
    // Events Display
    // ========================================================================

    addEvent(event) {
        // Avoid duplicates
        if (this.events.some(e => JSON.stringify(e) === JSON.stringify(event))) {
            return;
        }

        this.events.push(event);
        if (this.events.length > 50) {
            this.events.shift(); // Keep only last 50 events
        }

        this.updateEventsDisplay();
    }

    updateEventsDisplay() {
        const eventList = document.querySelector('[data-page="events"] .event-list');
        if (!eventList) return;

        if (this.events.length === 0) {
            eventList.innerHTML = '<div class="event">No events yet...</div>';
            return;
        }

        // Show most recent first
        const reversed = [...this.events].reverse();
        eventList.innerHTML = reversed.map(event => {
            const eventText = typeof event === 'string' ? event : event.description || JSON.stringify(event);
            return `<div class="event">${eventText}</div>`;
        }).join('');
    }

    // ========================================================================
    // Map Display
    // ========================================================================

    async showMapPage() {
        await this.loadLocations();

        const mapPage = document.querySelector('[data-page="map"]');
        if (!mapPage) return;

        const section = mapPage.querySelector('.section');
        if (!section) return;

        section.innerHTML = `
            <div class="section-title">Discovered Locations</div>
            <div class="map-grid">
                ${this.locations.map(loc => `
                    <div class="map-location ${loc.id === this.currentLocation?.id ? 'current' : ''}"
                         onclick="game.travelToLocation('${loc.id}')">
                        <div class="map-location-name">📍 ${loc.name}</div>
                        <div class="map-location-info">
                            <span>Type: ${loc.template}</span>
                            <span>NPCs: ${loc.npc_count || 0}</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    // ========================================================================
    // Notifications
    // ========================================================================

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.classList.add('notification-show');
        }, 10);

        setTimeout(() => {
            notification.classList.remove('notification-show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// Initialize game when page loads
let game;
window.addEventListener('DOMContentLoaded', () => {
    game = new RGenGame();
});
