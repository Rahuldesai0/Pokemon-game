# game.py
import pygame
from datetime import datetime
from settings import MAP_PATH, TILESIZE
from tilemap import TileMap
from player import Player
from camera import Camera

# FIXED GAME AREA (20x15 tiles)
GAME_TILES_W = 16
GAME_TILES_H = 16
GAME_WIDTH = GAME_TILES_W * TILESIZE
GAME_HEIGHT = GAME_TILES_H * TILESIZE

# Lighting colors
LIGHT_MORNING = (255, 180, 90)
LIGHT_DAY     = (255, 255, 255)
LIGHT_EVENING = (255, 120, 40)
LIGHT_NIGHT   = (10, 20, 40)

SUNRISE_START = 5 * 60
SUNRISE_END   = 5 * 60 + 5
SUNSET_START  = 17 * 60
SUNSET_END    = 17 * 60 + 5
NIGHT_START   = 19 * 60
NIGHT_END     = 19 * 60 + 5

def lerp_color(a, b, t):
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t)
    )


class Game:
    def __init__(self):
        pygame.init()

        # OS window (resizable)
        self.window = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)

        # Internal fixed game surface
        self.game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))

        # Map and camera sized exactly to 20x15 tiles
        self.map = TileMap(MAP_PATH)
        self.camera = Camera(GAME_WIDTH, GAME_HEIGHT)

        # Player start
        start_x = self.map.pixel_width // 2
        start_y = self.map.pixel_height // 2
        self.player = Player(start_x, start_y, self.map.collisions)

        self.clock = pygame.time.Clock()
        self.running = True


    # ---------------------------------------------------
    # EVENT HANDLING
    # ---------------------------------------------------
    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self.running = False


    # ---------------------------------------------------
    # UPDATE
    # ---------------------------------------------------
    def update(self, dt):
        self.player.update(dt)
        self.camera.update(self.player.rect, self.map.pixel_width, self.map.pixel_height)


    # ---------------------------------------------------
    # DRAW WORLD INTO FIXED GAME SURFACE (20x15 tiles)
    # ---------------------------------------------------
    def draw_native(self):
        surf = self.game_surface
        surf.fill((0,0,0))

        # Layers
        self.map.draw_layer(surf, self.camera, "floor")
        self.map.draw_layer(surf, self.camera, "grass")
        self.map.draw_layer(surf, self.camera, "walls")
        self.player.draw(surf, self.camera)
        self.map.draw_layer(surf, self.camera, "above")

        # ---------------------------------------------------
        # DAY/NIGHT LIGHTING + LIGHT OBJECTS
        # ---------------------------------------------------
        overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
        now = datetime.now()
        m = now.hour * 60 + now.minute

        if SUNRISE_START <= m < SUNRISE_END:
            t = (m - SUNRISE_START) / 5
            tint = lerp_color(LIGHT_NIGHT, LIGHT_MORNING, t)
            alpha = int(200 * (1 - t))
        elif SUNRISE_END <= m < SUNSET_START:
            tint = LIGHT_DAY
            alpha = 0
        elif SUNSET_START <= m < SUNSET_END:
            t = (m - SUNSET_START) / 5
            tint = lerp_color(LIGHT_DAY, LIGHT_EVENING, t)
            alpha = int(80 * t)
        elif SUNSET_END <= m < NIGHT_START:
            tint = LIGHT_EVENING
            alpha = 80
        elif NIGHT_START <= m < NIGHT_END:
            t = (m - NIGHT_START) / 5
            tint = lerp_color(LIGHT_EVENING, LIGHT_NIGHT, t)
            alpha = int(200 * t)
        else:
            tint = LIGHT_NIGHT
            alpha = 200

        # ---------------------------------------------------
        # DAY/NIGHT LIGHTING + LIGHT OBJECTS
        # ---------------------------------------------------

        # ALWAYS create a fresh overlay every frame
        overlay = pygame.Surface(self.game_surface.get_size(), pygame.SRCALPHA)

        is_night = not (m > SUNRISE_START and m < NIGHT_START)

        # ---- Draw tint ONLY if non-zero alpha ----
        if alpha > 0:
            overlay.fill((*tint, alpha))

        # ---- Draw circles ONLY at night ----
        if is_night:
            for lx, ly, w, h, r in getattr(self.map, "lights", []):
                cx = lx + w/2
                cy = ly + h/2
                sx = int(cx - self.camera.x)
                sy = int(cy - self.camera.y)

                pygame.draw.circle(
                    overlay,
                    (0, 0, 0, 0),   # transparent hole
                    (sx, sy),
                    int(r)
                )

        # Final apply
        self.game_surface.blit(overlay, (0, 0))


    # ---------------------------------------------------
    # SCALE TO WINDOW WHILE FITTING WIDTH EXACTLY
    # ---------------------------------------------------
    def present(self):
        win_w, win_h = self.window.get_size()

        # Fit width
        scale = win_w / GAME_WIDTH
        scaled_height = GAME_HEIGHT * scale

        if scaled_height <= win_h:
            # Perfect: black bars top/bottom
            y = (win_h - scaled_height) // 2
            final = pygame.transform.scale(self.game_surface, (win_w, int(scaled_height)))

            self.window.fill((0,0,0))
            self.window.blit(final, (0, y))

        else:
            # If too tall, crop vertically (rare)
            final = pygame.transform.scale(self.game_surface, (win_w, int(scaled_height)))
            crop = pygame.Rect(0, (scaled_height - win_h)/2, win_w, win_h)

            self.window.blit(final, (0,0), area=crop)

        pygame.display.flip()


    # ---------------------------------------------------
    # MAIN LOOP
    # ---------------------------------------------------
    def run(self):
        while self.running:
            dt = self.clock.tick(60)/1000
            self.handle_events()
            self.update(dt)
            self.draw_native()
            self.present()

        pygame.quit()

