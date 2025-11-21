/**
 * R-Gen Master Control Panel
 * JavaScript for admin panel functionality
 */

// Global state
const state = {
    worldData: null,
    npcs: [],
    locations: [],
    players: [],
    items: [],
    currentTab: 'dashboard',
    filteredNPCs: [],
    filteredLocations: [],
    filteredPlayers: [],
    filteredItems: []
};

// API Base URL
const API_BASE = '/api/master';

// ============================================================================
// Initialization
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

async function initializeApp() {
    setupEventListeners();
    await loadAllData();
    switchTab('dashboard');
}

// ============================================================================
// Event Listeners
// ============================================================================

function setupEventListeners() {
    // Tab navigation
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const tab = btn.getAttribute('data-tab');
            switchTab(tab);
        });
    });

    // Refresh button
    document.getElementById('refresh-btn').addEventListener('click', loadAllData);

    // Dashboard quick actions
    document.getElementById('clear-events-btn').addEventListener('click', clearEvents);

    // World settings
    document.getElementById('save-world-btn').addEventListener('click', saveWorldSettings);

    // Search inputs
    document.getElementById('npc-search').addEventListener('input', (e) => filterNPCs(e.target.value));
    document.getElementById('location-search').addEventListener('input', (e) => filterLocations(e.target.value));
    document.getElementById('player-search').addEventListener('input', (e) => filterPlayers(e.target.value));
    document.getElementById('item-search').addEventListener('input', (e) => filterItems(e.target.value));

    // Simulation controls
    document.getElementById('sim-clear-events-btn').addEventListener('click', clearEvents);
    document.getElementById('sim-refresh-btn').addEventListener('click', loadAllData);

    // Modal close buttons
    document.querySelectorAll('.modal-close, .modal-close-btn').forEach(btn => {
        btn.addEventListener('click', closeAllModals);
    });

    // Click outside modal to close
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeAllModals();
            }
        });
    });

    // NPC Edit Form
    document.getElementById('npc-edit-form').addEventListener('submit', saveNPCChanges);
    document.getElementById('delete-npc-btn').addEventListener('click', deleteNPC);

    // Location Edit Form
    document.getElementById('location-edit-form').addEventListener('submit', saveLocationChanges);
    document.getElementById('delete-location-btn').addEventListener('click', deleteLocation);

    // Player Edit Form
    document.getElementById('player-edit-form').addEventListener('submit', savePlayerChanges);
    document.getElementById('delete-player-btn').addEventListener('click', deletePlayer);

    // Add Item Form
    document.getElementById('add-item-btn').addEventListener('click', showAddItemModal);
    document.getElementById('add-item-form').addEventListener('submit', addItemToInventory);

    // Item Generation
    document.getElementById('generate-items-btn').addEventListener('click', generateItems);
}

// ============================================================================
// Data Loading
// ============================================================================

async function loadAllData() {
    showToast('Loading data...', 'info');

    try {
        await Promise.all([
            loadWorldData(),
            loadNPCs(),
            loadLocations(),
            loadPlayers(),
            loadItems()
        ]);

        updateDashboard();
        showToast('Data loaded successfully', 'success');
    } catch (error) {
        console.error('Error loading data:', error);
        showToast('Error loading data', 'error');
    }
}

async function loadWorldData() {
    const response = await fetch(`${API_BASE}/world`);
    const data = await response.json();
    state.worldData = data;

    // Update header
    document.getElementById('world-name').textContent = data.name;

    // Update world form
    document.getElementById('world-name-input').value = data.name;
    document.getElementById('world-description').value = data.description || '';
    document.getElementById('world-seed').value = data.seed || 'N/A';
}

async function loadNPCs() {
    const response = await fetch(`${API_BASE}/npcs`);
    const data = await response.json();
    state.npcs = data.npcs;
    state.filteredNPCs = data.npcs;

    renderNPCsTable();
}

