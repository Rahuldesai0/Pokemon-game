# world_manager.py
import os
from collections import deque
import pygame
from settings import TILESIZE, MAPS_FOLDER
import tilemap
import map_connections
from utils import resource_path


class MapInstance:
    def __init__(self, name: str, tilemap_obj: tilemap.TileMap, world_x: int, world_y: int):
        self.name = name
        self.map = tilemap_obj

        # world_x & world_y come DIRECTLY from the map’s custom properties
        self.world_x = int(world_x)
        self.world_y = int(world_y)

    @property
    def pixel_x(self):
        return self.world_x * TILESIZE

    @property
    def pixel_y(self):
        return self.world_y * TILESIZE

    @property
    def pixel_width(self):
        return self.map.pixel_width

    @property
    def pixel_height(self):
        return self.map.pixel_height


class MapManager:
    def __init__(self, maps_folder=MAPS_FOLDER):
        self.maps_folder = maps_folder
        self.instances = {}  # name → MapInstance

        self.world_left = 0
        self.world_top = 0
        self.world_width = 0
        self.world_height = 0

    # --------------------------------------------------------
    # Resolve map name → path
    # --------------------------------------------------------
    def _map_path_for(self, map_name):
        filename = map_name + ".json"
        full_path = resource_path(os.path.join(self.maps_folder, filename))

        if not os.path.exists(full_path):
            print("MapManager ERROR: missing map:", full_path)

        return full_path

    # --------------------------------------------------------
    # Load a TileMap instance
    # --------------------------------------------------------
    def load_map_file(self, map_name):
        return tilemap.TileMap(self._map_path_for(map_name))

    # --------------------------------------------------------
    # Build all interconnected maps starting from root
    # --------------------------------------------------------
    def build_world(self, root_map_name, load_connected=True):
        self.instances.clear()

        queue = deque([root_map_name])
        loaded = set()

        while queue:
            name = queue.popleft()
            if name in loaded:
                continue

            try:
                tm = self.load_map_file(name)
            except Exception as e:
                print("MapManager: failed to load", name, e)
                continue

            inst = MapInstance(
                name=name,
                tilemap_obj=tm,
                world_x=tm.world_x,  # from TileMap custom properties
                world_y=tm.world_y
            )

            self.instances[name] = inst
            loaded.add(name)

            # Add neighbors from region connections
            if load_connected:
                for n in map_connections.REGION_CONNECTIONS.get(name, []):
                    if n not in loaded:
                        queue.append(n)

        self._recompute_bounds()

    # --------------------------------------------------------
    # Compute total world bounds
    # --------------------------------------------------------
    def _recompute_bounds(self):
        if not self.instances:
            self.world_left = self.world_top = 0
            self.world_width = self.world_height = 0
            return

        left = min(inst.pixel_x for inst in self.instances.values())
        top = min(inst.pixel_y for inst in self.instances.values())
        right = max(inst.pixel_x + inst.pixel_width for inst in self.instances.values())
        bottom = max(inst.pixel_y + inst.pixel_height for inst in self.instances.values())

        self.world_left = left
        self.world_top = top
        self.world_width = right - left
        self.world_height = bottom - top

    def get_world_bounds(self):
        return (self.world_left, self.world_top, self.world_width, self.world_height)

    # --------------------------------------------------------
    # Region lookup
    # --------------------------------------------------------
    def get_region_of_world(self, wx, wy):
        for name, inst in self.instances.items():
            if inst.pixel_x <= wx < inst.pixel_x + inst.map.pixel_width and \
               inst.pixel_y <= wy < inst.pixel_y + inst.map.pixel_height:
                return name
        return None

    # --------------------------------------------------------
    # Drawing by layer, spatial order preserved
    # --------------------------------------------------------
    def draw_by_layers(self, surface, camera, layer_names):
        ordered = sorted(
            self.instances.values(),
            key=lambda inst: (inst.world_y, inst.world_x)
        )

        for layer in layer_names:
            for inst in ordered:
                inst.map.draw_layer(
                    surface, camera, layer,
                    offset_x=inst.pixel_x, offset_y=inst.pixel_y
                )

    # --------------------------------------------------------
    # Collisions
    # --------------------------------------------------------
    def get_all_collisions(self):
        out = []
        for inst in self.instances.values():
            ox, oy = inst.pixel_x, inst.pixel_y
            for crect in inst.map.collisions:
                out.append(pygame.Rect(crect.x + ox, crect.y + oy, crect.width, crect.height))
        return out

    # --------------------------------------------------------
    # Lights
    # --------------------------------------------------------
    def get_all_lights(self):
        out = []
        for inst in self.instances.values():
            ox, oy = inst.pixel_x, inst.pixel_y
            for (lx, ly, w, h, r) in inst.map.lights:
                out.append((lx + ox, ly + oy, w, h, r))
        return out

    # --------------------------------------------------------
    # Ledges
    # --------------------------------------------------------
    def get_all_ledges(self):
        out = []
        for inst in self.instances.values():
            ox, oy = inst.pixel_x, inst.pixel_y
            for ledge in inst.map.ledges:
                r = ledge["rect"]
                out.append({
                    "rect": pygame.Rect(r.x + ox, r.y + oy, r.width, r.height),
                    "dir": ledge["dir"]
                })
        return out

    # --------------------------------------------------------
    # Warps
    # --------------------------------------------------------
    def get_all_warps(self):
        out = []
        for inst in self.instances.values():
            ox, oy = inst.pixel_x, inst.pixel_y

            for warp in inst.map.warps:
                r = pygame.Rect(
                    ox + warp["x"] * TILESIZE,
                    oy + warp["y"] * TILESIZE,
                    TILESIZE, TILESIZE
                )
                out.append({
                    "rect": r,
                    "dest_map": warp["dest_map"],
                    "dest_x": warp["dest_x"],
                    "dest_y": warp["dest_y"]
                })
        return out

    # --------------------------------------------------------
    # Load ONLY one map (for interiors)
    # --------------------------------------------------------
    def load_single_map(self, map_name):
        self.instances.clear()

        tm = self.load_map_file(map_name)
        inst = MapInstance(map_name, tm, world_x=0, world_y=0)

        self.instances[map_name] = inst
        self._recompute_bounds()
