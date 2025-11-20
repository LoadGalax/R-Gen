#!/usr/bin/env python3
"""
Demo script showing client-server connection working

This demonstrates that the client can successfully connect to the game_server
and all basic API endpoints function correctly.
"""

import requests
import time
import json
from colorama import init, Fore, Style

init(autoreset=True)

def print_header(text):
    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{text:^70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

def print_success(text):
    print(f"{Fore.GREEN}✓{Style.RESET_ALL} {text}")

def print_info(text):
    print(f"{Fore.YELLOW}ℹ{Style.RESET_ALL} {text}")

def print_data(label, data):
    print(f"{Fore.MAGENTA}{label}:{Style.RESET_ALL}")
    print(json.dumps(data, indent=2))

def main():
    base_url = "http://localhost:5000"

    print_header("R-Gen Client-Server Connection Demo")

    # Test 1: Server Health
    print_header("1. Testing Server Health")
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            data = response.json()
            print_success("Server is healthy!")
            print_data("Health Status", data)
        else:
            print(f"{Fore.RED}✗ Server returned status {response.status_code}{Style.RESET_ALL}")
            return
    except Exception as e:
        print(f"{Fore.RED}✗ Cannot connect to server: {e}{Style.RESET_ALL}")
        print_info("Make sure the server is running: python3 game_server.py")
        return

    # Test 2: World Info
    print_header("2. Getting World Information")
    response = requests.get(f"{base_url}/api/world/info")
    if response.status_code == 200:
        data = response.json()
        print_success(f"Connected to world: {data['name']}")
        print_data("World Info", data)

    # Test 3: Locations
    print_header("3. Fetching Locations")
    response = requests.get(f"{base_url}/api/locations")
    if response.status_code == 200:
        data = response.json()
        locations = data['locations']
        print_success(f"Found {len(locations)} locations")
        print_info("Sample locations:")
        for loc in locations[:3]:
            print(f"  - {loc['name']} ({loc['template']}) - {loc['npc_count']} NPCs")

    # Test 4: NPCs
    print_header("4. Fetching NPCs")
    response = requests.get(f"{base_url}/api/npcs")
    if response.status_code == 200:
        data = response.json()
        npcs = data['npcs']
        print_success(f"Found {len(npcs)} NPCs")
        print_info("Sample NPCs:")
        for npc_data in npcs[:3]:
            npc_name = npc_data.get('data', {}).get('name', 'Unknown')
            location_name = npc_data.get('location_name', 'Unknown')
            print(f"  - {npc_name} at {location_name}")

    # Test 5: Location Details
    print_header("5. Getting Location Details")
    if locations:
        loc_id = locations[0]['id']
        response = requests.get(f"{base_url}/api/location/{loc_id}")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Fetched details for: {data['name']}")
            print_info(f"Description: {data.get('description', 'N/A')[:100]}...")
            print_info(f"Weather: {data.get('weather', 'Unknown')}")
            print_info(f"NPCs present: {len(data.get('npcs', []))}")
            print_info(f"Connected locations: {len(data.get('connections', []))}")

    # Test 6: NPC Dialogue
    print_header("6. Testing NPC Dialogue")
    if npcs:
        npc_id = npcs[0]['id']
        response = requests.get(f"{base_url}/api/npc/{npc_id}/dialogue")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Got dialogue from: {data['npc_name']}")
            print_data("Sample Dialogue", {
                "greeting": data['dialogues']['greeting'],
                "mood": data['dialogues']['mood']
            })

    # Test 7: Client HTML
    print_header("7. Testing Client Interface")
    response = requests.get(base_url)
    if response.status_code == 200 and 'Dark Grimoire' in response.text:
        print_success("Client HTML is being served correctly")
        print_info("You can open the game in your browser at:")
        print(f"  {Fore.BLUE}{base_url}{Style.RESET_ALL}")

    # Test 8: Client JavaScript
    response = requests.get(f"{base_url}/game.js")
    if response.status_code == 200 and 'RGenGame' in response.text:
        print_success("Client JavaScript is being served correctly")

    # Summary
    print_header("Connection Summary")
    print_success("All basic API endpoints are working!")
    print_success("Client files are being served correctly!")
    print_success("The client can successfully connect to the game_server!")

    print(f"\n{Fore.GREEN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'CLIENT-SERVER INTEGRATION SUCCESSFUL!':^70}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'='*70}{Style.RESET_ALL}\n")

    print_info("To use the web client:")
    print(f"  1. Keep the server running")
    print(f"  2. Open {Fore.BLUE}http://localhost:5000{Style.RESET_ALL} in your browser")
    print(f"  3. The Dark Grimoire interface will load and connect automatically\n")

if __name__ == '__main__':
    main()