async function loadLocations() {
    const response = await fetch(`${API_BASE}/locations`);
    const data = await response.json();
    state.locations = data.locations;
    state.filteredLocations = data.locations;

    renderLocationsTable();
}

async function loadPlayers() {
    const response = await fetch(`${API_BASE}/players`);
    const data = await response.json();
    state.players = data.players;
    state.filteredPlayers = data.players;

    renderPlayersTable();
}

async function loadItems() {
    const response = await fetch(`${API_BASE}/items`);
    const data = await response.json();
    state.items = data.items || [];
    state.filteredItems = data.items || [];

    renderItemsTable();
}

// ============================================================================
// Tab Navigation
// ============================================================================

function switchTab(tabName) {
    state.currentTab = tabName;

    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-tab') === tabName);
    });

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.toggle('active', content.id === `${tabName}-tab`);
    });
}

// ============================================================================
// Dashboard
// ============================================================================

function updateDashboard() {
    if (!state.worldData) return;

    document.getElementById('stat-locations').textContent = state.worldData.stats.total_locations;
    document.getElementById('stat-npcs').textContent = state.worldData.stats.total_npcs;
    document.getElementById('stat-players').textContent = state.players.length;
    document.getElementById('stat-events').textContent = state.worldData.stats.total_events;
}

// ============================================================================
// World Settings
// ============================================================================

async function saveWorldSettings(e) {
    e.preventDefault();

    const updates = {
        name: document.getElementById('world-name-input').value,
        description: document.getElementById('world-description').value
    };

    try {
        const response = await fetch(`${API_BASE}/world`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updates)
        });

        const data = await response.json();
        if (data.success) {
            showToast('World settings saved', 'success');
            await loadWorldData();
            updateDashboard();
        } else {
            showToast('Error saving world settings', 'error');
        }
    } catch (error) {
        console.error('Error saving world:', error);
        showToast('Error saving world settings', 'error');
    }
}

// ============================================================================
// NPCs Management
// ============================================================================

function renderNPCsTable() {
    const tbody = document.getElementById('npcs-table-body');
    const npcs = state.filteredNPCs;

    document.getElementById('npc-count').textContent = `${npcs.length} NPCs`;

    if (npcs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="loading">No NPCs found</td></tr>';
        return;
    }

    tbody.innerHTML = npcs.map(npc => `
        <tr>
            <td><strong>${escapeHtml(npc.name)}</strong></td>
            <td>${escapeHtml(npc.profession)}</td>
            <td>${getLocationName(npc.current_location_id)}</td>
            <td><span class="badge badge-info">${escapeHtml(npc.current_activity)}</span></td>
            <td>${formatNumber(npc.energy, 1)}</td>
            <td>${formatNumber(npc.mood, 1)}</td>
            <td>${npc.gold}g</td>
            <td>${npc.active ? '<span class="badge badge-success">Yes</span>' : '<span class="badge badge-danger">No</span>'}</td>
            <td>
                <button class="btn btn-primary action-btn" onclick="editNPC('${npc.id}')">✏️ Edit</button>
            </td>
        </tr>
    `).join('');
}

function filterNPCs(query) {
    const lowerQuery = query.toLowerCase();
    state.filteredNPCs = state.npcs.filter(npc =>
        npc.name.toLowerCase().includes(lowerQuery) ||
        npc.profession.toLowerCase().includes(lowerQuery) ||
        npc.current_activity.toLowerCase().includes(lowerQuery)
    );
    renderNPCsTable();
}

