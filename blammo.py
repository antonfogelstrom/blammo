import pygame
import sys
import random
import math
import csv


class Tile(pygame.sprite.Sprite):
    spawn_x = 0
    spawn_y = 0
    collision = False

    def __init__(self, _image, x, y, collison):
        pygame.sprite.Sprite.__init__(self)
        self.image = _image
        self.rect = self.image.get_rect()
        self.spawn_x = x
        self.spawn_y = y
        self.rect.x = x
        self.rect.y = y
        self.collision = collison

    def camera_offset(self, _camera):
        self.rect.x = self.spawn_x - _camera.x
        self.rect.y = self.spawn_y - _camera.y


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, target):
        pygame.sprite.Sprite.__init__(self)
        self.image_out_of_range = pygame.image.load('enemy.png')
        self.image_in_range = pygame.image.load('enemy_target.png')
        self.in_range = False
        self.image = pygame.image.load('enemy.png')
        self.rect = pygame.Rect(x, y, enemy_size, enemy_size)
        self.positional_rect = pygame.Rect(x, y, enemy_size, enemy_size)
        self.target = target

    def set_out_of_range(self):
        self.image = self.image_out_of_range
        self.in_range = False

    def set_in_range(self):
        self.image = self.image_in_range
        self.in_range = True

    def get_is_in_range(self):
        return self.in_range

    def set_target(self, target):
        self.target = target

    def move(self, _camera, _tiles):
        if self.positional_rect.x < self.target.x and not self.check_col(_camera, _tiles, enemy_speed,
                                                                         0) and self.positional_rect.x + self.target.x > enemy_speed:
            self.positional_rect.x += enemy_speed
        elif self.positional_rect.x > self.target.x and not self.check_col(_camera, _tiles, -enemy_speed,
                                                                           0) and self.positional_rect.x - self.target.x > enemy_speed:
            self.positional_rect.x -= enemy_speed

        if self.positional_rect.y < self.target.y and not self.check_col(_camera, _tiles, 0,
                                                                         enemy_speed) and self.positional_rect.y + self.target.y > enemy_speed:
            self.positional_rect.y += enemy_speed
        elif self.positional_rect.y > self.target.y and not self.check_col(_camera, _tiles, 0,
                                                                           -enemy_speed) and self.positional_rect.y - self.target.y > enemy_speed:
            self.positional_rect.y -= enemy_speed

    def check_col(self, _camera, _tiles, x, y):
        copy = pygame.Rect.copy(self.positional_rect)
        copy = copy.move(x - _camera.x, y - _camera.y)

        for _tile in _tiles:
            if _tile.collision and pygame.Rect.colliderect(_tile.rect, copy):
                return True

        return False


pygame.init()
pygame.font.init()
font = pygame.font.Font(None, 36)

WIDTH, HEIGHT = 800, 640
GAMEWORLD_WIDTH, GAMEWORLD_HEIGHT = 1024, 1024
SQUARE_SIZE = 32

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
player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
player_render_rect = player_rect

enemy_size = 32
enemy_speed = 3
enemies = pygame.sprite.Group()

score = 0
ammo = 3

ammo_spawned = False
ammo_x = 0
ammo_y = 0

tiles = pygame.sprite.Group()
GRASS = 1001
WATER = 1000
grass_image = pygame.image.load("grass.png")
water_image = pygame.image.load("water.png")

_map = []
with open("map.csv", "r") as file:
    reader = csv.reader(file)
    for row in reader:
        # Assuming each row contains numeric data, convert them to integers or floats
        numeric_row = [int(value) for value in row]
        _map.append(numeric_row)

for row_index, row in enumerate(_map):
    for col_index, value in enumerate(row):
        collision = False
        image = None
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
    enemies.add(Enemy(x, y, player_rect))


def spawn_ammo():
    global ammo_x, ammo_y
    ammo_x = random.randint(25, WIDTH - 25)
    ammo_y = random.randint(25, HEIGHT - 25)


def destroy_green_enemies():
    _list = []
    for _enemy in enemies:
        if _enemy.get_is_in_range():
            _list.append(_enemy)

    if len(_list) > 0:
        global ammo
        ammo -= 1

    for _enemy in _list:
        enemies.remove(_enemy)
        global score
        score += 1


def reset_game():
    global player_x, player_y, enemies, score, ammo, ammo_x, ammo_y, ammo_spawned, tiles
    player_x = WIDTH // 2
    player_y = HEIGHT // 2
    enemies = pygame.sprite.Group()
    score = 0
    ammo = 3
    ammo_x = 0
    ammo_y = 0
    ammo_spawned = False


def check_col(_rect):
    for _tile in tiles:
        if _tile.collision and pygame.Rect.colliderect(_tile.rect, _rect):
            return True
    return False


running = True
enemy_spawn_timer = 0
clock = pygame.time.Clock()
while running:
    clock.tick(60)
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

    if keys[pygame.K_w]:
        if not check_col(player_render_rect.move(0, -player_speed)):
            player_y -= player_speed
    if keys[pygame.K_s]:
        if not check_col(player_render_rect.move(0, player_speed)):
            player_y += player_speed
    if keys[pygame.K_a]:
        if not check_col(player_render_rect.move(-player_speed, 0)):
            player_x -= player_speed
    if keys[pygame.K_d]:
        if not check_col(player_render_rect.move(player_speed, 0)):
            player_x += player_speed
    if keys[pygame.K_ESCAPE]:
        pygame.quit()
        sys.exit()

    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
    camera.center = player_rect.center

    for tile in tiles:
        tile.camera_offset(camera)
    tiles.draw(screen)

    player_render_rect = pygame.draw.rect(screen, WHITE, player_rect.move(-camera.x, -camera.y))

    enemy_spawn_timer += 1
    if enemy_spawn_timer >= 60:
        spawn_enemy()
        enemy_spawn_timer = 0

    for enemy in enemies:
        enemy.target = player_rect
        enemy.move(camera, tiles)

        dist = math.sqrt((enemy.target.x - enemy.positional_rect.x) ** 2 + (enemy.target.y - enemy.positional_rect.y) ** 2)
        if dist < 200:
            enemy.set_in_range()
        else:
            enemy.set_out_of_range()

        enemy.rect = enemy.positional_rect.move(-camera.x, -camera.y)
    enemies.draw(screen)

    if not ammo_spawned:
        ammo_spawned = True
        spawn_ammo()

    ammo_rect = pygame.draw.rect(screen, WHITE, (ammo_x - camera.x, ammo_y - camera.y, 15, 15))

    if player_render_rect.colliderect(ammo_rect):
        ammo += 1
        ammo_spawned = False

    score_text_surface = font.render("Score: " + str(score), True, (255, 255, 255))
    screen.blit(score_text_surface, [5, 5])

    ammo_text_surface = font.render("Ammo: " + str(ammo), True, (255, 255, 255))
    screen.blit(ammo_text_surface, [5, 30])

    pygame.display.flip()
pygame.quit()
sys.exit()
