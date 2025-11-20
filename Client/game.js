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
        this.player = null;
        this.isAuthenticated = false;

        // Initialize
        this.init();
    }

    async init() {
        console.log('Initializing R-Gen Game Client...');

        // Check if authenticated
        await this.checkAuth();

        if (!this.isAuthenticated) {
            this.showAuthModal();
            this.setupAuthHandlers();
            return;
        }

        // Hide auth modal if showing
        this.hideAuthModal();

        // Show logout button
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.style.display = 'block';
            logoutBtn.onclick = () => this.logout();
        }

        // Connect to WebSocket
        this.connectWebSocket();

        // Load initial data
        await this.loadWorldInfo();
        await this.loadLocations();
        await this.loadNPCs();
        await this.loadEvents();
        await this.loadPlayerData();
        await this.loadPlayerInventory();

        // Set initial location
        if (this.player && this.player.current_location_id) {
            await this.setLocation(this.player.current_location_id);
        } else if (this.locations.length > 0) {
            await this.setLocation(this.locations[0].id);
        }

        // Update character page with player data
        this.updateCharacterPage();

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
            const response = await fetch(`${this.apiUrl}/api${endpoint}`, {
                credentials: 'include' // Include cookies for session
            });
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
                body: JSON.stringify(data),
                credentials: 'include' // Include cookies for session
            });
            if (!response.ok) {
                const errorData = await response.json().catch(() => null);
                throw new Error(errorData?.error || `HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`API POST error (${endpoint}):`, error);
            this.showNotification(`Error: ${error.message}`, 'error');
            return null;
        }
    }

    // ========================================================================
    // Authentication
    // ========================================================================

    async checkAuth() {
        try {
            const response = await fetch(`${this.apiUrl}/api/player/me`, {
                credentials: 'include'
            });
            if (response.ok) {
                const data = await response.json();
                this.player = data.player;
                this.isAuthenticated = true;
                console.log('Authenticated as:', this.player.username);
                return true;
            }
        } catch (error) {
            console.log('Not authenticated');
        }
        this.isAuthenticated = false;
        return false;
    }

    async login(username, password) {
        const data = await this.apiPost('/player/login', { username, password });
        if (data && data.success) {
            this.player = data.player;
            this.isAuthenticated = true;
            this.showNotification('Welcome back, ' + this.player.character_name + '!', 'success');
            // Reinitialize the game
            await this.init();
            return true;
        }
        return false;
    }

    async register(username, password, characterName, race, characterClass) {
        const data = await this.apiPost('/player/register', {
            username,
            password,
            character_name: characterName,
            race,
            class: characterClass
        });
        if (data && data.success) {
            this.player = data.player;
            this.isAuthenticated = true;
            this.showNotification('Welcome to the realm, ' + this.player.character_name + '!', 'success');
            // Reinitialize the game
            await this.init();
            return true;
        }
        return false;
    }

    async logout() {
        const data = await this.apiPost('/player/logout', {});
        if (data && data.success) {
            this.player = null;
            this.isAuthenticated = false;
            this.showNotification('You have left the realm', 'info');
            // Reload page to show login
            window.location.reload();
        }
    }

    async loadPlayerData() {
        try {
            const response = await fetch(`${this.apiUrl}/api/player/me`, {
                credentials: 'include'
            });
            if (response.ok) {
                const data = await response.json();
                this.player = data.player;
                console.log('Player data loaded:', this.player);
            }
        } catch (error) {
            console.error('Error loading player data:', error);
        }
    }

    showAuthModal() {
        const modal = document.getElementById('auth-modal');
        if (modal) {
            modal.style.display = 'flex';
        }
    }

    hideAuthModal() {
        const modal = document.getElementById('auth-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    setupAuthHandlers() {
        // Login button
        const loginBtn = document.getElementById('login-btn');
        if (loginBtn) {
            loginBtn.onclick = async () => {
                const username = document.getElementById('login-username').value;
                const password = document.getElementById('login-password').value;

                if (!username || !password) {
                    this.showNotification('Please enter username and password', 'warning');
                    return;
                }

                await this.login(username, password);
            };
        }

        // Register button
        const registerBtn = document.getElementById('register-btn');
        if (registerBtn) {
            registerBtn.onclick = async () => {
                const username = document.getElementById('register-username').value;
                const password = document.getElementById('register-password').value;
                const characterName = document.getElementById('register-character-name').value;
                const race = document.getElementById('register-race').value;
                const characterClass = document.getElementById('register-class').value;

                if (!username || !password || !characterName) {
                    this.showNotification('Please fill in all required fields', 'warning');
                    return;
                }

                await this.register(username, password, characterName, race, characterClass);
            };
        }

        // Enter key support
        const loginInputs = ['login-username', 'login-password'];
        loginInputs.forEach(id => {
            const input = document.getElementById(id);
            if (input) {
                input.onkeypress = (e) => {
                    if (e.key === 'Enter') loginBtn?.click();
                };
            }
        });
    }

    updateCharacterPage() {
        if (!this.player) return;

        // Update character page title
        const charTitle = document.querySelector('[data-page="character"] .page-title');
        if (charTitle) {
            charTitle.textContent = `⚔ ${this.player.character_name} ⚔`;
        }

        // Update subtitle
        const charSubtitle = document.querySelector('[data-page="character"] .page-subtitle');
        if (charSubtitle) {
            charSubtitle.textContent = `~ Level ${this.player.level} ${this.player.race} ${this.player.class} ~`;
        }

        // Update gold
        const goldBadge = document.querySelector('[data-page="character"] .gold-badge');
        if (goldBadge) {
            goldBadge.textContent = `💰 ${this.player.gold} Gold Coins`;
        }

        // Update stats if available
        if (this.player.stats) {
            this.updateStatsDisplay(this.player.stats);
        }

        // Update equipped items display
        this.updateEquippedItemsDisplay();
    }

    async loadPlayerInventory() {
        try {
            const response = await fetch(`${this.apiUrl}/api/player/inventory`, {
                credentials: 'include'
            });
            if (response.ok) {
                const data = await response.json();
                if (this.player) {
                    this.player.inventory = data.inventory;
                }
                this.updateInventoryPage();
                console.log('Inventory loaded:', data.inventory);
            }
        } catch (error) {
            console.error('Error loading inventory:', error);
        }
    }

    updateInventoryPage() {
        if (!this.player || !this.player.inventory) return;

        const inventory = this.player.inventory;
        const itemList = document.querySelector('[data-page="inventory"] .item-list');

        if (!itemList) return;

        // Separate equipped and unequipped items
        const equippedItems = inventory.filter(item => item.equipped);
        const unequippedItems = inventory.filter(item => !item.equipped);

        // Clear the item list
        itemList.innerHTML = '';

        // Add equipped items section
        if (equippedItems.length > 0) {
            equippedItems.forEach(item => {
                const itemDiv = this.createInventoryItemElement(item);
                itemList.appendChild(itemDiv);
            });
        }

        // Add unequipped items section
        if (unequippedItems.length > 0) {
            unequippedItems.forEach(item => {
                const itemDiv = this.createInventoryItemElement(item);
                itemList.appendChild(itemDiv);
            });
        }

        // Update subtitle with count
        const subtitle = document.querySelector('[data-page="inventory"] .page-subtitle');
        if (subtitle) {
            subtitle.textContent = `~ Carrying ${inventory.length} items ~`;
        }
    }

    createInventoryItemElement(item) {
        const itemDiv = document.createElement('div');
        const rarityClass = (item.item_data?.rarity || 'common').toLowerCase();
        itemDiv.className = `item ${rarityClass}`;

        // Get icon based on item type
        let icon = '📦';
        const itemType = item.item_type?.toLowerCase() || '';
        if (itemType.includes('weapon')) icon = '⚔️';
        else if (itemType.includes('armor') || itemType.includes('shield')) icon = '🛡️';
        else if (itemType.includes('potion') || itemType.includes('consumable')) icon = '🧪';
        else if (itemType.includes('ring') || itemType.includes('amulet')) icon = '💍';

        // Build display text
        let displayText = `${icon} `;
        if (item.item_data?.rarity) {
            displayText += `${item.item_data.rarity} `;
        }
        displayText += item.item_name;

        // Add stats if available
        if (item.item_data?.damage) {
            displayText += ` (+${item.item_data.damage} DMG)`;
        } else if (item.item_data?.defense) {
            displayText += ` (+${item.item_data.defense} DEF)`;
        }

        if (item.quantity > 1) {
            displayText += ` x${item.quantity}`;
        }

        if (item.equipped) {
            displayText += ' [EQUIPPED]';
        }

        itemDiv.textContent = displayText;
        itemDiv.onclick = () => this.showItemDetailsOnRightPage(item);

        return itemDiv;
    }

    updateEquippedItemsDisplay() {
        if (!this.player || !this.player.inventory) return;

        const equippedItems = this.player.inventory.filter(item => item.equipped);
        const rightCharContent = document.getElementById('right-character-content');

        if (!rightCharContent) return;

        if (equippedItems.length === 0) {
            rightCharContent.innerHTML = `
                <div class="section-title">Currently Equipped</div>
                <div class="description" style="text-align: center; color: #b8a485;">
                    You have no items equipped. Visit the Items tab to equip gear.
                </div>
            `;
            return;
        }

        // Build equipped items display
        let html = '<div class="section-title">Currently Equipped</div>';

        equippedItems.forEach(item => {
            const rarityClass = (item.item_data?.rarity || 'common').toLowerCase();

            html += `
                <div class="item ${rarityClass}" style="margin-bottom: 10px; cursor: pointer;" onclick="game.showItemDetailsOnRightPage(${JSON.stringify(item).replace(/"/g, '&quot;')})">
                    <div style="font-weight: bold; margin-bottom: 5px;">
                        ${item.item_name}
                    </div>
                    <div style="font-size: 0.9em; opacity: 0.9;">
                        Type: ${item.item_type}
                        ${item.item_data?.damage ? ` | Damage: +${item.item_data.damage}` : ''}
                        ${item.item_data?.defense ? ` | Defense: +${item.item_data.defense}` : ''}
                    </div>
                </div>
            `;
        });

        rightCharContent.innerHTML = html;
    }

    updateStatsDisplay(stats) {
        const statItems = {
            health: { label: '❤️ Health', color: 'health' },
            mana: { label: '✨ Mana', color: 'mana' },
            energy: { label: '⚡ Energy', color: 'energy' }
        };

        Object.entries(statItems).forEach(([key, config]) => {
            const current = stats[key];
            const max = stats[`max_${key}`];
            const percent = (current / max) * 100;

            // Update label
            const label = document.querySelector(`[data-page="character"] .stat-label span:first-child`);
            if (label && label.textContent.includes(config.label.substring(2))) {
                const valueSpan = label.parentElement.querySelector('span:last-child');
                if (valueSpan) {
                    valueSpan.textContent = `${current} / ${max}`;
                }
            }

            // Update bar
            const bars = document.querySelectorAll(`[data-page="character"] .stat-bar-fill.${config.color}`);
            bars.forEach(bar => {
                bar.style.width = `${percent}%`;
            });
        });
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
            <div class="npc-card" data-npc-id="${npcData.id}"
                 onclick="game.showNPCDetailsOnRightPage('${npcData.id}')"
                 ondblclick="game.showNPCDialogue('${npcData.id}')">
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
    // Right Page Detail Views
    // ========================================================================

    async showNPCDetailsOnRightPage(npcId) {
        const data = await this.apiGet(`/npc/${npcId}/dialogue`);
        if (!data) return;

        const title = document.getElementById('right-world-title');
        const subtitle = document.getElementById('right-world-subtitle');
        const content = document.getElementById('right-world-content');

        if (title) title.textContent = `⚔ ${data.npc_name} ⚔`;
        if (subtitle) subtitle.textContent = `~ ${data.profession} ~`;

        if (content) {
            content.innerHTML = `
                <div style="text-align: center; margin-bottom: 20px;">
                    <div style="font-size: 64px; margin-bottom: 10px;">
                        ${this.getNPCIcon(data.profession)}
                    </div>
                </div>

                <div class="section">
                    <div class="section-title">Character Info</div>
                    <div class="info-box">
                        <div class="info-row">
                            <span class="label">Level:</span>
                            <span>${data.level || 1}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">Profession:</span>
                            <span>${data.profession}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">Mood:</span>
                            <span>${data.mood || 'Neutral'}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">Activity:</span>
                            <span>${data.current_activity || 'Idle'}</span>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <div class="section-title">Greeting</div>
                    <div class="description" style="font-style: italic;">
                        "${data.dialogues?.greeting || 'Hello there, traveler.'}"
                    </div>
                </div>

                <div class="section">
                    <div class="section-title">About Their Work</div>
                    <div class="description" style="font-style: italic; text-indent: 0;">
                        "${data.dialogues?.profession || 'I do my work with pride.'}"
                    </div>
                </div>

                <div class="section" style="margin-top: auto;">
                    <button class="btn" onclick="game.showNPCDialogue('${npcId}')" style="width: 100%;">
                        💬 Start Conversation
                    </button>
                </div>
            `;
        }
    }

    showLocationDetailsOnRightPage(location) {
        const title = document.getElementById('right-map-title');
        const subtitle = document.getElementById('right-map-subtitle');
        const content = document.getElementById('right-map-content');

        if (title) title.textContent = `⚔ ${location.name} ⚔`;
        if (subtitle) subtitle.textContent = `~ ${location.template} ~`;

        if (content) {
            const isCurrent = location.id === this.currentLocation?.id;
            content.innerHTML = `
                <div class="section">
                    <div class="section-title">Location Details</div>
                    <div class="info-box">
                        <div class="info-row">
                            <span class="label">Type:</span>
                            <span>${location.template}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">NPCs Present:</span>
                            <span>${location.npc_count || 0}</span>
                        </div>
                        ${isCurrent ? `
                        <div class="info-row">
                            <span class="label">Status:</span>
                            <span style="color: #d4af37; font-weight: bold;">📍 Current Location</span>
                        </div>
                        ` : ''}
                    </div>
                </div>

                <div class="section">
                    <div class="section-title">Description</div>
                    <div class="description">
                        ${location.description || 'A mysterious location awaits your discovery.'}
                    </div>
                </div>

                ${!isCurrent ? `
                <div class="section" style="margin-top: auto;">
                    <button class="btn" onclick="game.travelToLocation('${location.id}')" style="width: 100%;">
                        🗺️ Travel Here
                    </button>
                </div>
                ` : `
                <div class="section" style="margin-top: auto;">
                    <div class="description" style="text-align: center; color: #d4af37;">
                        You are currently at this location
                    </div>
                </div>
                `}
            `;
        }
    }

    showEventDetailsOnRightPage(event, index) {
        const title = document.getElementById('right-events-title');
        const subtitle = document.getElementById('right-events-subtitle');
        const content = document.getElementById('right-events-content');

        const eventText = typeof event === 'string' ? event : event.description || JSON.stringify(event);
        const eventTime = event.timestamp ? new Date(event.timestamp).toLocaleString() : 'Recently';

        if (title) title.textContent = `⚔ Event #${index + 1} ⚔`;
        if (subtitle) subtitle.textContent = `~ ${eventTime} ~`;

        if (content) {
            content.innerHTML = `
                <div class="section">
                    <div class="section-title">Event Description</div>
                    <div class="description">
                        ${eventText}
                    </div>
                </div>

                ${event.location ? `
                <div class="section">
                    <div class="section-title">Location</div>
                    <div class="info-box">
                        <div class="info-row">
                            <span class="label">Where:</span>
                            <span>${event.location}</span>
                        </div>
                    </div>
                </div>
                ` : ''}

                ${event.details ? `
                <div class="section">
                    <div class="section-title">Additional Details</div>
                    <div class="description" style="text-indent: 0;">
                        ${event.details}
                    </div>
                </div>
                ` : ''}
            `;
        }
    }

    showItemDetailsOnRightPage(item) {
        const title = document.getElementById('right-inventory-title');
        const subtitle = document.getElementById('right-inventory-subtitle');
        const content = document.getElementById('right-inventory-content');

        const rarity = item.rarity || 'Common';
        const rarityColor = {
            'Legendary': '#ffd700',
            'Rare': '#6495ed',
            'Uncommon': '#32cd32',
            'Common': '#b8a485'
        };

        if (title) title.textContent = `⚔ ${item.name} ⚔`;
        if (subtitle) subtitle.innerHTML = `~ <span style="color: ${rarityColor[rarity] || '#b8a485'}">${rarity}</span> ${item.type || 'Item'} ~`;

        if (content) {
            content.innerHTML = `
                <div class="section">
                    <div class="section-title">Item Statistics</div>
                    <div class="info-box">
                        ${item.damage ? `
                        <div class="info-row">
                            <span class="label">⚔️ Damage:</span>
                            <span>+${item.damage}</span>
                        </div>
                        ` : ''}
                        ${item.defense ? `
                        <div class="info-row">
                            <span class="label">🛡️ Defense:</span>
                            <span>+${item.defense}</span>
                        </div>
                        ` : ''}
                        ${item.magic_power ? `
                        <div class="info-row">
                            <span class="label">✨ Magic Power:</span>
                            <span>+${item.magic_power}</span>
                        </div>
                        ` : ''}
                        ${item.value ? `
                        <div class="info-row">
                            <span class="label">💰 Value:</span>
                            <span>${item.value} Gold</span>
                        </div>
                        ` : ''}
                        ${item.weight ? `
                        <div class="info-row">
                            <span class="label">⚖️ Weight:</span>
                            <span>${item.weight} lbs</span>
                        </div>
                        ` : ''}
                    </div>
                </div>

                <div class="section">
                    <div class="section-title">Description</div>
                    <div class="description">
                        ${item.description || 'A mysterious item with unknown properties.'}
                    </div>
                </div>

                ${item.special_effects ? `
                <div class="section">
                    <div class="section-title">Special Effects</div>
                    <div class="description" style="text-indent: 0; color: #d4af37;">
                        ${item.special_effects}
                    </div>
                </div>
                ` : ''}

                <div class="section" style="margin-top: auto;">
                    <div class="action-grid">
                        ${item.equipped ? `
                        <button class="btn" onclick="game.unequipItem('${item.id}')">
                            ❌ Unequip
                        </button>
                        ` : item.type !== 'Consumable' ? `
                        <button class="btn" onclick="game.equipItem('${item.id}')">
                            ⚔️ Equip
                        </button>
                        ` : ''}
                        ${item.type === 'Consumable' ? `
                        <button class="btn" onclick="game.useItem('${item.id}')">
                            🍖 Use
                        </button>
                        ` : ''}
                        <button class="btn" onclick="game.discardItem('${item.id}')">
                            🗑️ Discard
                        </button>
                    </div>
                </div>
            `;
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
        eventList.innerHTML = reversed.map((event, index) => {
            const eventText = typeof event === 'string' ? event : event.description || JSON.stringify(event);
            const eventJson = JSON.stringify(event).replace(/"/g, '&quot;');
            return `<div class="event" onclick="game.showEventDetailsOnRightPage(JSON.parse('${eventJson}'), ${index})" style="cursor: pointer;">${eventText}</div>`;
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
                ${this.locations.map(loc => {
                    const locJson = JSON.stringify(loc).replace(/"/g, '&quot;');
                    return `
                    <div class="map-location ${loc.id === this.currentLocation?.id ? 'current' : ''}"
                         onclick="game.showLocationDetailsOnRightPage(JSON.parse('${locJson}'))"
                         ondblclick="game.travelToLocation('${loc.id}')">
                        <div class="map-location-name">📍 ${loc.name}</div>
                        <div class="map-location-info">
                            <span>Type: ${loc.template}</span>
                            <span>NPCs: ${loc.npc_count || 0}</span>
                        </div>
                    </div>
                    `;
                }).join('')}
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

    // ========================================================================
    // Item Management (Placeholders)
    // ========================================================================

    async equipItem(itemId) {
        try {
            const response = await fetch(`/api/player/inventory/${itemId}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ equipped: true })
            });

            const data = await response.json();

            if (response.ok) {
                this.showNotification('Item equipped successfully!', 'success');
                // Reload inventory to update display
                await this.loadPlayerInventory();
                // Update character page to show newly equipped item
                this.updateEquippedItemsDisplay();
            } else {
                this.showNotification(data.error || 'Failed to equip item', 'error');
            }
        } catch (error) {
            console.error('Error equipping item:', error);
            this.showNotification('Failed to equip item', 'error');
        }
    }

    async unequipItem(itemId) {
        try {
            const response = await fetch(`/api/player/inventory/${itemId}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ equipped: false })
            });

            const data = await response.json();

            if (response.ok) {
                this.showNotification('Item unequipped', 'info');
                // Reload inventory to update display
                await this.loadPlayerInventory();
                // Update character page
                this.updateEquippedItemsDisplay();
            } else {
                this.showNotification(data.error || 'Failed to unequip item', 'error');
            }
        } catch (error) {
            console.error('Error unequipping item:', error);
            this.showNotification('Failed to unequip item', 'error');
        }
    }

    async useItem(itemId) {
        this.showNotification('Using item...', 'info');
        // TODO: Implement item usage via API (consume potions, etc.)
        console.log('Use item:', itemId);
    }

    async discardItem(itemId) {
        const confirmed = confirm('Are you sure you want to discard this item?');
        if (!confirmed) return;

        try {
            const response = await fetch(`/api/player/inventory/${itemId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (response.ok) {
                this.showNotification('Item discarded', 'warning');
                // Reload inventory to update display
                await this.loadPlayerInventory();
                // Clear right page if this item was being displayed
                const rightInventoryContent = document.getElementById('right-inventory-content');
                if (rightInventoryContent) {
                    rightInventoryContent.innerHTML = `
                        <div class="description" style="text-align: center; color: #b8a485;">
                            Select an item from your inventory to view its details.
                        </div>
                    `;
                }
            } else {
                this.showNotification(data.error || 'Failed to discard item', 'error');
            }
        } catch (error) {
            console.error('Error discarding item:', error);
            this.showNotification('Failed to discard item', 'error');
        }
    }

    // ========================================================================
    // Crafting System
    // ========================================================================

    showCraftDetailOnRightPage(type, data) {
        const rightCraftTitle = document.getElementById('right-craft-title');
        const rightCraftSubtitle = document.getElementById('right-craft-subtitle');
        const rightCraftContent = document.getElementById('right-craft-content');

        if (!rightCraftContent) return;

        if (type === 'profession') {
            this.showProfessionDetail(data, rightCraftTitle, rightCraftSubtitle, rightCraftContent);
        } else if (type === 'recipe') {
            this.showRecipeDetail(data, rightCraftTitle, rightCraftSubtitle, rightCraftContent);
        } else if (type === 'material') {
            this.showMaterialDetail(data, rightCraftTitle, rightCraftSubtitle, rightCraftContent);
        }
    }

    showProfessionDetail(professionName, titleEl, subtitleEl, contentEl) {
        const professions = {
            blacksmithing: {
                name: 'Blacksmithing',
                icon: '⚒️',
                level: 8,
                xp: 750,
                nextLevel: 1000,
                description: 'The ancient art of forging metal into weapons and armor. Blacksmiths are masters of the forge, capable of creating powerful equipment for warriors.',
                benefits: [
                    'Craft weapons and heavy armor',
                    'Repair damaged equipment',
                    'Enhance gear with special properties',
                    'Unlock legendary weapon recipes at high levels'
                ],
                recipes: ['Iron Sword', 'Steel Helmet', 'Chain Mail', 'Battle Axe', 'Legendary Greatsword', 'Mithril Armor']
            },
            alchemy: {
                name: 'Alchemy',
                icon: '🧪',
                level: 6,
                xp: 480,
                nextLevel: 600,
                description: 'The mystical practice of combining reagents to create powerful potions and elixirs. Alchemists can brew concoctions that heal, enhance abilities, or cause devastating effects.',
                benefits: [
                    'Brew healing and mana potions',
                    'Create buff potions for combat',
                    'Transmute materials',
                    'Craft powerful explosives'
                ],
                recipes: ['Health Potion', 'Mana Potion', 'Strength Elixir', 'Poison Vial', 'Elixir of Life']
            },
            enchanting: {
                name: 'Enchanting',
                icon: '✨',
                level: 5,
                xp: 380,
                nextLevel: 500,
                description: 'The art of imbuing items with magical properties. Enchanters can enhance weapons and armor with powerful enchantments, making them far more effective.',
                benefits: [
                    'Add magical properties to equipment',
                    'Disenchant items to learn enchantments',
                    'Create enchanted scrolls',
                    'Craft powerful artifacts at high levels'
                ],
                recipes: ['Fire Weapon Enchant', 'Shield of Protection', 'Ring of Speed', 'Scroll of Wisdom']
            },
            leatherworking: {
                name: 'Leatherworking',
                icon: '🦌',
                level: 4,
                xp: 280,
                nextLevel: 400,
                description: 'The craft of working with leather and hides to create light armor and accessories. Leatherworkers can craft durable gear perfect for rangers and rogues.',
                benefits: [
                    'Craft light armor and leather goods',
                    'Create bags and containers',
                    'Tan rare hides for exotic armor',
                    'Make armor kits to enhance gear'
                ],
                recipes: ['Leather Armor', 'Hunting Boots', 'Leather Gloves', 'Dragon Scale Vest', 'Quiver']
            },
            tailoring: {
                name: 'Tailoring',
                icon: '🧵',
                level: 4,
                xp: 300,
                nextLevel: 400,
                description: 'The art of working with cloth and fabric to create robes and magical garments. Tailors specialize in creating gear for spellcasters and creating bags.',
                benefits: [
                    'Craft cloth armor and robes',
                    'Create magical garments',
                    'Sew enchanted bags',
                    'Make cloaks with special properties'
                ],
                recipes: ['Mage Robe', 'Silk Cloak', 'Netherweave Bag', 'Hood of Shadows', 'Embroidered Gloves']
            },
            jewelcrafting: {
                name: 'Jewelcrafting',
                icon: '💎',
                level: 3,
                xp: 200,
                nextLevel: 300,
                description: 'The delicate art of cutting gems and crafting jewelry. Jewelcrafters create rings, necklaces, and other accessories that grant powerful bonuses.',
                benefits: [
                    'Cut and polish precious gems',
                    'Craft rings and necklaces',
                    'Socket gems into equipment',
                    'Create legendary jewelry pieces'
                ],
                recipes: ['Ruby Ring', 'Sapphire Necklace', 'Diamond Amulet', 'Emerald Earrings', 'Crown of Kings']
            },
            cooking: {
                name: 'Cooking',
                icon: '🍳',
                level: 3,
                xp: 220,
                nextLevel: 300,
                description: 'The culinary arts provide sustenance and temporary buffs. Skilled cooks can prepare meals that grant significant advantages in battle and exploration.',
                benefits: [
                    'Prepare food that restores health',
                    'Cook meals that grant temporary buffs',
                    'Create travel rations',
                    'Unlock gourmet recipes'
                ],
                recipes: ['Bread', 'Grilled Meat', 'Vegetable Stew', 'Apple Pie', 'Feast Platter']
            },
            woodworking: {
                name: 'Woodworking',
                icon: '🪓',
                level: 3,
                xp: 190,
                nextLevel: 300,
                description: 'The craft of shaping wood into useful items. Woodworkers create staves, bows, shields, and furniture. Master woodworkers can craft legendary wooden weapons.',
                benefits: [
                    'Craft bows and staves',
                    'Create wooden shields',
                    'Build furniture and decorations',
                    'Make magical wands'
                ],
                recipes: ['Oak Bow', 'Maple Staff', 'Wooden Shield', 'Enchanted Wand', 'Ancient Staff']
            },
            engineering: {
                name: 'Engineering',
                icon: '⚙️',
                level: 2,
                xp: 140,
                nextLevel: 200,
                description: 'The science of creating mechanical devices and explosives. Engineers craft unique gadgets, bombs, and mechanical companions that provide utility and combat advantages.',
                benefits: [
                    'Create bombs and explosives',
                    'Build mechanical pets',
                    'Craft goggles and trinkets',
                    'Make siege weapons'
                ],
                recipes: ['Dynamite', 'Mechanical Squirrel', 'Goggles of Vision', 'Portable Cannon', 'Rocket Boots']
            },
            inscription: {
                name: 'Inscription',
                icon: '📜',
                level: 2,
                xp: 120,
                nextLevel: 200,
                description: 'The art of creating magical scrolls, glyphs, and tomes. Scribes can craft powerful scrolls for instant spellcasting and create valuable books.',
                benefits: [
                    'Create magical scrolls',
                    'Inscribe glyphs to enhance abilities',
                    'Craft spellbooks and tomes',
                    'Make contracts and documents'
                ],
                recipes: ['Scroll of Fireball', 'Glyph of Strength', 'Tome of Knowledge', 'Contract Scroll', 'Ancient Codex']
            },
            mining: {
                name: 'Mining',
                icon: '⛏️',
                level: 2,
                xp: 150,
                nextLevel: 200,
                description: 'The gathering profession focused on extracting ores and gems from the earth. Miners provide essential materials for blacksmithing, engineering, and jewelcrafting.',
                benefits: [
                    'Extract ores from mineral veins',
                    'Find precious gems while mining',
                    'Smelt ores into usable bars',
                    'Discover rare materials in rich veins'
                ],
                recipes: ['Copper Bar', 'Iron Bar', 'Steel Ingot', 'Mithril Bar', 'Adamantite Ore']
            },
            herbalism: {
                name: 'Herbalism',
                icon: '🌿',
                level: 1,
                xp: 60,
                nextLevel: 100,
                description: 'The gathering profession of collecting herbs and plants. Herbalists gather ingredients essential for alchemy and inscription, finding rare plants in the wilderness.',
                benefits: [
                    'Gather herbs and flowers',
                    'Find rare alchemical reagents',
                    'Identify medicinal plants',
                    'Harvest magical herbs'
                ],
                recipes: ['Red Herb', 'Blue Flower', 'Moonpetal', 'Dragonbloom', 'Ancient Moss']
            },
            skinning: {
                name: 'Skinning',
                icon: '🔪',
                level: 1,
                xp: 45,
                nextLevel: 100,
                description: 'The gathering profession of collecting hides and leather from defeated creatures. Skinners provide essential materials for leatherworking.',
                benefits: [
                    'Skin beasts for leather',
                    'Harvest rare hides from exotic creatures',
                    'Obtain scales from dragons and serpents',
                    'Collect rare furs'
                ],
                recipes: ['Leather Scraps', 'Thick Hide', 'Dragon Scale', 'Bear Fur', 'Serpent Skin']
            },
            fishing: {
                name: 'Fishing',
                icon: '🎣',
                level: 1,
                xp: 30,
                nextLevel: 100,
                description: 'The peaceful art of catching fish from waters around the world. Fishers can catch fish for cooking, find treasure, and discover rare aquatic creatures.',
                benefits: [
                    'Catch fish for cooking',
                    'Find treasure in waters',
                    'Discover rare fish',
                    'Fish in any body of water'
                ],
                recipes: ['Raw Fish', 'Salmon', 'Treasure Chest', 'Golden Trout', 'Ancient Relic']
            },
            archaeology: {
                name: 'Archaeology',
                icon: '🏺',
                level: 1,
                xp: 25,
                nextLevel: 100,
                description: 'The scholarly profession of uncovering ancient artifacts and relics. Archaeologists can discover powerful items from lost civilizations and learn forgotten knowledge.',
                benefits: [
                    'Excavate dig sites for artifacts',
                    'Restore ancient relics',
                    'Discover lost treasures',
                    'Learn about ancient civilizations'
                ],
                recipes: ['Ancient Pottery', 'Fossil', 'Relic Fragment', 'Lost Artifact', 'Legendary Tome']
            }
        };

        const profession = professions[professionName.toLowerCase()] || professions.blacksmithing;

        if (titleEl) titleEl.textContent = `${profession.icon} ${profession.name} ${profession.icon}`;
        if (subtitleEl) subtitleEl.textContent = `~ Level ${profession.level} ~`;

        const progressPercent = (profession.xp / profession.nextLevel) * 100;

        contentEl.innerHTML = `
            <div class="section">
                <div class="section-title">Profession Level</div>
                <div class="description">
                    <strong>Current Level:</strong> ${profession.level}<br>
                    <strong>Experience:</strong> ${profession.xp} / ${profession.nextLevel} XP<br>
                    <div style="background: #2a1810; height: 20px; border: 1px solid #8b7355; margin-top: 10px; position: relative;">
                        <div style="background: linear-gradient(90deg, #cd7f32, #8b4513); height: 100%; width: ${progressPercent}%;"></div>
                        <span style="position: absolute; top: 2px; left: 50%; transform: translateX(-50%); color: #fff; font-size: 0.9em;">${Math.round(progressPercent)}%</span>
                    </div>
                </div>
            </div>

            <div class="section">
                <div class="section-title">About</div>
                <div class="description">
                    ${profession.description}
                </div>
            </div>

            <div class="section">
                <div class="section-title">Benefits</div>
                <div class="description">
                    ${profession.benefits.map(b => `• ${b}`).join('<br>')}
                </div>
            </div>

            <div class="section">
                <div class="section-title">Known Recipes (${profession.recipes.length})</div>
                <div class="description">
                    ${profession.recipes.map(r => `• ${r}`).join('<br>')}
                </div>
            </div>

            <div class="section" style="margin-top: auto;">
                <div class="action-grid">
                    <button class="btn" onclick="game.showNotification('Training not yet implemented', 'info')">
                        📚 Train
                    </button>
                    <button class="btn" onclick="game.showNotification('Recipe discovery coming soon', 'info')">
                        🔍 Discover Recipes
                    </button>
                </div>
            </div>
        `;
    }

    showRecipeDetail(recipe, titleEl, subtitleEl, contentEl) {
        if (titleEl) titleEl.textContent = `🔨 ${recipe.name} 🔨`;
        if (subtitleEl) subtitleEl.textContent = `~ ${recipe.profession} Recipe ~`;

        // Check if player has materials
        const materialsHtml = recipe.materials.map(mat => {
            // For demo purposes, we're showing if they have enough (this should check actual inventory)
            const hasEnough = true; // TODO: Check actual inventory
            const statusColor = hasEnough ? '#90EE90' : '#FF6B6B';
            return `<div style="color: ${statusColor};">• ${mat.name} x${mat.quantity}</div>`;
        }).join('');

        contentEl.innerHTML = `
            <div class="section">
                <div class="section-title">Recipe Information</div>
                <div class="description">
                    <strong>Profession:</strong> ${recipe.profession}<br>
                    <strong>Required Level:</strong> ${recipe.level}<br>
                    <strong>Difficulty:</strong> ${recipe.level <= 2 ? 'Easy' : recipe.level <= 4 ? 'Medium' : 'Hard'}
                </div>
            </div>

            <div class="section">
                <div class="section-title">Required Materials</div>
                <div class="description">
                    ${materialsHtml}
                </div>
            </div>

            <div class="section">
                <div class="section-title">Result</div>
                <div class="description">
                    Crafting this recipe will produce: <strong>${recipe.name}</strong><br>
                    ${recipe.name.includes('Sword') ? 'A sharp blade suitable for combat.' : ''}
                    ${recipe.name.includes('Potion') ? 'A restorative potion that heals wounds.' : ''}
                    ${recipe.name.includes('Bread') ? 'Nourishing bread that restores energy.' : ''}
                </div>
            </div>

            <div class="section" style="margin-top: auto;">
                <div class="action-grid">
                    <button class="btn" onclick="game.craftItem('${recipe.id}')">
                        🔨 Craft Item
                    </button>
                    <button class="btn" onclick="game.showNotification('Mass crafting coming soon', 'info')">
                        ⚡ Craft x5
                    </button>
                </div>
            </div>
        `;
    }

    showMaterialDetail(material, titleEl, subtitleEl, contentEl) {
        if (titleEl) titleEl.textContent = `📦 ${material.name} 📦`;
        if (subtitleEl) subtitleEl.textContent = `~ Crafting Material ~`;

        contentEl.innerHTML = `
            <div class="section">
                <div class="section-title">Material Information</div>
                <div class="description">
                    <strong>Quantity:</strong> ${material.quantity}<br>
                    <strong>Type:</strong> Crafting Material
                </div>
            </div>

            <div class="section">
                <div class="section-title">Description</div>
                <div class="description">
                    ${material.description}
                </div>
            </div>

            <div class="section">
                <div class="section-title">Used In</div>
                <div class="description">
                    ${material.name === 'Iron Ingot' ? '• Iron Sword<br>• Steel Helmet<br>• Chain Mail' : ''}
                    ${material.name === 'Wood' ? '• Iron Sword (handle)<br>• Wooden Shield<br>• Bow' : ''}
                    ${material.name === 'Red Herb' ? '• Health Potion<br>• Antidote<br>• Healing Salve' : ''}
                    ${material.name === 'Crystal Vial' ? '• All potions and elixirs' : ''}
                    ${material.name === 'Wheat' ? '• Bread<br>• Pastries<br>• Beer' : ''}
                </div>
            </div>

            <div class="section" style="margin-top: auto;">
                <div class="action-grid">
                    <button class="btn" onclick="game.showNotification('Gathering locations coming soon', 'info')">
                        🗺️ Find Sources
                    </button>
                    <button class="btn" onclick="game.showNotification('Trading not yet implemented', 'info')">
                        💰 Sell Material
                    </button>
                </div>
            </div>
        `;
    }

    craftItem(recipeId) {
        this.showNotification('Crafting system coming soon! This will create: ' + recipeId, 'info');
        console.log('Craft item:', recipeId);
        // TODO: Implement crafting via API
        // - Check materials
        // - Check profession level
        // - Consume materials
        // - Add crafted item to inventory
        // - Give profession XP
    }
}

// Initialize game when page loads
let game;
window.addEventListener('DOMContentLoaded', () => {
    game = new RGenGame();
});
