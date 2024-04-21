import pygame
import sys
import random
import math
import csv

class Tile(pygame.sprite.Sprite):
    spawn_x = 0
    spawn_y = 0
    collison = False
    
    def __init__(self, image, x, y, collison):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.spawn_x = x
        self.spawn_y = y
        self.rect.x = x
        self.rect.y = y
        self.collison = collison
    
    def pos(self, x, y):
        self.rect.x = self.spawn_x - x
        self.rect.y = self.spawn_y - y
       
pygame.init()
pygame.font.init()
font = pygame.font.Font(None, 36)

WIDTH, HEIGHT = 800, 600
GAMEWORLD_WIDTH, GAMEWORLD_HEIGHT = 1000, 1000
SQUARE_SIZE = 16

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (25, 25, 25)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("blammo")

player_size = 32
player_x = WIDTH // 2
player_y = HEIGHT // 2
player_speed = 8

enemy_size = 16
enemy_speed = 3
enemies = []

score = 0
ammo = 3

ammo_spawned = False
ammo_x = 0
ammo_y = 0

tiles = pygame.sprite.Group()
GRASS = 1000
WATER = 1001
grass_image = pygame.image.load("grass.png")
water_image = pygame.image.load("water.png")

map = []
with open("map.csv", "r") as file:
    reader = csv.reader(file)
    for row in reader:
        # Assuming each row contains numeric data, convert them to integers or floats
        numeric_row = [int(value) for value in row]
        map.append(numeric_row)
        
for row_index, row in enumerate(map):
    for col_index, value in enumerate(row):
        collision = False
        if value == GRASS:
            image = grass_image
        elif value == WATER:
            image = water_image
            collision = True
        tile = Tile(image, col_index * SQUARE_SIZE, row_index * SQUARE_SIZE, collision)
        tiles.add(tile)
        
def spawn_enemy():
    side = random.randint(1, 4)
    if side == 1:
        x = random.randint(0, WIDTH - enemy_size)
        y = -enemy_size
    elif side == 2:
        x = WIDTH
        y = random.randint(0, HEIGHT - enemy_size)
    elif side == 3:
        x = random.randint(0, WIDTH - enemy_size)
        y = HEIGHT
    else:
        x = -enemy_size
        y = random.randint(0, HEIGHT - enemy_size)
    enemies.append([x, y, RED])

def spawn_ammo():
    global ammo_x, ammo_y
    ammo_x = random.randint(25, WIDTH - 25)
    ammo_y = random.randint(25, HEIGHT - 25)

def move_enemy(enemy):
    dx = player_x  - enemy[0]
    dy = player_y  - enemy[1]
    dist = math.sqrt(dx ** 2 + dy ** 2)
    if dist != 0:
        dx /= dist
        dy /= dist
    extra_speed = float(score + 1) * 0.01 + 1
    enemy[0] += dx * enemy_speed * extra_speed
    enemy[1] += dy * enemy_speed * extra_speed

def destroy_green_enemies():
    list = []
    for enemy in enemies:
        if enemy[2] == GREEN:
            list.append(enemy)
    
    if len(list) > 0:
        global ammo
        ammo -= 1
    
    for enemy in list:
        enemies.remove(enemy)
        global score
        score += 1

def reset_game():
    global player_x, player_y, enemies, score, ammo, ammo_x, ammo_y, ammo_spawned, tiles
    player_x = WIDTH // 2
    player_y = HEIGHT // 2
    enemies = []
    score = 0
    ammo = 3
    ammo_x = 0
    ammo_y = 0
    ammo_spawned = False

def check_col(x, y):
    rect = pygame.Rect(player_x - dummy_camera.x + x, player_y - dummy_camera.y + y, player_size, player_size)
    for tile in tiles:
        if tile.collison and pygame.Rect.colliderect(tile.rect, rect):
            return True
    return False
                
running = True
enemy_spawn_timer = 0
while running:
    pygame.time.Clock().tick(60)
    pygame.display.flip()
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_game()
            if event.key == pygame.K_SPACE and ammo > 0:
                destroy_green_enemies()

    keys = pygame.key.get_pressed()
    frame = screen.get_rect()
    camera = frame.copy()
    
    collide = False
    dummy_camera = frame.copy()
    dummy_camera.center = pygame.Rect(player_x - dummy_camera.x, player_y - dummy_camera.y, player_size, player_size).center
    dummy_player_rect = pygame.Rect(player_x - dummy_camera.x, player_y - dummy_camera.y, player_size, player_size)
    for tile in tiles:
        tile.pos(dummy_camera.x, dummy_camera.y)
    tiles.draw(screen) 
    if keys[pygame.K_w]:
        if not check_col(0, -player_speed):
            player_y -= player_speed
    if keys[pygame.K_s]:
        if not check_col(0, player_speed):
            player_y += player_speed
    if keys[pygame.K_a]:
        if not check_col(-player_speed, 0):
            player_x -= player_speed
    if keys[pygame.K_d]:
        for tile in tiles:
            if pygame.Rect.colliderect(tile.rect, pygame.Rect(player_x - dummy_camera.x + player_speed, player_y - dummy_camera.y, player_size, player_size)):
                collide = True
        if not check_col(player_speed, 0):
            player_x += player_speed
    if keys[pygame.K_ESCAPE]:
        pygame.quit()
        sys.exit()

    camera.center = pygame.Rect(player_x - camera.x, player_y - camera.y, player_size, player_size).center

    player_rect = pygame.draw.rect(screen, WHITE, pygame.Rect(player_x - camera.x, player_y - camera.y, player_size, player_size))
    
    enemy_spawn_timer += 1
    if enemy_spawn_timer >= 60: 
        spawn_enemy()
        enemy_spawn_timer = 0
    
    for enemy in enemies:
        move_enemy(enemy)

        dist = math.sqrt((player_x - enemy[0]) ** 2 + (player_y - enemy[1]) ** 2)
        if dist < 200:
            enemy[2] = GREEN
        else:
            enemy[2] = RED
            
        enemy_rect = pygame.draw.rect(screen, enemy[2], (enemy[0] - camera.x, enemy[1] - camera.y, enemy_size, enemy_size))

        if player_rect.colliderect(enemy_rect):
            reset_game()

    if not ammo_spawned:
        ammo_spawned = True
        spawn_ammo()
    
    ammo_rect = pygame.draw.rect(screen, WHITE, (ammo_x - camera.x, ammo_y - camera.y, 15, 15))

    if player_rect.colliderect(ammo_rect):
        ammo += 1
        ammo_spawned = False

    score_text_surface = font.render("Score: " + str(score), True, (255, 255, 255))
    screen.blit(score_text_surface, [5,5])

    ammo_text_surface = font.render("Ammo: " + str(ammo), True, (255, 255, 255))
    screen.blit(ammo_text_surface, [5,30])

pygame.quit()
sys.exit()
