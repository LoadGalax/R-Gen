/**
 * R-Gen Client Configuration
 * All configurable values for the game client
 */

const CONFIG = {
    // API Configuration
    api: {
        eventsLimit: 20,  // Number of events to fetch from API
    },

    // UI Configuration
    ui: {
        notificationDuration: 3000,  // Notification display duration in milliseconds
        maxEventsInMemory: 50,       // Maximum events to keep in memory
    },

    // Item Rarity Configuration
    itemRarity: {
        colors: {
            'Legendary': '#ffd700',
            'Rare': '#6495ed',
            'Uncommon': '#32cd32',
            'Common': '#b8a485'
        }
    },

    // Profession Configuration
    profession: {
        xpPerLevel: 100,  // XP required per level (multiplied by level)
        rarityThresholds: {
            legendary: 8,   // Level threshold for legendary rarity
            rare: 6,        // Level threshold for rare rarity
            uncommon: 3     // Level threshold for uncommon rarity
        }
    },

    // Recipe Configuration
    recipe: {
        rarityThresholds: {
            rare: 7,        // Required level threshold for rare recipes
            uncommon: 4     // Required level threshold for uncommon recipes
        }
    },

    // External Dependencies (reference only - update index.html script tags to change)
    external: {
        socketIoUrl: 'https://cdn.socket.io/4.5.4/socket.io.min.js',
        socketIoVersion: '4.5.4'
    }
};

// Freeze the config to prevent modifications
Object.freeze(CONFIG);