function editNPC(npcId) {
    const npc = state.npcs.find(n => n.id === npcId);
    if (!npc) return;

    document.getElementById('edit-npc-id').value = npc.id;
    document.getElementById('edit-npc-name').value = npc.name;
    document.getElementById('edit-npc-profession').value = npc.profession;
    document.getElementById('edit-npc-energy').value = npc.energy;
    document.getElementById('edit-npc-hunger').value = npc.hunger;
    document.getElementById('edit-npc-mood').value = npc.mood;
    document.getElementById('edit-npc-gold').value = npc.gold;
    document.getElementById('edit-npc-activity').value = npc.current_activity;
    document.getElementById('edit-npc-work-start').value = npc.work_start_hour;
    document.getElementById('edit-npc-work-end').value = npc.work_end_hour;
    document.getElementById('edit-npc-active').checked = npc.active;

    showModal('npc-modal');
}

async function saveNPCChanges(e) {
    e.preventDefault();

    const npcId = document.getElementById('edit-npc-id').value;
    const updates = {
        energy: parseFloat(document.getElementById('edit-npc-energy').value),
        hunger: parseFloat(document.getElementById('edit-npc-hunger').value),
        mood: parseFloat(document.getElementById('edit-npc-mood').value),
        gold: parseInt(document.getElementById('edit-npc-gold').value),
        current_activity: document.getElementById('edit-npc-activity').value,
        work_start_hour: parseInt(document.getElementById('edit-npc-work-start').value),
        work_end_hour: parseInt(document.getElementById('edit-npc-work-end').value),
        active: document.getElementById('edit-npc-active').checked
    };

    try {
        const response = await fetch(`${API_BASE}/npc/${npcId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updates)
        });

        const data = await response.json();
        if (data.success) {
            showToast('NPC updated successfully', 'success');
            await loadNPCs();
            closeAllModals();
        } else {
            showToast('Error updating NPC', 'error');
        }
    } catch (error) {
        console.error('Error updating NPC:', error);
        showToast('Error updating NPC', 'error');
    }
}

async function deleteNPC() {
    if (!confirm('Are you sure you want to delete this NPC? This cannot be undone.')) {
        return;
    }

    const npcId = document.getElementById('edit-npc-id').value;

    try {
        const response = await fetch(`${API_BASE}/npc/${npcId}`, {
            method: 'DELETE'
        });

        const data = await response.json();
        if (data.success) {
            showToast('NPC deleted successfully', 'success');
            await loadNPCs();
            updateDashboard();
            closeAllModals();
        } else {
            showToast('Error deleting NPC', 'error');
        }
    } catch (error) {
        console.error('Error deleting NPC:', error);
        showToast('Error deleting NPC', 'error');
    }
}

// ============================================================================
// Locations Management
// ============================================================================

function renderLocationsTable() {
    const tbody = document.getElementById('locations-table-body');
    const locations = state.filteredLocations;

    document.getElementById('location-count').textContent = `${locations.length} Locations`;

    if (locations.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="loading">No locations found</td></tr>';
        return;
    }

    tbody.innerHTML = locations.map(loc => `
        <tr>
            <td><strong>${escapeHtml(loc.name)}</strong></td>
            <td><span class="badge badge-secondary">${escapeHtml(loc.template)}</span></td>
            <td>${loc.npc_count}</td>
            <td>${escapeHtml(loc.current_weather || 'N/A')}</td>
            <td>${loc.market_open ? '<span class="badge badge-success">Open</span>' : '<span class="badge badge-danger">Closed</span>'}</td>
            <td>${loc.active ? '<span class="badge badge-success">Yes</span>' : '<span class="badge badge-danger">No</span>'}</td>
            <td>
                <button class="btn btn-primary action-btn" onclick="editLocation('${loc.id}')">✏️ Edit</button>
            </td>
        </tr>
    `).join('');
}

function filterLocations(query) {
    const lowerQuery = query.toLowerCase();
    state.filteredLocations = state.locations.filter(loc =>
        loc.name.toLowerCase().includes(lowerQuery) ||
        loc.template.toLowerCase().includes(lowerQuery) ||
        (loc.current_weather && loc.current_weather.toLowerCase().includes(lowerQuery))
    );
    renderLocationsTable();
}

function editLocation(locationId) {
    const location = state.locations.find(l => l.id === locationId);
    if (!location) return;

    document.getElementById('edit-location-id').value = location.id;
    document.getElementById('edit-location-name').value = location.name;
    document.getElementById('edit-location-description').value = location.description || '';
    document.getElementById('edit-location-template').value = location.template;
    document.getElementById('edit-location-weather').value = location.current_weather || 'Clear';
    document.getElementById('edit-location-market').checked = location.market_open;
    document.getElementById('edit-location-active').checked = location.active;

    showModal('location-modal');
}

async function saveLocationChanges(e) {
    e.preventDefault();

    const locationId = document.getElementById('edit-location-id').value;
    const updates = {
        current_weather: document.getElementById('edit-location-weather').value,
        market_open: document.getElementById('edit-location-market').checked,
        active: document.getElementById('edit-location-active').checked,
        data: {
            description: document.getElementById('edit-location-description').value
        }
    };

    try {
        const response = await fetch(`${API_BASE}/location/${locationId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updates)
        });

        const data = await response.json();
        if (data.success) {
            showToast('Location updated successfully', 'success');
            await loadLocations();
            closeAllModals();
        } else {
            showToast('Error updating location', 'error');
        }
    } catch (error) {
        console.error('Error updating location:', error);
        showToast('Error updating location', 'error');
    }
}

