# camera.py
class Camera:
    def __init__(self, width, height):
        self.w = width
        self.h = height
        self.x = 0
        self.y = 0

    def update(self, target_rect, map_pixel_w, map_pixel_h):
        # center camera on target rect center
        self.x = target_rect.centerx - self.w // 2
        self.y = target_rect.centery - self.h // 2

        # clamp to map bounds
        self.x = max(0, min(self.x, map_pixel_w - self.w))
        self.y = max(0, min(self.y, map_pixel_h - self.h))

    def apply(self, rect):
        # shift a pygame.Rect or (x,y) tuple
        if hasattr(rect, "topleft"):
            return rect.move(-self.x, -self.y)
        else:
            x, y = rect
            return x - self.x, y - self.y
