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
        self.instances = {}   # name -> MapInstance
        self.world_left = 0
        self.world_top = 0
        self.world_width = 0
        self.world_height = 0

    # --------------------------------------------------------
    # RESOLVE MAP NAME → JSON PATH
    # --------------------------------------------------------
    def _map_path_for(self, map_name):
        filename = map_name + ".json"
        full_path = os.path.join(self.maps_folder, filename)
        full_path = resource_path(full_path)

        if not os.path.exists(full_path):
            print("MapManager ERROR: cannot find map:", full_path)
        else:
            print("File found: ", full_path)

        return full_path

    # --------------------------------------------------------
    # LOAD TILEMAP
    # --------------------------------------------------------
    def load_map_file(self, map_name):
        return tilemap.TileMap(self._map_path_for(map_name))

    # --------------------------------------------------------
    # BUILD WORLD (ROOT + CONNECTED MAPS)
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
                print("MapManager: failed to load map", name, e)
                continue

            # read world offsets from map custom properties
            props = tm.properties
            world_x = int(props.get("world_x", 0))
            world_y = int(props.get("world_y", 0))

            inst = MapInstance(name, tm, world_x, world_y)
            self.instances[name] = inst
            loaded.add(name)

            if load_connected:
                neighbors = map_connections.REGION_CONNECTIONS.get(name, [])
                for n in neighbors:
                    if n not in loaded:
                        queue.append(n)

        self._recompute_bounds()

    # --------------------------------------------------------
    # WORLD BOUNDS
    # --------------------------------------------------------
    def _recompute_bounds(self):
        if not self.instances:
            self.world_left = self.world_top = 0
            self.world_width = self.world_height = 0
            return

        left = min(i.pixel_x for i in self.instances.values())
        top = min(i.pixel_y for i in self.instances.values())
        right = max(i.pixel_x + i.pixel_width for i in self.instances.values())
        bottom = max(i.pixel_y + i.pixel_height for i in self.instances.values())

        self.world_left = left
        self.world_top = top
        self.world_width = right - left
        self.world_height = bottom - top

    def get_world_bounds(self):
        return (self.world_left, self.world_top, self.world_width, self.world_height)

    # --------------------------------------------------------
    # LAYERED DRAWING (SORTED BY world_y THEN world_x)
    # --------------------------------------------------------
    def draw_by_layers(self, surface, camera, layer_names):
        # Ensures correct spatial order: maps above are drawn first
        ordered_maps = sorted(
            self.instances.values(),
            key=lambda inst: (inst.world_y, inst.world_x)
        )

        for layer in layer_names:
            for inst in ordered_maps:
                inst.map.draw_layer(
                    surface,
                    camera,
                    layer,
                    offset_x=inst.pixel_x,
                    offset_y=inst.pixel_y
                )

    # --------------------------------------------------------
    # COLLISIONS ACROSS ALL MAPS
    # --------------------------------------------------------
    def get_all_collisions(self):
        out = []
        for inst in self.instances.values():
            ox, oy = inst.pixel_x, inst.pixel_y
            for crect in inst.map.collisions:
                out.append(
                    pygame.Rect(
                        crect.x + ox,
                        crect.y + oy,
                        crect.width,
                        crect.height
                    )
                )
        return out

    # --------------------------------------------------------
    # LIGHTS ACROSS ALL MAPS
    # --------------------------------------------------------
    def get_all_lights(self):
        out = []
        for inst in self.instances.values():
            ox, oy = inst.pixel_x, inst.pixel_y
            for (lx, ly, w, h, r) in inst.map.lights:
                out.append((lx + ox, ly + oy, w, h, r))
        return out
