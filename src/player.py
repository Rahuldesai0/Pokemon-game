import pygame
from settings import PLAYER_IMAGE, TILESIZE
from utils import resource_path

PLAYER_WIDTH = TILESIZE
PLAYER_HEIGHT = int(TILESIZE * 1.5)
FEET_HEIGHT = TILESIZE
MOVE_TIME = 0.15  # seconds per tile

class Player:
    def __init__(self, x, y, collisions):
        # Load sprite
        img_path = resource_path(PLAYER_IMAGE)
        try:
            self.image = pygame.image.load(img_path).convert_alpha()
        except:
            self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
            self.image.fill((255, 255, 0))

        # Feet-only collision rect
        self.rect = pygame.Rect(x, y, TILESIZE, FEET_HEIGHT)
        self.head_offset = PLAYER_HEIGHT - FEET_HEIGHT
        self.collisions = collisions

        # Tile coordinates
        self.tile_x = x // TILESIZE
        self.tile_y = y // TILESIZE

        # Movement
        self.moving = False
        self.start_pos = pygame.Vector2(self.rect.x, self.rect.y)
        self.target_pos = self.start_pos.copy()
        self.move_timer = 0

    # Feet-only collision check
    def can_move(self, tx, ty):
        test_rect = pygame.Rect(tx * TILESIZE, ty * TILESIZE, TILESIZE, FEET_HEIGHT)
        for wall in self.collisions:
            if test_rect.colliderect(wall):
                return False
        return True

    # Start moving to a tile
    def start_move(self, dx, dy):
        next_tile_x = self.tile_x + dx
        next_tile_y = self.tile_y + dy

        if self.can_move(next_tile_x, next_tile_y):
            self.start_pos = pygame.Vector2(self.rect.x, self.rect.y)
            self.target_pos = pygame.Vector2(next_tile_x * TILESIZE, next_tile_y * TILESIZE)
            self.tile_x = next_tile_x
            self.tile_y = next_tile_y
            self.move_timer = 0
            self.moving = True

    # Update player
    def update(self, dt, actions):
        keys = pygame.key.get_pressed()

        # Determine latest direction pressed
        dx, dy = 0, 0
        if actions["left"] or keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx, dy = -1, 0
        if actions["right"] or keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx, dy = 1, 0
        if actions["up"] or keys[pygame.K_UP] or keys[pygame.K_w]:
            dx, dy = 0, -1
        if actions["down"] or keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dx, dy = 0, 1

        # Sprint logic
        sprint = actions["B"] or keys[pygame.K_SPACE] or keys[pygame.K_LSHIFT]
        speed_mult = 2 if sprint else 1

        # Start new move only if not moving
        if not self.moving and (dx != 0 or dy != 0):
            self.start_move(dx, dy)

        # Interpolate movement
        if self.moving:
            self.move_timer += dt * speed_mult
            t = min(self.move_timer / MOVE_TIME, 1)
            self.rect.x = round(self.start_pos.x + (self.target_pos.x - self.start_pos.x) * t)
            self.rect.y = round(self.start_pos.y + (self.target_pos.y - self.start_pos.y) * t)

            # When tile reached
            if t >= 1:
                self.rect.x = int(self.target_pos.x)
                self.rect.y = int(self.target_pos.y)
                self.moving = False


    # Draw full sprite
    def draw(self, screen, camera):
        draw_x = self.rect.x
        draw_y = self.rect.y - self.head_offset
        screen.blit(self.image, camera.apply(pygame.Rect(draw_x, draw_y, PLAYER_WIDTH, PLAYER_HEIGHT)))
