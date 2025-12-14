import socket
import threading
import pickle
import time
from random import randint

# Server configuration
HOST = '0.0.0.0'
PORT = 5555

# Game state
players = {}
rice_tiles = []
player_id_counter = 0
lock = threading.Lock()

# Initialize rice tiles (shared across all players)
def init_rice_tiles():
    tiles = []
    for i2 in range(3):
        for i in range(31):
            tiles.append({
                'id': f'{i2}-{i}',
                'x': 16 + i * 20,
                'y': 64 + i2 * 120,
                'harvested': False,
                'timer': 0,
                'growth_time': randint(65, 300)
            })
    return tiles

rice_tiles = init_rice_tiles()

def update_rice_tiles():
    """Update rice growth timers"""
    global rice_tiles
    with lock:
        for tile in rice_tiles:
            if tile['harvested']:
                tile['timer'] += 1
                if tile['timer'] >= tile['growth_time']:
                    tile['harvested'] = False
                    tile['timer'] = 0

def handle_client(conn, addr, player_id):
    global players, rice_tiles
    
    print(f"[NEW CONNECTION] {addr} connected as Player {player_id}")
    
    # Send player their ID
    try:
        conn.send(pickle.dumps({'type': 'id', 'id': player_id}))
    except:
        print(f"[ERROR] Failed to send ID to {addr}")
        conn.close()
        return
    
    # Wait for player to send their name
    try:
        data = conn.recv(4096)
        msg = pickle.loads(data)
        if msg['type'] == 'set_name':
            player_name = msg['name']
        else:
            player_name = f'Player {player_id}'
    except:
        player_name = f'Player {player_id}'
    
    # Initialize player with their chosen name
    with lock:
        players[player_id] = {
            'x': 320,
            'y': 420,
            'direction': 'down',
            'score': 0,
            'money': 0,
            'name': player_name,
            'wing': False,
            'winner_name': None
        }
    
    print(f"[PLAYER NAME] Player {player_id} is named '{player_name}'")
    
    connected = True
    while connected:
        try:
            # Receive data from client
            data = conn.recv(4096)
            if not data:
                break
            
            msg = pickle.loads(data)
            
            if msg['type'] == 'update':
                # Update player data
                with lock:
                    if player_id in players:
                        players[player_id].update(msg['data'])
            
            elif msg['type'] == 'harvest':
                # Handle rice harvesting
                tile_id = msg['tile_id']
                with lock:
                    for tile in rice_tiles:
                        if tile['id'] == tile_id and not tile['harvested']:
                            tile['harvested'] = True
                            tile['timer'] = 0
                            players[player_id]['score'] += 1
                            break
            
            elif msg['type'] == 'sell':
                # Handle selling at store
                with lock:
                    if players[player_id]['score'] > 0:
                        players[player_id]['money'] += players[player_id]['score'] * 3
                        players[player_id]['score'] = 0
            
            elif msg['type'] == 'buy_ticket':
                # Handle ticket purchase
                with lock:
                    if players[player_id]['money'] >= 1000:
                        players[player_id]['wing'] = True
                        # Broadcast winner to all players
                        winner_name = players[player_id]['name']
                        for pid in players:
                            players[pid]['winner_name'] = winner_name
                        print(f"[WINNER] {winner_name} has won the game!")
            
            # Send game state to client
            with lock:
                game_state = {
                    'players': players.copy(),
                    'rice': rice_tiles.copy()
                }
            
            conn.send(pickle.dumps(game_state))
            
        except Exception as e:
            print(f"[ERROR] {addr}: {e}")
            break
    
    # Client disconnected
    with lock:
        if player_id in players:
            del players[player_id]
    
    conn.close()
    print(f"[DISCONNECTED] Player {player_id} ({addr}) disconnected")

def rice_update_loop():
    """Background thread to update rice growth"""
    while True:
        update_rice_tiles()
        time.sleep(1/30)  # 30 FPS

def main():
    global player_id_counter
    
    # Let server owner choose IP to bind to
    print("=" * 50)
    print("RICE FARMING SERVER")
    print("=" * 50)
    print("\nBind options:")
    print("  1. 0.0.0.0 (All interfaces - recommended)")
    print("  2. 127.0.0.1 (Localhost only)")
    print("  3. Custom IP address")
    
    choice = input("\nEnter choice (1-3) [default: 1]: ").strip()
    
    if choice == "2":
        host = "127.0.0.1"
    elif choice == "3":
        host = input("Enter IP address to bind to: ").strip()
    else:
        host = HOST  # Default to 0.0.0.0
    
    port_input = input(f"Enter port [default: {PORT}]: ").strip()
    port = int(port_input) if port_input else PORT
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((host, port))
        server.listen()
    except Exception as e:
        print(f"[ERROR] Failed to bind to {host}:{port} - {e}")
        return
    
    print(f"\n[STARTING] Server is running on {host}:{port}")
    print(f"[INFO] Players should connect to this IP in their client")
    
    # Start rice update thread
    rice_thread = threading.Thread(target=rice_update_loop, daemon=True)
    rice_thread.start()
    
    print("[LISTENING] Server is listening for connections\n")
    
    while True:
        conn, addr = server.accept()
        player_id = player_id_counter
        player_id_counter += 1
        
        thread = threading.Thread(target=handle_client, args=(conn, addr, player_id))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}")

if __name__ == "__main__":
    main()