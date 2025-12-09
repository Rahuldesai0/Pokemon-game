# tilemap.py
import pygame
import json
import os
from typing import Dict
from settings import TILESIZE, TILESET_FOLDER
from utils import resource_path


class TileMap:
    """
    Loads a Tiled .json map including:
      - properties (world_x, world_y, region)
      - multiple tilesets
      - tile layers
      - collision walls layer
      - object layer (lights)
    """

    def __init__(self, map_json_path: str):
        map_path = resource_path(map_json_path)

        with open(map_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

        self.width = self.data["width"]
        self.height = self.data["height"]

        self.tile_w = self.data.get("tilewidth", TILESIZE)
        self.tile_h = self.data.get("tileheight", TILESIZE)

        self.pixel_width = self.width * self.tile_w
        self.pixel_height = self.height * self.tile_h

        # -------------------------------
        # MAP PROPERTIES (world_x/world_y)
        # -------------------------------
        props_raw = self.data.get("properties", {})
        if isinstance(props_raw, list):
            # convert array of {name,value} → dict
            props = {p.get("name"): p.get("value") for p in props_raw}
            self.properties = props
        else:
            self.properties = props_raw or {}

        # -------------------------------
        # TILESET PROCESSING
        # -------------------------------
        self.tiles: Dict[int, pygame.Surface] = {}

        for ts in self.data.get("tilesets", []):
            firstgid = ts["firstgid"]
            image_name = ts.get("image")

            if not image_name:
                continue

            tileset_path = resource_path(os.path.join(TILESET_FOLDER, image_name))
            image = pygame.image.load(tileset_path).convert_alpha()

            tw = ts.get("tilewidth", self.tile_w)
            th = ts.get("tileheight", self.tile_h)
            margin = ts.get("margin", 0)
            spacing = ts.get("spacing", 0)

            columns = (image.get_width() - margin + spacing) // (tw + spacing)
            rows = (image.get_height() - margin + spacing) // (th + spacing)

            gid = firstgid
            for ry in range(rows):
                for rx in range(columns):
                    x = margin + rx * (tw + spacing)
                    y = margin + ry * (th + spacing)
                    rect = pygame.Rect(x, y, tw, th)

                    surf = image.subsurface(rect).copy()
                    self.tiles[gid] = surf
                    gid += 1

        # -------------------------------
        # LAYERS
        # -------------------------------
        self.layers = [l for l in self.data.get("layers", []) if l.get("type") == "tilelayer"]

        self.layer_map = {}
        for i, layer in enumerate(self.layers):
            name = layer.get("name", "").lower()
            self.layer_map[name] = i

        # -------------------------------
        # COLLISION LAYER (walls)
        # -------------------------------
        self.collisions = []
        walls_idx = self.layer_map.get("walls")

        if walls_idx is not None:
            walls_layer = self.layers[walls_idx]
            data = walls_layer.get("data", [])
            for i, gid in enumerate(data):
                if gid == 0:
                    continue
                tx = (i % self.width) * self.tile_w
                ty = (i // self.width) * self.tile_h
                self.collisions.append(pygame.Rect(tx, ty, self.tile_w, self.tile_h))

        # --- Load directional ledges ---
        self.ledges = []
        for layer in self.data.get("layers", []):
            if layer.get("type") == "objectgroup" and layer.get("name", "").lower() == "ledge":
                for obj in layer.get("objects", []):
                    x = obj.get("x", 0)
                    y = obj.get("y", 0)
                    w = obj.get("width", self.tile_w)
                    h = obj.get("height", self.tile_h)

                    # Get direction property from object
                    props = {}
                    for p in obj.get("properties", []):
                        props[p["name"]] = p["value"]

                    direction = int(props.get("direction", -1))  # 0,1,2,3

                    self.ledges.append({
                        "rect": pygame.Rect(x, y, w, h),
                        "dir": direction
                    })

        # -------------------------------
        # LIGHT OBJECTS
        # -------------------------------
        self.lights = []
        for layer in self.data.get("layers", []):
            if layer.get("type") == "objectgroup" and layer.get("name", "").lower() == "lights":
                for obj in layer.get("objects", []):
                    x = obj["x"]
                    y = obj["y"]
                    w = obj["width"]
                    h = obj["height"]
                    r = int(max(w, h) * 0.8)
                    self.lights.append((x, y, w, h, r))

    # --------------------------------------------------------
    # DRAW ONE LAYER
    # --------------------------------------------------------
    def draw_layer(self, surface, camera, layer_name, offset_x=0, offset_y=0):
        idx = self.layer_map.get(layer_name.lower())
        if idx is None:
            return

        layer = self.layers[idx]
        data = layer.get("data", [])

        for i, gid in enumerate(data):
            if gid == 0:
                continue

            tile = self.tiles.get(gid)
            if tile is None:
                continue

            x = (i % self.width) * self.tile_w + offset_x
            y = (i // self.width) * self.tile_h + offset_y

            dest = camera.apply(pygame.Rect(x, y, self.tile_w, self.tile_h))
            surface.blit(tile, dest.topleft)
