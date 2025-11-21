const express = require('express');
const fs = require('fs').promises;
const path = require('path');
const app = express();

const PORT = 3000;
const DATA_DIR = path.join(__dirname, 'GenerationEngine', 'data');

// Middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.static(__dirname));

// CORS headers
app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
    res.header('Access-Control-Allow-Headers', 'Content-Type');
    next();
});

// Read JSON file
app.get('/api/read/:filename', async (req, res) => {
    try {
        const filename = req.params.filename;

        // Security: prevent directory traversal
        if (filename.includes('..') || filename.includes('/')) {
            return res.status(400).json({ error: 'Invalid filename' });
        }

        const filePath = path.join(DATA_DIR, filename);
        const content = await fs.readFile(filePath, 'utf8');
        const data = JSON.parse(content);

        res.json(data);
    } catch (error) {
        console.error('Error reading file:', error);
        res.status(500).json({ error: error.message });
    }
});

// Save JSON file
app.post('/api/save/:filename', async (req, res) => {
    try {
        const filename = req.params.filename;
        const { content } = req.body;

        // Security: prevent directory traversal
        if (filename.includes('..') || filename.includes('/')) {
            return res.status(400).json({ error: 'Invalid filename' });
        }

        // Validate JSON
        const data = JSON.parse(content);

        const filePath = path.join(DATA_DIR, filename);

        // Create backup before saving
        const backupDir = path.join(__dirname, 'backups');
        try {
            await fs.mkdir(backupDir, { recursive: true });
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const backupPath = path.join(backupDir, `${filename}.${timestamp}.backup`);

            // Copy current file to backup
            try {
                const currentContent = await fs.readFile(filePath, 'utf8');
                await fs.writeFile(backupPath, currentContent);
            } catch (e) {
                // File might not exist yet, that's ok
            }
        } catch (backupError) {
            console.warn('Warning: Could not create backup:', backupError.message);
        }

        // Write the formatted JSON
        await fs.writeFile(filePath, JSON.stringify(data, null, 2), 'utf8');

        res.json({ success: true, message: 'File saved successfully' });
    } catch (error) {
        console.error('Error saving file:', error);
        res.status(500).json({ error: error.message });
    }
});

// List all JSON files
app.get('/api/files', async (req, res) => {
    try {
        const files = await fs.readdir(DATA_DIR);
        const jsonFiles = files.filter(f => f.endsWith('.json'));
        res.json(jsonFiles);
    } catch (error) {
        console.error('Error listing files:', error);
        res.status(500).json({ error: error.message });
    }
});

// Get file info
app.get('/api/info/:filename', async (req, res) => {
    try {
        const filename = req.params.filename;

        if (filename.includes('..') || filename.includes('/')) {
            return res.status(400).json({ error: 'Invalid filename' });
        }

        const filePath = path.join(DATA_DIR, filename);
        const stats = await fs.stat(filePath);
        const content = await fs.readFile(filePath, 'utf8');
        const data = JSON.parse(content);

        res.json({
            size: stats.size,
            modified: stats.mtime,
            lines: content.split('\n').length,
            keys: Object.keys(data).length
        });
    } catch (error) {
        console.error('Error getting file info:', error);
        res.status(500).json({ error: error.message });
    }
});

// Health check
app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', dataDir: DATA_DIR });
});

// Start server
app.listen(PORT, () => {
    console.log(`
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🎮  GenerationEngine JSON Editor Server                ║
║                                                           ║
║   Server running on: http://localhost:${PORT}              ║
║   Data directory: ${DATA_DIR.padEnd(37)}║
║                                                           ║
║   Open http://localhost:${PORT}/json-editor.html           ║
║                                                           ║
║   Press Ctrl+C to stop the server                        ║
║                                                           ║
╔═══════════════════════════════════════════════════════════╗
    `);
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n\nShutting down server...');
    process.exit(0);
});
