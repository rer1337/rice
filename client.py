import pygame
import os
import socket
import pickle
import threading

# Server configuration
SERVER = '127.0.0.1'  # Change to server IP if not localhost
PORT = 5555

pygame.init()

WIDTH, HEIGHT = 640, 640
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("China Online")

FPS = 30
clock = pygame.time.Clock()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SPRITE_PATH = os.path.join(BASE_DIR, "pl")

# Try to load images, use placeholders if not found
try:
    rice0 = pygame.image.load(os.path.join(BASE_DIR, "tiles.png")).convert_alpha()
    rice1 = pygame.image.load(os.path.join(BASE_DIR, "tiles1.png")).convert_alpha()
except:
    # Create placeholder surfaces
    rice0 = pygame.Surface((20, 20))
    rice0.fill((107, 142, 35))
    rice1 = pygame.Surface((20, 20))
    rice1.fill((74, 53, 32))

try:
    agartha = pygame.image.load(os.path.join(BASE_DIR, "ticket.png")).convert_alpha()
except:
    agartha = pygame.Surface((48, 48))
    agartha.fill((255, 215, 0))

try:
    win1 = pygame.image.load(os.path.join(BASE_DIR, "win.png")).convert_alpha()
except:
    win1 = pygame.Surface((WIDTH, HEIGHT))
    win1.fill((255, 215, 0))

try:
    storepath = pygame.image.load(os.path.join(BASE_DIR, "store.png")).convert_alpha()
except:
    storepath = pygame.Surface((48, 32))
    storepath.fill((139, 69, 19))

# Load player sprites
try:
    img_up = pygame.image.load(os.path.join(SPRITE_PATH, "u.png")).convert_alpha()
    img_down = pygame.image.load(os.path.join(SPRITE_PATH, "d.png")).convert_alpha()
    img_left = pygame.image.load(os.path.join(SPRITE_PATH, "l.png")).convert_alpha()
    img_right = pygame.image.load(os.path.join(SPRITE_PATH, "r.png")).convert_alpha()
except:
    # Create placeholder player sprites
    img_up = pygame.Surface((24, 24))
    img_up.fill((255, 68, 68))
    img_down = img_up.copy()
    img_left = img_up.copy()
    img_right = img_up.copy()

# Sounds
try:
    harvest_sound = pygame.mixer.Sound(os.path.join(SPRITE_PATH, "harvest.wav"))
    sell_sound = pygame.mixer.Sound(os.path.join(SPRITE_PATH, "sell.wav"))
    grow_sound = pygame.mixer.Sound(os.path.join(SPRITE_PATH, "grow.wav"))
    final_sound = pygame.mixer.Sound(os.path.join(SPRITE_PATH, "winmua.wav"))
    harvest_sound.set_volume(1)
    sell_sound.set_volume(0.3)
    grow_sound.set_volume(0.7)
    final_sound.set_volume(1.5)
except:
    harvest_sound = None
    sell_sound = None
    grow_sound = None
    final_sound = None

font1 = pygame.font.SysFont("Arial", 16)

# Network variables
player_id = None
game_state = {'players': {}, 'rice': []}
game_state_lock = threading.Lock()

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = SERVER
        self.port = PORT
        self.addr = (self.server, self.port)
        self.connected = False
        
    def connect(self):
        try:
            self.client.connect(self.addr)
            self.connected = True
            # Receive player ID
            data = self.client.recv(4096)
            msg = pickle.loads(data)
            return msg['id']
        except Exception as e:
            print(f"Connection error: {e}")
            return None
    
    def send_name(self, name):
        """Send player name to server"""
        try:
            self.client.send(pickle.dumps({'type': 'set_name', 'name': name}))
        except Exception as e:
            print(f"Error sending name: {e}")
    
    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            response = self.client.recv(4096)
            return pickle.loads(response)
        except Exception as e:
            print(f"Send error: {e}")
            return None

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 4
        self.direction = 'down'
        self.img_up = img_up
        self.img_down = img_down
        self.img_left = img_left
        self.img_right = img_right
        self.image = self.img_down
        self.rect = pygame.Rect(self.x, self.y, 24, 24)
        
    def update(self, keys):
        dx = 0
        dy = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
            self.image = self.img_up
            self.direction = 'up'
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1
            self.image = self.img_down
            self.direction = 'down'
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
            self.image = self.img_left
            self.direction = 'left'
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1
            self.image = self.img_right
            self.direction = 'right'
        
        if dx != 0 or dy != 0:
            length = (dx * dx + dy * dy) ** 0.5
            dx /= length
            dy /= length

        self.x += dx * self.speed
        self.y += dy * self.speed
        self.rect.topleft = (self.x, self.y)

    def draw(self, scr):
        scr.blit(self.image, (self.x, self.y))

def get_player_sprite(direction):
    """Get the appropriate sprite based on direction"""
    if direction == 'up':
        return img_up
    elif direction == 'down':
        return img_down
    elif direction == 'left':
        return img_left
    elif direction == 'right':
        return img_right
    return img_down

