# game.py
import pygame
from datetime import datetime
from settings import MAP_PATH, TILESIZE, MAPS_FOLDER
from tilemap import TileMap
from player import Player
from camera import Camera
from virtual_controls import VirtualControls
from world_manager import MapManager
import os

# FIXED GAME AREA (20x15 tiles)
GAME_TILES_W = 16
GAME_TILES_H = 16
GAME_WIDTH = GAME_TILES_W * TILESIZE
GAME_HEIGHT = GAME_TILES_H * TILESIZE

# Lighting colors...
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

        self.window = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
        self.game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))

        # ---------------------------------------------------
        # REGION POPUP SYSTEM
        # ---------------------------------------------------
        self.region_popup_text = ""
        self.region_popup_timer = 0.0       # seconds remaining (visible + fade)
        self.current_region = None          # region key name
        self.dt = 0.0                       # last frame dt
        self.region_popup_y = -100  # start above the window

        # ---------------------------------------------------
        # LOAD WORLD USING MAPS_FOLDER ONLY
        # ---------------------------------------------------
        root_name = None
        for file in os.listdir(MAPS_FOLDER):
            if file.endswith(".json"):
                root_name = os.path.splitext(file)[0]
                break

        if root_name is None:
            raise RuntimeError("ERROR: No .json maps found in MAPS_FOLDER")

        self.current_region = root_name

        self.map_manager = MapManager(maps_folder=MAPS_FOLDER)
        self.map_manager.build_world(root_name, load_connected=True)

        self.camera = Camera(GAME_WIDTH, GAME_HEIGHT)
        self.controls = VirtualControls()

        # ---------------------------------------------------
        # START PLAYER AT CENTER OF ROOT MAP
        # ---------------------------------------------------
        root_inst = self.map_manager.instances[root_name]

        start_x = root_inst.pixel_x + root_inst.map.pixel_width // 2
        start_y = root_inst.pixel_y + root_inst.map.pixel_height // 2

        self.player = Player(start_x, start_y, self.map_manager)

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

    def update(self, dt):
        # store dt for any draw-time needs (we don't use dt inside draw_native)
        self.dt = dt

        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                self.running = False

        win_w, win_h = self.window.get_size()
        self.controls.update(events, (win_w, win_h))

        # Track region before/after player update
        old_region = self.current_region

        # Player update (movement)
        self.player.update(dt, self.controls.actions)

        # Detect region change by asking map_manager
        new_region = self.map_manager.get_region_of_world(
            self.player.rect.centerx,
            self.player.rect.centery
        )

        # Only trigger popup when entering a valid new region
        if new_region is not None and new_region != old_region:
            self.current_region = new_region
            # Format popup text (convert _ → space and uppercase)
            self.region_popup_text = new_region.replace("_", " ").upper()
            # Show for 5 seconds (visible + fade handled in draw)
            self.region_popup_timer = 2.0
            print("Player is in:", new_region)

        # Decrement popup timer (clamp to zero)
        if self.region_popup_timer > 0:
            self.region_popup_timer = max(0.0, self.region_popup_timer - dt)

        # Camera clamps to world bounds
        wl, wt, ww, wh = self.map_manager.get_world_bounds()
        self.camera.update(self.player.rect, wl, wt, ww, wh)

    # -------------------------
    # DRAW WORLD + REGION POPUP
    # -------------------------
    def draw_native(self):
        surf = self.game_surface
        surf.fill((0,0,0))

        # Draw world layers
        layer_order = ["floor", "grass", "walls"]
        self.map_manager.draw_by_layers(surf, self.camera, layer_order)
        self.player.draw(surf, self.camera)
        self.map_manager.draw_by_layers(surf, self.camera, ["above"])

        # DAY/NIGHT LIGHTING
        overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
        now = datetime.now()
        m = now.hour * 60 + now.minute

        if SUNRISE_START <= m < SUNRISE_END:
            t = (m - SUNRISE_START)/5
            tint = lerp_color(LIGHT_NIGHT, LIGHT_MORNING, t)
            alpha = int(200*(1-t))
        elif SUNRISE_END <= m < SUNSET_START:
            tint = LIGHT_DAY
            alpha = 0
        elif SUNSET_START <= m < SUNSET_END:
            t = (m - SUNSET_START)/5
            tint = lerp_color(LIGHT_DAY, LIGHT_EVENING, t)
            alpha = int(80*t)
        elif SUNSET_END <= m < NIGHT_START:
            tint = LIGHT_EVENING
            alpha = 80
        elif NIGHT_START <= m < NIGHT_END:
            t = (m - NIGHT_START)/5
            tint = lerp_color(LIGHT_EVENING, LIGHT_NIGHT, t)
            alpha = int(200*t)
        else:
            tint = LIGHT_NIGHT
            alpha = 200

        if alpha > 0:
            overlay.fill((*tint, alpha))

        is_night = not (m > SUNRISE_START and m < NIGHT_START)
        if is_night:
            for lx, ly, w, h, r in self.map_manager.get_all_lights():
                cx = lx + w/2
                cy = ly + h/2
                sx = int(cx - self.camera.x)
                sy = int(cy - self.camera.y)
                pygame.draw.circle(overlay, (0,0,0,0), (sx, sy), int(r))

        surf.blit(overlay, (0,0))

        # ------------------------
        # REGION POPUP ANIMATION
        # ------------------------
        if self.region_popup_timer > 0 or self.region_popup_y > -100:
            target_y = 16
            speed = 400  # px/sec

            dt = self.dt
            if self.region_popup_timer > 0:
                self.region_popup_y += speed * dt
                if self.region_popup_y > target_y:
                    self.region_popup_y = target_y
            else:
                self.region_popup_y -= speed * dt
                if self.region_popup_y < -80-10:  # box height + extra
                    self.region_popup_y = -80-10

            # Popup box
            box_width, box_height = 400, 80
            box_x = (GAME_WIDTH - box_width)//2
            box_y = int(self.region_popup_y)

            rect_surf = pygame.Surface((box_width, box_height))
            rect_surf.fill((255,255,255))  # white background
            pygame.draw.rect(rect_surf, (0,0,0), rect_surf.get_rect(), 4)  # border

            try:
                font = pygame.font.Font("PressStart2P.ttf", 32)
            except:
                font = pygame.font.SysFont("Courier", 32, bold=True)

            text_surf = font.render(self.region_popup_text, True, (0,0,0))
            text_rect = text_surf.get_rect(center=(box_width//2, box_height//2))
            rect_surf.blit(text_surf, text_rect)

            surf.blit(rect_surf, (box_x, box_y))

    # ----------------------------------------
    # SCALE TO WINDOW + DRAW UI CONTROLS
    # ----------------------------------------
    def present(self):# In your main loop:
        win_w, win_h = self.window.get_size()
        self.controls.draw(self.window)


        # Compute scale to maintain aspect ratio
        scale_w = win_w / GAME_WIDTH
        scale_h = win_h / GAME_HEIGHT
        scale = min(scale_w, scale_h)

        # Scaled game surface size
        scaled_width = int(GAME_WIDTH * scale)
        scaled_height = int(GAME_HEIGHT * scale)

        # Offsets for centering (letterbox/pillarbox)
        offset_x = (win_w - scaled_width)//2
        offset_y = (win_h - scaled_height)//2

        # Scale and blit game surface
        final_surf = pygame.transform.scale(self.game_surface, (scaled_width, scaled_height))
        self.window.fill((0,0,0))  # margins
        self.window.blit(final_surf, (offset_x, offset_y))

        # Draw scaled UI controls
        self.controls.draw(self.window)

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