async function deleteLocation() {
    if (!confirm('Are you sure you want to delete this location? NPCs will be moved to another location.')) {
        return;
    }

    const locationId = document.getElementById('edit-location-id').value;

    try {
        const response = await fetch(`${API_BASE}/location/${locationId}`, {
            method: 'DELETE'
        });

        const data = await response.json();
        if (data.success) {
            showToast('Location deleted successfully', 'success');
            await loadLocations();
            await loadNPCs(); // Reload NPCs as they may have moved
            updateDashboard();
            closeAllModals();
        } else {
            showToast('Error deleting location', 'error');
        }
    } catch (error) {
        console.error('Error deleting location:', error);
        showToast('Error deleting location', 'error');
    }
}

// ============================================================================
// Players Management
// ============================================================================

function renderPlayersTable() {
    const tbody = document.getElementById('players-table-body');
    const players = state.filteredPlayers;

    document.getElementById('player-count').textContent = `${players.length} Players`;

    if (players.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="loading">No players found</td></tr>';
        return;
    }

    tbody.innerHTML = players.map(player => `
        <tr>
            <td><strong>${escapeHtml(player.username)}</strong></td>
            <td>${escapeHtml(player.character_name)}</td>
            <td>${escapeHtml(player.race)}</td>
            <td>${escapeHtml(player.class)}</td>
            <td>${player.level}</td>
            <td>${player.gold}g</td>
            <td>${player.profession_count}</td>
            <td>${player.inventory_count}</td>
            <td>
                <button class="btn btn-primary action-btn" onclick="editPlayer(${player.id})">✏️ Edit</button>
            </td>
        </tr>
    `).join('');
}

function filterPlayers(query) {
    const lowerQuery = query.toLowerCase();
    state.filteredPlayers = state.players.filter(player =>
        player.username.toLowerCase().includes(lowerQuery) ||
        player.character_name.toLowerCase().includes(lowerQuery) ||
        player.race.toLowerCase().includes(lowerQuery) ||
        player.class.toLowerCase().includes(lowerQuery)
    );
    renderPlayersTable();
}

