# player.py
import pygame
from settings import PLAYER_IMAGE, TILESIZE, MOVE_TIME
from utils import resource_path

PLAYER_WIDTH = TILESIZE
PLAYER_HEIGHT = int(TILESIZE * 1.5)
FEET_HEIGHT = TILESIZE


class Player:
    def __init__(self, x, y, map_manager, debug=False):

        img_path = resource_path(PLAYER_IMAGE)
        try:
            sheet = pygame.image.load(img_path).convert_alpha()
        except:
            sheet = pygame.Surface((PLAYER_WIDTH * 4, PLAYER_HEIGHT), pygame.SRCALPHA)
            sheet.fill((255, 255, 0))

        self.frames = {
            "down":  sheet.subsurface((0 * PLAYER_WIDTH, 0, PLAYER_WIDTH, PLAYER_HEIGHT)),
            "up":    sheet.subsurface((1 * PLAYER_WIDTH, 0, PLAYER_WIDTH, PLAYER_HEIGHT)),
            "left":  sheet.subsurface((2 * PLAYER_WIDTH, 0, PLAYER_WIDTH, PLAYER_HEIGHT)),
            "right": sheet.subsurface((3 * PLAYER_WIDTH, 0, PLAYER_WIDTH, PLAYER_HEIGHT)),
        }

        self.direction = "down"
        self.image = self.frames[self.direction]

        self.rect = pygame.Rect(x, y, TILESIZE, FEET_HEIGHT)
        self.head_offset = PLAYER_HEIGHT - FEET_HEIGHT

        self.map_manager = map_manager

        self.tile_x = x // TILESIZE
        self.tile_y = y // TILESIZE

        self.moving = False
        self.start_pos = pygame.Vector2(self.rect.x, self.rect.y)
        self.target_pos = self.start_pos.copy()
        self.move_timer = 0

        self.debug = debug

        # interaction flags (read by Game)
        self.pending_sign_text = None
        self.pending_warp = None

    # ----------------------------------------------------------

    def set_direction(self, dx, dy):
        if dx > 0:
            self.direction = "right"
        elif dx < 0:
            self.direction = "left"
        elif dy > 0:
            self.direction = "down"
        elif dy < 0:
            self.direction = "up"
        self.image = self.frames[self.direction]

    # ----------------------------------------------------------

    def _ledge_allows(self, ledge_dir, dx, dy):
        return (
            (ledge_dir == 0 and dy > 0) or
            (ledge_dir == 1 and dy < 0) or
            (ledge_dir == 2 and dx < 0) or
            (ledge_dir == 3 and dx > 0)
        )

    # ----------------------------------------------------------

    def can_move(self, tx, ty, dx, dy):
        test_rect = pygame.Rect(tx * TILESIZE, ty * TILESIZE, TILESIZE, FEET_HEIGHT)

        for ledge in self.map_manager.get_all_ledges():
            if test_rect.colliderect(ledge["rect"]):
                if not self._ledge_allows(ledge["dir"], dx, dy):
                    return False

        for wall in self.map_manager.get_all_collisions():
            if test_rect.colliderect(wall):
                return False

        return True

    # ----------------------------------------------------------

    def start_move(self, dx, dy):
        if dx != 0 and dy != 0:
            return

        next_tx = self.tile_x + dx
        next_ty = self.tile_y + dy

        if self.can_move(next_tx, next_ty, dx, dy):
            self.start_pos = pygame.Vector2(self.rect.x, self.rect.y)
            self.target_pos = pygame.Vector2(next_tx * TILESIZE, next_ty * TILESIZE)
            self.tile_x = next_tx
            self.tile_y = next_ty
            self.move_timer = 0
            self.moving = True

    # ----------------------------------------------------------

    def update(self, dt, controls):
        dx = dy = 0

        if controls.actions["left"]:
            dx = -1
        elif controls.actions["right"]:
            dx = 1
        elif controls.actions["up"]:
            dy = -1
        elif controls.actions["down"]:
            dy = 1

        # update facing even if blocked
        if dx or dy:
            self.set_direction(dx, dy)

        # interaction (DISCRETE)
        if controls.just_pressed["A"]:
            sign = self.check_sign_ahead()
            if sign:
                self.pending_sign_text = sign

        sprint = controls.actions["B"]
        speed_mult = 2 if sprint else 1

        if not self.moving and (dx or dy):
            self.start_move(dx, dy)

        if self.moving:
            self.move_timer += dt * speed_mult
            t = min(self.move_timer / MOVE_TIME, 1)

            self.rect.x = round(self.start_pos.x + (self.target_pos.x - self.start_pos.x) * t)
            self.rect.y = round(self.start_pos.y + (self.target_pos.y - self.start_pos.y) * t)

            if t >= 1:
                self.rect.topleft = self.target_pos
                self.moving = False

                warp = self.check_for_warp()
                if warp:
                    self.pending_warp = warp

    # ----------------------------------------------------------

    def check_for_warp(self):
        feet = pygame.Rect(self.rect.x, self.rect.y, TILESIZE, FEET_HEIGHT)
        for warp in self.map_manager.get_all_warps():
            if feet.colliderect(warp["rect"]):
                return warp
        return None

    # ----------------------------------------------------------

    def check_sign_ahead(self):
        dx = dy = 0
        if self.direction == "up": dy = -1
        elif self.direction == "down": dy = 1
        elif self.direction == "left": dx = -1
        elif self.direction == "right": dx = 1

        rect = pygame.Rect(
            self.rect.x + dx * TILESIZE,
            self.rect.y + dy * TILESIZE,
            TILESIZE,
            FEET_HEIGHT
        )

        for sign in self.map_manager.get_all_signs():
            if rect.colliderect(sign["rect"]):
                return sign["text"]
        return None

    # ----------------------------------------------------------

    def draw(self, screen, camera):
        draw_x = self.rect.x
        draw_y = self.rect.y - self.head_offset
        screen.blit(
            self.image,
            camera.apply(pygame.Rect(draw_x, draw_y, PLAYER_WIDTH, PLAYER_HEIGHT))
        )
