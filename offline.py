#билетик за 1000 баксов

import pygame
import os
from random import randint

pygame.init()

WIDTH, HEIGHT = 640, 640
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("china")

FPS = 30
clock = pygame.time.Clock()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SPRITE_PATH = os.path.join(BASE_DIR, "pl")

score = 0
money = 0

font1 = pygame.font.SysFont("TempleOs", 16)

rice0 = pygame.image.load(os.path.join(BASE_DIR, "tiles.png")).convert_alpha()
rice1 = pygame.image.load(os.path.join(BASE_DIR, "tiles1.png")).convert_alpha()

agartha = pygame.image.load(os.path.join(BASE_DIR, "ticket.png")).convert_alpha()
win1 = pygame.image.load(os.path.join(BASE_DIR, "win.png")).convert_alpha()

harvest_sound = pygame.mixer.Sound(os.path.join(SPRITE_PATH, "harvest.wav"))
sell_sound = pygame.mixer.Sound(os.path.join(SPRITE_PATH, "sell.wav"))
grow_sound = pygame.mixer.Sound(os.path.join(SPRITE_PATH, "grow.wav"))
final_sound = pygame.mixer.Sound(os.path.join(SPRITE_PATH, "winmua.wav"))

harvest_sound.set_volume(1)
sell_sound.set_volume(0.3)
grow_sound.set_volume(0.7)
final_sound.set_volume(1.5)

storepath = pygame.image.load(os.path.join(BASE_DIR, "store.png")).convert_alpha()

img_up = pygame.image.load(os.path.join(SPRITE_PATH, "u.png")).convert_alpha()
img_down = pygame.image.load(os.path.join(SPRITE_PATH, "d.png")).convert_alpha()
img_left = pygame.image.load(os.path.join(SPRITE_PATH, "l.png")).convert_alpha()
img_right = pygame.image.load(os.path.join(SPRITE_PATH, "r.png")).convert_alpha()

black_rect = pygame.Rect(0, 0, 20, 20)

wing = False

class Block:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.rect = img.get_rect(topleft=(x, y))

    def draw(self, scr):
        scr.blit(self.img, (self.x, self.y))
        
class Rice:
    def __init__(self, block: Block, img_grown, img_cropped, growth_time):
        self.block = block
        self.img_grown = img_grown
        self.img_cropped = img_cropped
        self.growth_time = growth_time

        self.harvested = False
        self.timer = 0

        self.block.img = self.img_grown
    def main(self, hit):
        global score

        # harvest
        if not self.harvested and self.block.rect.colliderect(hit):
            self.block.img = self.img_cropped
            self.harvested = True
            self.timer = 0
            score += 1
            harvest_sound.play()
            return

        if self.harvested:
            self.timer += 1
            if self.timer >= self.growth_time:
                self.harvested = False
                self.block.img = self.img_grown
                self.timer = 0
                grow_sound.play()
    
class Store:
    def __init__(self, block: Block):
        self.block = block
    def main(self, hit):
        global score, money
        if self.block.rect.colliderect(hit) and score > 0:
            money = money + score * 3
            score = 0
            sell_sound.play()
            
class Ticket:
    def __init__(self, block:Block):
        self.block = block
    def main(self,hit):
        global wing
        if self.block.rect.colliderect(hit) and money >= 1000:
            wing = True
            
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 4
        
        self.img_up = pygame.image.load(os.path.join(SPRITE_PATH, "u.png")).convert_alpha()
        self.img_down = pygame.image.load(os.path.join(SPRITE_PATH, "d.png")).convert_alpha()
        self.img_left = pygame.image.load(os.path.join(SPRITE_PATH, "l.png")).convert_alpha()
        self.img_right = pygame.image.load(os.path.join(SPRITE_PATH, "r.png")).convert_alpha()

        self.image = self.img_down
        self.rect = self.image.get_rect(topleft=(self.x, self.y))  
        
    def update(self, keys):
        dx = 0
        dy = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
            self.image = self.img_up
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1
            self.image = self.img_down
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
            self.image = self.img_left
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1
            self.image = self.img_right
        
        #if keys[pygame.K_e]:
        #for tile in ricel:
        #if test_tile.rect.colliderect(player.rect):
        #    print("cropped")
        
        if dx != 0 or dy != 0:
            length = (dx * dx + dy * dy) ** 0.5
            dx /= length
            dy /= length

        self.x += dx * self.speed
        self.y += dy * self.speed

    def draw(self, scr):
        scr.blit(self.image, (self.x, self.y))


player = Player(320, 420)
storeblock = Block(320-24, 500, storepath)
tikblock = Block(550, 400, agartha)
store = Store(storeblock)
tickett = Ticket(tikblock)
ricel = []

killyou = False
for i2 in range(3):
    for i in range(31):
        block = Block(16 + i*20, 64 + i2*120, rice0)
        rice = Rice(block, rice0, rice1, randint(100, 3000))
        ricel.append(rice)
run = True
while run:

    if wing:
        win.blit(pygame.transform.scale(win1, (WIDTH, HEIGHT)), (0, 0))
        pygame.display.update()
        continue
    clock.tick(FPS)
    
    if money >= 750 and not killyou:
        final_sound.play()
        killyou = True
    scoretxt = font1.render(str(score), 2, (255,255,255))
    ricetxt = font1.render("rice",2,(255,255,255))
    
    moneytxt = font1.render(f"{money}$", 2, (255,255,255))
    
    moved = black_rect.move(player.x-2, player.y-2)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    keys = pygame.key.get_pressed()
    player.update(keys)
    store.main(moved)
    tickett.main(moved)
    win.fill((0, 0, 0))
    
    win.blit(scoretxt, (600,600))
    win.blit(ricetxt, (570,620))
    win.blit(moneytxt, (30, 600))
    for rice in ricel:
        rice.main(moved)
        rice.block.draw(win)
    store.block.draw(win)
    tickett.block.draw(win)
    pygame.draw.rect(win, (0,0,0), moved)
    player.draw(win)
    
    pygame.display.update()

pygame.quit()
