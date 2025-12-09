# camera.py
class Camera:
    def __init__(self, width, height):
        self.w = width
        self.h = height
        self.x = 0
        self.y = 0

    # ---------------------------------------------------------
    # Supports BOTH old mode:  update(target, map_w, map_h)
    #        AND new mode:     update(target, world_x, world_y, world_w, world_h)
    # ---------------------------------------------------------
    def update(self, target_rect, *bounds):
        if len(bounds) == 2:
            # --- OLD MODE (single map) ---
            map_pixel_w, map_pixel_h = bounds
            world_x = 0
            world_y = 0
            world_w = map_pixel_w
            world_h = map_pixel_h

        elif len(bounds) == 4:
            # --- WORLD MODE (multi-map) ---
            world_x, world_y, world_w, world_h = bounds

        else:
            raise ValueError("Camera.update expected 2 or 4 boundary arguments.")

        # ---------------------------------------------------------
        # Center camera on player
        # ---------------------------------------------------------
        cx = target_rect.centerx
        cy = target_rect.centery

        self.x = cx - self.w // 2
        self.y = cy - self.h // 2

        # ---------------------------------------------------------
        # Clamp inside world bounds
        # ---------------------------------------------------------
        if self.x < world_x:
            self.x = world_x
        if self.y < world_y:
            self.y = world_y

        if self.x + self.w > world_x + world_w:
            self.x = world_x + world_w - self.w
        if self.y + self.h > world_y + world_h:
            self.y = world_y + world_h - self.h

    # ---------------------------------------------------------
    # Shift rectangles based on camera offset
    # ---------------------------------------------------------
    def apply(self, rect):
        if hasattr(rect, "topleft"):
            return rect.move(-self.x, -self.y)
        else:
            x, y = rect
            return x - self.x, y - self.y