function editPlayer(playerId) {
    const player = state.players.find(p => p.id === playerId);
    if (!player) return;

    document.getElementById('edit-player-id').value = player.id;
    document.getElementById('edit-player-username').value = player.username;
    document.getElementById('edit-player-character').value = player.character_name;
    document.getElementById('edit-player-race').value = player.race;
    document.getElementById('edit-player-class').value = player.class;
    document.getElementById('edit-player-level').value = player.level;
    document.getElementById('edit-player-experience').value = player.experience;
    document.getElementById('edit-player-gold').value = player.gold;

    if (player.stats) {
        document.getElementById('edit-player-health').value = player.stats.health;
        document.getElementById('edit-player-max-health').value = player.stats.max_health;
        document.getElementById('edit-player-mana').value = player.stats.mana;
        document.getElementById('edit-player-max-mana').value = player.stats.max_mana;
        document.getElementById('edit-player-str').value = player.stats.strength;
        document.getElementById('edit-player-dex').value = player.stats.dexterity;
        document.getElementById('edit-player-con').value = player.stats.constitution;
        document.getElementById('edit-player-int').value = player.stats.intelligence;
        document.getElementById('edit-player-wis').value = player.stats.wisdom;
        document.getElementById('edit-player-cha').value = player.stats.charisma;
    }

    // Load player inventory
    loadPlayerInventory(playerId);

    showModal('player-modal');
}

