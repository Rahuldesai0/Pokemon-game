# tilemap.py
import pygame
import json
import os
from typing import Dict
from settings import TILESIZE, TILESET_FOLDER
from utils import resource_path

class TileMap:
    """
    Loads a Tiled JSON map that can reference multiple tileset images located under TILESET_FOLDER.
    Exposes:
      - width (tiles), height (tiles)
      - tile_w, tile_h (pixels)
      - pixel_width, pixel_height
      - tiles : dict gid -> Surface
      - layers : list of layer dicts (as in Tiled JSON)
      - collisions : list of pygame.Rect (from walls layer, index inferred by name)
    """

    def __init__(self, map_json_path: str):
        map_path = resource_path(map_json_path)
        with open(map_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

        self.width = self.data["width"]
        self.height = self.data["height"]
        # map tile size from file (override default TILESIZE)
        self.tile_w = self.data.get("tilewidth", TILESIZE)
        self.tile_h = self.data.get("tileheight", TILESIZE)
        self.pixel_width = self.width * self.tile_w
        self.pixel_height = self.height * self.tile_h

        # Load all tilesets referenced in JSON (assumes image paths are filenames relative to TILESET_FOLDER)
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

        # Store layers array for drawing; Tiled uses order in file
        self.layers = [layer for layer in self.data.get("layers", []) if layer.get("type") == "tilelayer"]

        # find layers by name (case-insensitive)
        self.layer_map = {}
        for i, layer in enumerate(self.layers):
            name = layer.get("name", "").lower()
            self.layer_map[name] = i

        # Build collision rects from 'walls' layer (layer 2)
        self.collisions = []
        walls_index = self.layer_map.get("walls")  # name must be "walls"
        if walls_index is not None:
            walls_layer = self.layers[walls_index]
            arr = walls_layer.get("data", [])
            for i, gid in enumerate(arr):
                if gid == 0:
                    continue
                tx = (i % self.width) * self.tile_w
                ty = (i // self.width) * self.tile_h
                self.collisions.append(pygame.Rect(tx, ty, self.tile_w, self.tile_h))

        # --- Load light positions from object layer ---
        self.lights = []
        for layer in self.data["layers"]:
            if layer["type"] == "objectgroup" and layer["name"].lower() == "lights":
                for obj in layer["objects"]:
                    x = obj["x"]
                    y = obj["y"]  # Tiled tile-object bottom alignment
                    w = obj["width"]
                    h = obj["height"]
                    r = int(max(w, h) * 0.8)
                    self.lights.append((x, y, w, h, r))



    def draw_layer(self, surface: pygame.Surface, camera, layer_name: str):
        """
        Draw a specific named layer (floor / walls / above).
        camera.apply accepts pygame.Rect or (x,y).
        """
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
            x = (i % self.width) * self.tile_w
            y = (i // self.width) * self.tile_h
            # camera.apply can accept a rect to return shifted rect
            dest = camera.apply(pygame.Rect(x, y, self.tile_w, self.tile_h))
            surface.blit(tile, dest.topleft)
