from datetime import datetime

# settings.py
WIDTH = 800
HEIGHT = 600
FPS = 60
TITLE = "Pokemon Clone"

# Map & tiles
MAP_PATH = "assets/maps/route_1.json"       # export from Tiled (JSON)
TILESET_FOLDER = "assets/tilesets"       # where outdoor.png, buildings.png live
MAPS_FOLDER = "assets/maps"
# Default tile size (will be replaced by map's tile size if available)
TILESIZE = 32

NATIVE_WIDTH = 640
NATIVE_HEIGHT = 480

# Player
PLAYER_SPEED = 150  # pixels per second
PLAYER_SIZE = 32    # width/height in pixels (square placeholder)
MOVE_TIME = 0.15
PLAYER_IMAGE = "assets/entities/player.png"

# MUCH BETTER LIGHTING COLORS (Pokémon-like)

LIGHT_MORNING = (255, 180, 90)     # deep warm orange sunrise
LIGHT_DAY     = (255, 255, 255)    # no tint
LIGHT_EVENING = (255, 120, 40)     # strong orange sunset
LIGHT_NIGHT   = (10, 20, 40)       # very dark blue (almost black)
## Get hour+minute as a single float
now = datetime.now()
hour = now.hour
minute = now.minute
time = hour * 60 + minute   # total minutes since midnight

# Define minute marks
SUNRISE_START  = 5*60       # 05:00
SUNRISE_END    = 5*60 + 5   # 05:05

SUNSET_START   = 17*60      # 17:00
SUNSET_END     = 17*60 + 5  # 17:05

NIGHT_START    = 19*60      # 19:00
NIGHT_END      = 19*60 + 5  # 19:05

GAME_TILES_W = 16
GAME_TILES_H = 16
GAME_WIDTH = GAME_TILES_W * TILESIZE
GAME_HEIGHT = GAME_TILES_H * TILESIZE