async function savePlayerChanges(e) {
    e.preventDefault();

    const playerId = parseInt(document.getElementById('edit-player-id').value);
    const updates = {
        character_name: document.getElementById('edit-player-character').value,
        race: document.getElementById('edit-player-race').value,
        class: document.getElementById('edit-player-class').value,
        level: parseInt(document.getElementById('edit-player-level').value),
        experience: parseInt(document.getElementById('edit-player-experience').value),
        gold: parseInt(document.getElementById('edit-player-gold').value),
        stats: {
            health: parseInt(document.getElementById('edit-player-health').value),
            max_health: parseInt(document.getElementById('edit-player-max-health').value),
            mana: parseInt(document.getElementById('edit-player-mana').value),
            max_mana: parseInt(document.getElementById('edit-player-max-mana').value),
            strength: parseInt(document.getElementById('edit-player-str').value),
            dexterity: parseInt(document.getElementById('edit-player-dex').value),
            constitution: parseInt(document.getElementById('edit-player-con').value),
            intelligence: parseInt(document.getElementById('edit-player-int').value),
            wisdom: parseInt(document.getElementById('edit-player-wis').value),
            charisma: parseInt(document.getElementById('edit-player-cha').value)
        }
    };

    try {
        const response = await fetch(`${API_BASE}/player/${playerId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updates)
        });

        const data = await response.json();
        if (data.success) {
            showToast('Player updated successfully', 'success');
            await loadPlayers();
            closeAllModals();
        } else {
            showToast('Error updating player', 'error');
        }
    } catch (error) {
        console.error('Error updating player:', error);
        showToast('Error updating player', 'error');
    }
}

async function deletePlayer() {
    if (!confirm('Are you sure you want to delete this player? This cannot be undone.')) {
        return;
    }

    const playerId = parseInt(document.getElementById('edit-player-id').value);

    try {
        const response = await fetch(`${API_BASE}/player/${playerId}`, {
            method: 'DELETE'
        });

        const data = await response.json();
        if (data.success) {
            showToast('Player deleted successfully', 'success');
            await loadPlayers();
            updateDashboard();
            closeAllModals();
        } else {
            showToast('Error deleting player', 'error');
        }
    } catch (error) {
        console.error('Error deleting player:', error);
        showToast('Error deleting player', 'error');
    }
}

// ============================================================================
// Player Inventory Management
// ============================================================================

async function loadPlayerInventory(playerId) {
    try {
        const response = await fetch(`${API_BASE}/player/${playerId}/inventory`);
        const data = await response.json();

        if (data.success === false) {
            throw new Error(data.error || 'Failed to load inventory');
        }

        renderInventoryList(data.inventory || []);
    } catch (error) {
        console.error('Error loading inventory:', error);
        document.getElementById('player-inventory-list').innerHTML = '<p class="error">Failed to load inventory</p>';
    }
}

function renderInventoryList(inventory) {
    const listElement = document.getElementById('player-inventory-list');

    if (inventory.length === 0) {
        listElement.innerHTML = '<p class="loading">No items in inventory</p>';
        return;
    }

    listElement.innerHTML = inventory.map(item => {
        // Parse item data
        let itemData = {};
        try {
            itemData = typeof item.data === 'string' ? JSON.parse(item.data) : item.data;
        } catch (e) {
            console.error('Error parsing item data:', e);
        }

        const rarity = itemData.rarity || 'common';
        const equipped = item.equipped ? '<span class="badge badge-success">Equipped</span>' : '';

        return `
            <div class="inventory-item" data-item-id="${item.id}">
                <div class="item-header">
                    <strong class="item-name rarity-${rarity}">${escapeHtml(item.item_name)}</strong>
                    <span class="item-type badge badge-secondary">${escapeHtml(item.item_type)}</span>
                    ${equipped}
                </div>
                <div class="item-details">
                    <span>Qty: ${item.quantity}</span>
                    ${itemData.damage ? `<span>Damage: ${itemData.damage}</span>` : ''}
                    ${itemData.defense ? `<span>Defense: ${itemData.defense}</span>` : ''}
                    ${itemData.value ? `<span>Value: ${itemData.value}g</span>` : ''}
                </div>
                ${itemData.description ? `<div class="item-description">${escapeHtml(itemData.description)}</div>` : ''}
                <div class="item-actions">
                    <button class="btn btn-sm btn-primary" onclick="editInventoryItem(${item.id}, ${item.equipped}, ${item.quantity})">Edit</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteInventoryItem(${item.id})">Delete</button>
                </div>
            </div>
        `;
    }).join('');
}

function showAddItemModal() {
    const playerId = document.getElementById('edit-player-id').value;
    document.getElementById('add-item-player-id').value = playerId;

    // Reset form
    document.getElementById('add-item-form').reset();
    document.getElementById('add-item-quantity').value = 1;
    document.getElementById('add-item-value').value = 0;

    showModal('add-item-modal');
}

async function addItemToInventory(e) {
    e.preventDefault();

    const playerId = parseInt(document.getElementById('add-item-player-id').value);
    const itemName = document.getElementById('add-item-name').value;
    const itemType = document.getElementById('add-item-type').value;
    const quantity = parseInt(document.getElementById('add-item-quantity').value);
    const equipped = document.getElementById('add-item-equipped').checked;
    const description = document.getElementById('add-item-description').value;
    const damage = document.getElementById('add-item-damage').value;
    const defense = document.getElementById('add-item-defense').value;
    const rarity = document.getElementById('add-item-rarity').value;
    const value = parseInt(document.getElementById('add-item-value').value);

    // Build item data
    const itemData = {
        description,
        rarity,
        value
    };

    if (damage) itemData.damage = parseInt(damage);
    if (defense) itemData.defense = parseInt(defense);

    try {
        const response = await fetch(`${API_BASE}/player/${playerId}/inventory`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                item_name: itemName,
                item_type: itemType,
                quantity: quantity,
                equipped: equipped ? 1 : 0,
                item_data: itemData
            })
        });

        const data = await response.json();
        if (data.success) {
            showToast('Item added successfully', 'success');
            await loadPlayerInventory(playerId);
            closeAllModals();
        } else {
            showToast(data.error || 'Error adding item', 'error');
        }
    } catch (error) {
        console.error('Error adding item:', error);
        showToast('Error adding item', 'error');
    }
}

async function editInventoryItem(itemId, currentEquipped, currentQuantity) {
    const newQuantity = prompt(`Enter new quantity for item:`, currentQuantity);
    if (newQuantity === null) return;

    const quantity = parseInt(newQuantity);
    if (isNaN(quantity) || quantity < 0) {
        showToast('Invalid quantity', 'error');
        return;
    }

    const equipped = confirm('Is this item equipped?');
    const playerId = parseInt(document.getElementById('edit-player-id').value);

    try {
        const response = await fetch(`${API_BASE}/player/${playerId}/inventory/${itemId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                quantity: quantity,
                equipped: equipped ? 1 : 0
            })
        });

        const data = await response.json();
        if (data.success) {
            showToast('Item updated successfully', 'success');
            await loadPlayerInventory(playerId);
        } else {
            showToast(data.error || 'Error updating item', 'error');
        }
    } catch (error) {
        console.error('Error updating item:', error);
        showToast('Error updating item', 'error');
    }
}