def main():
    global player_id, game_state, win
    
    # Create window for server IP input
    input_win = pygame.display.set_mode((500, 300))
    pygame.display.set_caption("Connect to Server")
    
    # Server IP input
    server_ip = "127.0.0.1"
    server_port = "5555"
    active_field = "ip"  # "ip" or "port"
    ip_entered = False
    input_font = pygame.font.SysFont("Arial", 24)
    title_font = pygame.font.SysFont("Arial", 32, bold=True)
    
    while not ip_entered:
        input_win.fill((30, 30, 30))
        
        # Draw title
        title = title_font.render("Connect to Server", True, (100, 200, 100))
        input_win.blit(title, (100, 30))
        
        # Draw server IP label and input box
        ip_label = input_font.render("Server IP:", True, (200, 200, 200))
        input_win.blit(ip_label, (30, 100))
        
        ip_box_color = (100, 150, 255) if active_field == "ip" else (255, 255, 255)
        pygame.draw.rect(input_win, ip_box_color, (30, 135, 440, 40), 2)
        ip_surface = input_font.render(server_ip, True, (255, 255, 255))
        input_win.blit(ip_surface, (40, 142))
        
        # Draw port label and input box
        port_label = input_font.render("Port:", True, (200, 200, 200))
        input_win.blit(port_label, (30, 190))
        
        port_box_color = (100, 150, 255) if active_field == "port" else (255, 255, 255)
        pygame.draw.rect(input_win, port_box_color, (30, 225, 440, 40), 2)
        port_surface = input_font.render(server_port, True, (255, 255, 255))
        input_win.blit(port_surface, (40, 232))
        
        # Draw instructions
        instruction = pygame.font.SysFont("Arial", 14).render("TAB to switch fields | ENTER to connect", True, (150, 150, 150))
        input_win.blit(instruction, (30, 275))
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and len(server_ip) > 0:
                    ip_entered = True
                elif event.key == pygame.K_TAB:
                    active_field = "port" if active_field == "ip" else "ip"
                elif event.key == pygame.K_BACKSPACE:
                    if active_field == "ip":
                        server_ip = server_ip[:-1]
                    else:
                        server_port = server_port[:-1]
                elif event.unicode.isprintable():
                    if active_field == "ip" and len(server_ip) < 30:
                        server_ip += event.unicode
                    elif active_field == "port" and len(server_port) < 5 and event.unicode.isdigit():
                        server_port += event.unicode
    
    # Now show name input screen
    input_win = pygame.display.set_mode((400, 200))
    pygame.display.set_caption("Enter Your Name")
    
    # Name input
    player_name = ""
    name_entered = False
    input_font = pygame.font.SysFont("Arial", 32)
    
    while not name_entered:
        input_win.fill((30, 30, 30))
        
        # Draw prompt
        prompt = input_font.render("Enter your name:", True, (255, 255, 255))
        input_win.blit(prompt, (20, 40))
        
        # Draw input box
        pygame.draw.rect(input_win, (255, 255, 255), (20, 90, 360, 50), 2)
        name_surface = input_font.render(player_name, True, (255, 255, 255))
        input_win.blit(name_surface, (30, 100))
        
        # Draw instruction
        instruction = pygame.font.SysFont("Arial", 16).render("Press ENTER to join", True, (150, 150, 150))
        input_win.blit(instruction, (20, 160))
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and len(player_name) > 0:
                    name_entered = True
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif len(player_name) < 15 and event.unicode.isprintable():
                    player_name += event.unicode
    
    # Resize window back to game size
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Rice Farming Online")
    
    # Connect to server with chosen IP and port
    network = Network()
    network.server = server_ip
    network.port = int(server_port) if server_port else 5555
    network.addr = (network.server, network.port)
    
    print(f"Connecting to {server_ip}:{server_port}...")
    player_id = network.connect()
    
    if player_id is None:
        print("Failed to connect to server")
        error_font = pygame.font.SysFont("Arial", 24)
        error_text = error_font.render(f"Failed to connect to {server_ip}:{server_port}", True, (255, 100, 100))
        win.fill((0, 0, 0))
        win.blit(error_text, (50, HEIGHT // 2))
        pygame.display.update()
        pygame.time.wait(3000)
        pygame.quit()
        return
    
    # Send player name to server
    network.send_name(player_name)
    
    print(f"Connected as Player {player_id} with name '{player_name}'")
    
    player = Player(320, 420)
    
    wing = False
    sound_played = False
    last_score = 0
    last_money = 0
    winner_name = None
    
    black_rect = pygame.Rect(0, 0, 20, 20)
    
    run = True
    while run:
        # Check if someone won
        if player_id in game_state.get('players', {}):
            winner_name = game_state['players'][player_id].get('winner_name', None)
        
        if winner_name:
            # Display winner screen
            win.blit(pygame.transform.scale(win1, (WIDTH, HEIGHT)), (0, 0))
            
            # Draw winner text
            winner_font = pygame.font.SysFont("Arial", 72, bold=True)
            winner_text = winner_font.render(f"{winner_name} WON!!!!", True, (255, 215, 0))
            text_rect = winner_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            
            # Draw black outline for better visibility
            outline_color = (0, 0, 0)
            for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
                outline = winner_font.render(f"{winner_name} WON!!!!", True, outline_color)
                win.blit(outline, (text_rect.x + dx, text_rect.y + dy))
            
            win.blit(winner_text, text_rect)
            pygame.display.update()
            continue
        
        if wing:
            win.blit(pygame.transform.scale(win1, (WIDTH, HEIGHT)), (0, 0))
            pygame.display.update()
            continue
            
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        player.update(keys)
        
        moved = black_rect.move(int(player.x - 2), int(player.y - 2))
        
        # Get current score and money before actions
        current_score = 0
        current_money = 0
        if player_id in game_state.get('players', {}):
            current_score = game_state['players'][player_id]['score']
            current_money = game_state['players'][player_id]['money']
        
        # Check for harvesting
        harvested_this_frame = False
        with game_state_lock:
            for tile in game_state.get('rice', []):
                tile_rect = pygame.Rect(tile['x'], tile['y'], 20, 20)
                if moved.colliderect(tile_rect) and not tile['harvested']:
                    response = network.send({'type': 'harvest', 'tile_id': tile['id']})
                    if response:
                        game_state = response
                        harvested_this_frame = True
                        if harvest_sound:
                            harvest_sound.play()
                    break  # Only harvest one tile per frame
        
        # Check store collision
        store_rect = pygame.Rect(320 - 24, 500, 48, 32)
        if moved.colliderect(store_rect):
            # Get updated score before selling
            if player_id in game_state.get('players', {}):
                current_score = game_state['players'][player_id]['score']
            
            if current_score > 0:
                response = network.send({'type': 'sell'})
                if response:
                    game_state = response
                    if sell_sound:
                        sell_sound.play()
        
        # Check ticket collision
        ticket_rect = pygame.Rect(550, 400, 48, 48)
        if moved.colliderect(ticket_rect):
            # Get updated money before buying
            if player_id in game_state.get('players', {}):
                current_money = game_state['players'][player_id]['money']
            
            if current_money >= 1000:
                response = network.send({'type': 'buy_ticket'})
                if response:
                    game_state = response
        
        # Regular update - send player position
        player_data = {
            'x': player.x,
            'y': player.y,
            'direction': player.direction
        }
        
        if not harvested_this_frame:  # Only send regular update if we didn't just harvest
            response = network.send({'type': 'update', 'data': player_data})
            if response:
                with game_state_lock:
                    game_state = response
        
        # Update local variables from server state
        if player_id in game_state.get('players', {}):
            my_data = game_state['players'][player_id]
            current_score = my_data['score']
            current_money = my_data['money']
            wing = my_data['wing']
        
        # Play final sound
        if current_money >= 750 and not sound_played and final_sound:
            final_sound.play()
            sound_played = True
        
        # Draw
        win.fill((0, 0, 0))
        
        # Draw rice tiles
        for tile in game_state.get('rice', []):
            if tile['harvested']:
                win.blit(rice1, (tile['x'], tile['y']))
            else:
                win.blit(rice0, (tile['x'], tile['y']))
        
        # Draw store
        win.blit(storepath, (320 - 24, 500))
        
        # Draw ticket
        win.blit(agartha, (550, 400))
        
        # Draw all players
        for pid, pdata in game_state.get('players', {}).items():
            px = pdata['x']
            py = pdata['y']
            direction = pdata.get('direction', 'down')
            
            # Get the sprite for this player's direction
            sprite = get_player_sprite(direction)
            win.blit(sprite, (px, py))
            
            # Draw name above player (centered)
            name = pdata.get('name', f'P{pid}')
            name_text = font1.render(name, True, (255, 255, 255))
            text_width = name_text.get_width()
            player_center = px + 12  # Player sprite is 24px wide
            text_x = player_center - text_width // 2
            win.blit(name_text, (text_x, py - 20))
        
        # Draw UI
        scoretxt = font1.render(str(current_score), True, (255, 255, 255))
        ricetxt = font1.render("rice", True, (255, 255, 255))
        moneytxt = font1.render(f"{current_money}$", True, (255, 255, 255))
        player_count = font1.render(f"Players: {len(game_state.get('players', {}))}", True, (255, 255, 255))
        
        win.blit(scoretxt, (600, 600))
        win.blit(ricetxt, (570, 620))
        win.blit(moneytxt, (30, 600))
        win.blit(player_count, (30, 30))
        
        pygame.display.update()
    
    pygame.quit()

if __name__ == "__main__":
    main()