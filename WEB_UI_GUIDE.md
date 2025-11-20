# R-Gen Web UI Access Guide

## Starting the Game Server

To start the R-Gen web game server, run:

```bash
python3 game_server.py
```

The game will be available at: **http://localhost:5000**

## Accessing the Web UI

1. Open your web browser
2. Navigate to `http://localhost:5000`
3. You should see the **Dark Grimoire** themed login screen

## First Time Access

When you first access the game, you'll see a login/registration modal:

### Creating a New Account
1. Click "Register here" on the login screen
2. Fill in:
   - Username
   - Password
   - Character Name
   - Race (Human, Elf, Dwarf, Halfling, Orc)
   - Class (Warrior, Mage, Rogue, Cleric, Ranger, Bard)
3. Click "⚔️ Create Hero"
4. You'll be automatically logged in

### Logging In
1. Enter your username and password
2. Click "🗝️ Enter Realm"

## Troubleshooting

### "The web UI does not have login or is not working"

If you're experiencing issues with the login not showing or JavaScript errors:

**1. Clear Browser Cache (Hard Refresh)**
   - **Chrome/Edge**: Press `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
   - **Firefox**: Press `Ctrl+F5` (Windows/Linux) or `Cmd+Shift+R` (Mac)
   - **Safari**: Press `Cmd+Option+R`

**2. Clear All Browser Data**
   - Chrome: Settings → Privacy and security → Clear browsing data
   - Firefox: Settings → Privacy & Security → Cookies and Site Data → Clear Data
   - Make sure to select "Cached images and files"

**3. Try Incognito/Private Mode**
   - This ensures no cached files are being used
   - Chrome: `Ctrl+Shift+N`
   - Firefox: `Ctrl+Shift+P`

**4. Check Developer Console**
   - Press `F12` to open browser developer tools
   - Check the "Console" tab for any JavaScript errors
   - If you see errors related to old code, clear cache and refresh

### JavaScript Syntax Error at line 1537

This error was fixed in commit `d12612f`. If you still see this error:

1. The issue is your browser is loading an **old cached version** of `game.js`
2. Follow the "Clear Browser Cache" steps above
3. The current version includes cache-busting (`game.js?v=20251120-2`) and cache control headers
4. After clearing cache and refreshing, you should see the login modal

### Server Not Starting

If you get a "ModuleNotFoundError" for Flask:

```bash
pip3 install flask flask-cors flask-socketio werkzeug
```

Then restart the server:
```bash
python3 game_server.py
```

## Features

Once logged in, you can:
- Explore the world through the **Dark Grimoire** interface
- View your character stats and inventory
- Interact with NPCs
- Craft items using various professions
- Navigate between locations
- Track quests and events

## Cache Control

The server is configured to prevent browser caching of JavaScript files during development:
- Cache-Control headers are set on all responses
- JavaScript files include version parameters (`?v=timestamp`)
- Meta tags prevent HTML caching

If you're still seeing old code after following the troubleshooting steps, please report the issue with:
- Browser name and version
- Any console errors (press F12 → Console tab)
- Steps you've already tried

## Server Info

- **Port**: 5000
- **Host**: localhost (0.0.0.0)
- **WebSocket**: Enabled for real-time updates
- **Database**: SQLite (game.db)

## Support

For issues or questions:
1. Check this guide first
2. Look at the browser console for errors (F12 → Console)
3. Try the troubleshooting steps above
4. Check the GitHub issues page