async function deleteInventoryItem(itemId) {
    if (!confirm('Are you sure you want to delete this item?')) {
        return;
    }

    const playerId = parseInt(document.getElementById('edit-player-id').value);

    try {
        const response = await fetch(`${API_BASE}/player/${playerId}/inventory/${itemId}`, {
            method: 'DELETE'
        });

        const data = await response.json();
        if (data.success) {
            showToast('Item deleted successfully', 'success');
            await loadPlayerInventory(playerId);
        } else {
            showToast(data.error || 'Error deleting item', 'error');
        }
    } catch (error) {
        console.error('Error deleting item:', error);
        showToast('Error deleting item', 'error');
    }
}

// ============================================================================
// Simulation Control
// ============================================================================

async function clearEvents() {
    if (!confirm('Are you sure you want to clear all events? This cannot be undone.')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/events/clear`, {
            method: 'POST'
        });

        const data = await response.json();
        if (data.success) {
            showToast(data.message, 'success');
            await loadWorldData();
            updateDashboard();
        } else {
            showToast('Error clearing events', 'error');
        }
    } catch (error) {
        console.error('Error clearing events:', error);
        showToast('Error clearing events', 'error');
    }
}

// ============================================================================
// Items Management
// ============================================================================

function renderItemsTable() {
    const tbody = document.getElementById('items-table-body');
    const countDisplay = document.getElementById('item-count-display');

    if (!state.filteredItems || state.filteredItems.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10" class="loading">No items found</td></tr>';
        countDisplay.textContent = '0 items';
        return;
    }

    countDisplay.textContent = `${state.filteredItems.length} item${state.filteredItems.length !== 1 ? 's' : ''}`;

    let html = '';
    state.filteredItems.forEach(item => {
        const data = item.data || {};
        const quality = data.quality || 'common';
        const rarity = data.rarity || 'common';
        const value = data.value || 0;
        const equipped = item.equipped ? 'Yes' : 'No';
        const owner = item.player_name || 'Unknown';

        html += `
            <tr>
                <td>${item.id}</td>
                <td><strong>${escapeHtml(item.item_name)}</strong></td>
                <td>${escapeHtml(item.item_type)}</td>
                <td>${escapeHtml(owner)}</td>
                <td>${item.quantity}</td>
                <td><span class="quality-badge quality-${quality}">${escapeHtml(quality)}</span></td>
                <td><span class="rarity-badge rarity-${rarity}">${escapeHtml(rarity)}</span></td>
                <td>${value} gold</td>
                <td>${equipped}</td>
                <td>
                    <button class="btn btn-danger btn-sm" onclick="deleteItemConfirm(${item.id})">🗑️ Delete</button>
                </td>
            </tr>
        `;
    });

    tbody.innerHTML = html;
}

function filterItems(query) {
    const lowerQuery = query.toLowerCase();
    state.filteredItems = state.items.filter(item =>
        item.item_name.toLowerCase().includes(lowerQuery) ||
        item.item_type.toLowerCase().includes(lowerQuery) ||
        (item.player_name && item.player_name.toLowerCase().includes(lowerQuery)) ||
        (item.data && JSON.stringify(item.data).toLowerCase().includes(lowerQuery))
    );
    renderItemsTable();
}

async function deleteItemConfirm(itemId) {
    const item = state.items.find(i => i.id === itemId);
    if (!item) return;

    if (!confirm(`Are you sure you want to delete "${item.item_name}"?`)) {
        return;
    }

    await deleteItemFromDB(itemId);
}

async function deleteItemFromDB(itemId) {
    try {
        const response = await fetch(`${API_BASE}/items/${itemId}`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (response.ok && result.success) {
            showToast('Item deleted successfully', 'success');
            await loadItems();
        } else {
            showToast(result.error || 'Failed to delete item', 'error');
        }
    } catch (error) {
        console.error('Error deleting item:', error);
        showToast('Error deleting item', 'error');
    }
}

// ============================================================================
// Item Generation
// ============================================================================

async function generateItems() {
    const template = document.getElementById('item-template').value;
    const count = parseInt(document.getElementById('item-count').value);
    const minQuality = document.getElementById('min-quality').value;
    const minRarity = document.getElementById('min-rarity').value;
    const minValue = document.getElementById('min-value').value;

    // Build constraints object
    const constraints = {};
    if (minQuality) constraints.min_quality = minQuality;
    if (minRarity) constraints.min_rarity = minRarity;
    if (minValue) constraints.min_value = parseInt(minValue);

    try {
        const response = await fetch(`${API_BASE}/items/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ template, count, constraints })
        });

        const result = await response.json();

        if (response.ok && result.success) {
            displayGeneratedItems(result.items);
            showToast(`Successfully generated ${result.count} item(s)`, 'success');
        } else {
            showToast(result.error || 'Failed to generate items', 'error');
        }
    } catch (error) {
        console.error('Error generating items:', error);
        showToast('Error generating items', 'error');
    }
}

