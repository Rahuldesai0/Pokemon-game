import pygame

class VirtualControls:
    def __init__(self):
        self.actions = {
            "up": False,
            "down": False,
            "left": False,
            "right": False,
            "A": False,
            "B": False,
            "start": False,
            "select": False
        }

        # previous frame (for edge detection)
        self.prev_actions = self.actions.copy()

        # just pressed (edge)
        self.just_pressed = {k: False for k in self.actions}

    def update(self, events, win_size):
        """
        Update keyboard + virtual buttons
        """
        # save previous state
        self.prev_actions = self.actions.copy()

        # reset
        for key in self.actions:
            self.actions[key] = False

        # ---------------------------
        # KEYBOARD INPUT (IMPORTANT)
        # ---------------------------
        keys = pygame.key.get_pressed()

        self.actions["up"]    |= keys[pygame.K_UP] or keys[pygame.K_w]
        self.actions["down"]  |= keys[pygame.K_DOWN] or keys[pygame.K_s]
        self.actions["left"]  |= keys[pygame.K_LEFT] or keys[pygame.K_a]
        self.actions["right"] |= keys[pygame.K_RIGHT] or keys[pygame.K_d]

        self.actions["A"] |= (
            keys[pygame.K_e] or
            keys[pygame.K_RETURN] or
            keys[pygame.K_KP_ENTER]
        )

        self.actions["B"] |= keys[pygame.K_SPACE] or keys[pygame.K_LSHIFT]

        # ---------------------------
        # VIRTUAL BUTTONS (MOUSE)
        # ---------------------------
        mouse = pygame.mouse.get_pos()
        pressed = pygame.mouse.get_pressed()[0]

        buttons = self.get_buttons(win_size)

        if pressed:
            for key, rect in buttons.items():
                if rect.collidepoint(mouse):
                    self.actions[key] = True

        # ---------------------------
        # EDGE DETECTION
        # ---------------------------
        for key in self.actions:
            self.just_pressed[key] = (
                self.actions[key] and not self.prev_actions[key]
            )

    # ------------------------------------------------------------------

    def get_buttons(self, win_size):
        w, h = win_size

        size = int(min(w, h) * 0.08)
        margin = int(size * 0.3)

        up = pygame.Rect(margin + size, h - 3*size - 2*margin, size, size)
        down = pygame.Rect(margin + size, h - size - margin, size, size)
        left = pygame.Rect(margin, h - 2*size - margin, size, size)
        right = pygame.Rect(2*size + 2*margin, h - 2*size - margin, size, size)

        a_size = int(size * 1.2)
        a = pygame.Rect(w - 2*a_size - 2*margin, h - 2*a_size - margin, a_size, a_size)
        b = pygame.Rect(w - a_size - margin, h - a_size - 2*margin, a_size, a_size)

        s_w, s_h = int(a_size*1.2), int(a_size*0.6)
        start = pygame.Rect(w//2 + margin, h - s_h - margin, s_w, s_h)
        select = pygame.Rect(w//2 - s_w - margin, h - s_h - margin, s_w, s_h)

        return {
            "up": up, "down": down, "left": left, "right": right,
            "A": a, "B": b, "start": start, "select": select
        }

    # ------------------------------------------------------------------
    def draw(self, surf):
        w, h = surf.get_size()
        buttons = self.get_buttons((w, h))

        # Colors
        DEFAULT_COLOR = (200,200,200)
        PRESSED_COLOR = (80,80,80)
        TEXT_COLOR = (30,30,30)
        TEXT_PRESSED = (255,255,255)
        ARROW_COLOR = (20,20,20)

        # Draw D-pad
        for key in ["up","down","left","right"]:
            rect = buttons[key]
            pressed = self.actions[key]
            color = PRESSED_COLOR if pressed else DEFAULT_COLOR
            pygame.draw.rect(surf, color, rect, border_radius=max(2,int(rect.width*0.2)))

        # Draw arrows on D-pad
        for key in ["up","down","left","right"]:
            rect = buttons[key]
            if key == "up":
                pts = [(rect.centerx, rect.top + rect.height*0.2),
                       (rect.centerx - rect.width*0.3, rect.bottom - rect.height*0.2),
                       (rect.centerx + rect.width*0.3, rect.bottom - rect.height*0.2)]
            elif key == "down":
                pts = [(rect.centerx, rect.bottom - rect.height*0.2),
                       (rect.centerx - rect.width*0.3, rect.top + rect.height*0.2),
                       (rect.centerx + rect.width*0.3, rect.top + rect.height*0.2)]
            elif key == "left":
                pts = [(rect.left + rect.width*0.2, rect.centery),
                       (rect.right - rect.width*0.2, rect.centery - rect.height*0.3),
                       (rect.right - rect.width*0.2, rect.centery + rect.height*0.3)]
            elif key == "right":
                pts = [(rect.right - rect.width*0.2, rect.centery),
                       (rect.left + rect.width*0.2, rect.centery - rect.height*0.3),
                       (rect.left + rect.width*0.2, rect.centery + rect.height*0.3)]
            pygame.draw.polygon(surf, ARROW_COLOR, pts)

        # Draw A & B
        font = pygame.font.SysFont("Arial", max(10,int(w*0.03)), bold=True)
        for key in ["A","B"]:
            rect = buttons[key]
            pressed = self.actions[key]
            color = PRESSED_COLOR if pressed else DEFAULT_COLOR
            text_color = TEXT_PRESSED if pressed else TEXT_COLOR
            pygame.draw.circle(surf, color, rect.center, rect.width//2)
            text_surf = font.render(key, True, text_color)
            surf.blit(text_surf, (rect.centerx - text_surf.get_width()//2,
                                   rect.centery - text_surf.get_height()//2))

        # Start & Select
        small_font = pygame.font.SysFont("Arial", max(8,int(w*0.02)), bold=True)
        for key,label in [("start","START"),("select","SELECT")]:
            rect = buttons[key]
            pressed = self.actions[key]
            color = PRESSED_COLOR if pressed else DEFAULT_COLOR
            pygame.draw.rect(surf, color, rect, border_radius=max(2,int(rect.width*0.2)))
            text_surf = small_font.render(label, True, TEXT_PRESSED if pressed else TEXT_COLOR)
            surf.blit(text_surf, (rect.centerx - text_surf.get_width()//2,
                                   rect.centery - text_surf.get_height()//2))

