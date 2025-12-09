import pygame
from settings import PLAYER_IMAGE, TILESIZE, MOVE_TIME
from utils import resource_path

PLAYER_WIDTH = TILESIZE
PLAYER_HEIGHT = int(TILESIZE * 1.5)
FEET_HEIGHT = TILESIZE

class Player:
    def __init__(self, x, y, map_manager, debug=False):
        # load sprite (unchanged)
        img_path = resource_path(PLAYER_IMAGE)
        try:
            self.image = pygame.image.load(img_path).convert_alpha()
        except:
            self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
            self.image.fill((255, 255, 0))

        # feet-only rect in world coords
        self.rect = pygame.Rect(x, y, TILESIZE, FEET_HEIGHT)
        self.head_offset = PLAYER_HEIGHT - FEET_HEIGHT

        # keep reference to MapManager so we can query current world collisions/ledges
        self.map_manager = map_manager

        # tile coords (tile-locked)
        self.tile_x = x // TILESIZE
        self.tile_y = y // TILESIZE

        # movement interpolation
        self.moving = False
        self.start_pos = pygame.Vector2(self.rect.x, self.rect.y)
        self.target_pos = self.start_pos.copy()
        self.move_timer = 0

        self.debug = debug

    # -------------------------
    # ledge helper: checks allowed direction
    # ledge_dir: 0=down,1=up,2=left,3=right
    # dx,dy are integer tile movement (-1,0,1)
    # -------------------------
    def _ledge_allows(self, ledge_dir, dx, dy):
        if ledge_dir == 0:   # allowed moving downwards
            return dy > 0
        if ledge_dir == 1:   # allowed moving upwards
            return dy < 0
        if ledge_dir == 2:   # allowed moving left
            return dx < 0
        if ledge_dir == 3:   # allowed moving right
            return dx > 0
        return False

    # -------------------------
    # Can move to tile (tx,ty) given attempted movement (dx,dy)
    # Uses world-space ledges and walls from MapManager
    # -------------------------
    def can_move(self, tx, ty, dx, dy):
        # build test rect in world pixel coords
        test_rect = pygame.Rect(tx * TILESIZE, ty * TILESIZE, TILESIZE, FEET_HEIGHT)

        # query world ledges and collisions each time (keeps dynamic maps safe)
        ledges = self.map_manager.get_all_ledges()    # returns list of {"rect":Rect, "dir":int}
        collisions = self.map_manager.get_all_collisions()

        # --- 1) If test intersects any ledge, the ledge controls passability ---
        for ledge in ledges:
            lr = ledge["rect"]
            if test_rect.colliderect(lr):
                allowed = self._ledge_allows(ledge["dir"], dx, dy)
                if self.debug:
                    print(f"[Ledge] test {test_rect} intersects ledge {lr} dir={ledge['dir']} -> allowed={allowed}")
                if not allowed:
                    return False
                # if allowed, continue checking walls (an allowed ledge does not bypass walls logic below if you want it too)
                # Usually ledge object sits visually on top of tiles; we allow passage if direction matches.

        # --- 2) Wall collision: if any wall collides, block ---
        for wall in collisions:
            if test_rect.colliderect(wall):
                if self.debug:
                    print(f"[Wall] test {test_rect} collides with wall {wall} -> blocked")
                return False

        return True

    # -------------------------
    # Start a tile move
    # -------------------------
    def start_move(self, dx, dy):
        # No diagonals
        if dx != 0 and dy != 0:
            return

        next_tile_x = self.tile_x + dx
        next_tile_y = self.tile_y + dy

        if self.can_move(next_tile_x, next_tile_y, dx, dy):
            self.start_pos = pygame.Vector2(self.rect.x, self.rect.y)
            self.target_pos = pygame.Vector2(next_tile_x * TILESIZE, next_tile_y * TILESIZE)
            self.tile_x = next_tile_x
            self.tile_y = next_tile_y
            self.move_timer = 0
            self.moving = True
            if self.debug:
                print(f"[Move] starting move to tile ({self.tile_x},{self.tile_y})")
        else:
            if self.debug:
                print(f"[Move] blocked from ({self.tile_x},{self.tile_y}) -> ({next_tile_x},{next_tile_y}) dx,dy=({dx},{dy})")

    # -------------------------
    # Update (same API you have)
    # -------------------------
    def update(self, dt, actions):
        keys = pygame.key.get_pressed()

        # determine latest direction pressed
        dx, dy = 0, 0
        if actions["left"] or keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx, dy = -1, 0
        if actions["right"] or keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx, dy = 1, 0
        if actions["up"] or keys[pygame.K_UP] or keys[pygame.K_w]:
            dx, dy = 0, -1
        if actions["down"] or keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dx, dy = 0, 1

        sprint = actions["B"] or keys[pygame.K_SPACE] or keys[pygame.K_LSHIFT]
        speed_mult = 2 if sprint else 1

        # start new move only when not currently moving
        if not self.moving and (dx != 0 or dy != 0):
            self.start_move(dx, dy)

        # interpolate if moving
        if self.moving:
            self.move_timer += dt * speed_mult
            t = min(self.move_timer / MOVE_TIME, 1)
            self.rect.x = round(self.start_pos.x + (self.target_pos.x - self.start_pos.x) * t)
            self.rect.y = round(self.start_pos.y + (self.target_pos.y - self.start_pos.y) * t)

            if t >= 1:
                self.rect.x = int(self.target_pos.x)
                self.rect.y = int(self.target_pos.y)
                self.moving = False
                if self.debug:
                    print(f"[Move] arrived at tile ({self.tile_x},{self.tile_y})")

    # -------------------------
    # Draw full sprite
    # -------------------------
    def draw(self, screen, camera):
        draw_x = self.rect.x
        draw_y = self.rect.y - self.head_offset
        screen.blit(self.image, camera.apply(pygame.Rect(draw_x, draw_y, PLAYER_WIDTH, PLAYER_HEIGHT)))
