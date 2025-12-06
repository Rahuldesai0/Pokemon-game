import pygame
from settings import PLAYER_IMAGE, PLAYER_SPEED, TILESIZE
from utils import resource_path

PLAYER_WIDTH = 32
PLAYER_HEIGHT = 48
FEET_HEIGHT = 32  # collision box = lower part of sprite

MOVE_TIME = 0.15  # seconds to move exactly 1 tile


class Player:
    def __init__(self, x, y, collisions):
        # Load sprite
        img_path = resource_path(PLAYER_IMAGE)
        try:
            self.image = pygame.image.load(img_path).convert_alpha()
        except:
            self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
            self.image.fill((255, 255, 0))

        # Feet collision box
        self.rect = pygame.Rect(
            x, y + (PLAYER_HEIGHT - FEET_HEIGHT), PLAYER_WIDTH, FEET_HEIGHT
        )

        self.collisions = collisions

        # Tile movement state
        self.moving = False
        self.start_pos = pygame.Vector2(self.rect.x, self.rect.y)
        self.target_pos = pygame.Vector2(self.rect.x, self.rect.y)
        self.move_timer = 0

    def try_start_move(self, dx, dy):
        if self.moving:
            return

        # Cannot move diagonally on tile-step
        if dx != 0 and dy != 0:
            return

        # Compute target tile in pixel space
        tx = self.rect.x + dx * TILESIZE
        ty = self.rect.y + dy * TILESIZE

        test_rect = pygame.Rect(tx, ty, self.rect.width, self.rect.height)

        # Collision check
        for wall in self.collisions:
            if test_rect.colliderect(wall):
                return  # blocked

        # Start tile-step animation
        self.moving = True
        self.move_timer = 0
        self.start_pos = pygame.Vector2(self.rect.x, self.rect.y)
        self.target_pos = pygame.Vector2(tx, ty)

    def update(self, dt, actions):
        keys = pygame.key.get_pressed()

        # Only choose a direction if we're not already moving
        if not self.moving:

            # MERGE VIRTUAL BUTTONS + KEYBOARD
            if actions["left"] or keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.try_start_move(-1, 0)

            elif actions["right"] or keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.try_start_move(1, 0)

            elif actions["up"] or keys[pygame.K_UP] or keys[pygame.K_w]:
                self.try_start_move(0, -1)

            elif actions["down"] or keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.try_start_move(0, 1)

        # movement interpolation untouched…
        if self.moving:
            self.move_timer += dt
            t = min(self.move_timer / MOVE_TIME, 1)
            new_x = self.start_pos.x + (self.target_pos.x - self.start_pos.x) * t
            new_y = self.start_pos.y + (self.target_pos.y - self.start_pos.y) * t
            self.rect.x = round(new_x)
            self.rect.y = round(new_y)

            if t >= 1:
                self.rect.x = int(self.target_pos.x)
                self.rect.y = int(self.target_pos.y)
                self.moving = False


    def draw(self, screen, camera):
        draw_x = self.rect.x
        draw_y = self.rect.y - (PLAYER_HEIGHT - FEET_HEIGHT)
        screen.blit(self.image, camera.apply(
            pygame.Rect(draw_x, draw_y, PLAYER_WIDTH, PLAYER_HEIGHT)
        ))