function displayGeneratedItems(items) {
    const container = document.getElementById('generated-items-container');

    if (!items || items.length === 0) {
        container.innerHTML = '<p class="help-text">No items generated.</p>';
        return;
    }

    let html = '<div class="generated-items-grid">';

    items.forEach((item, index) => {
        // Get rarity color class
        const rarityClass = item.rarity ? `rarity-${item.rarity.toLowerCase()}` : 'rarity-common';

        // Format stats
        const stats = item.stats || {};
        const statsHtml = Object.entries(stats)
            .map(([key, value]) => `<span class="stat-badge">${key}: +${value}</span>`)
            .join(' ');

        // Format properties
        const damage = item.stats?.damage ? `<div class="item-stat">Damage: ${item.stats.damage}</div>` : '';
        const defense = item.stats?.defense ? `<div class="item-stat">Defense: ${item.stats.defense}</div>` : '';

        html += `
            <div class="item-card ${rarityClass}">
                <div class="item-header">
                    <h4>${escapeHtml(item.name)}</h4>
                    <span class="item-rarity">${escapeHtml(item.rarity || 'common')}</span>
                </div>
                <div class="item-body">
                    <div class="item-type">${escapeHtml(item.type)} ${item.subtype ? '- ' + escapeHtml(item.subtype) : ''}</div>
                    <div class="item-quality">Quality: ${escapeHtml(item.quality || 'common')}</div>
                    ${item.material ? `<div class="item-material">Material: ${escapeHtml(item.material)}</div>` : ''}
                    ${damage}
                    ${defense}
                    ${statsHtml ? `<div class="item-stats">${statsHtml}</div>` : ''}
                    <div class="item-value">Value: ${item.value || 0} gold</div>
                    ${item.description ? `<div class="item-description">${escapeHtml(item.description)}</div>` : ''}
                </div>
            </div>
        `;
    });

    html += '</div>';
    container.innerHTML = html;
}

// ============================================================================
// Utility Functions
// ============================================================================

function showModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.add('active');
}

function closeAllModals() {
    document.querySelectorAll('.modal').forEach(modal => {
        modal.classList.remove('active');
    });
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast show ${type}`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

function formatNumber(num, decimals = 0) {
    return parseFloat(num).toFixed(decimals);
}

function getLocationName(locationId) {
    const location = state.locations.find(l => l.id === locationId);
    return location ? location.name : 'Unknown';
}
