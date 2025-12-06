# virtual_controls.py
import pygame

class VirtualControls:
    def __init__(self):
        # True/False actions, matching keyboard movement/actions
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

        # Button rectangles (screen positions)
        self.btn_up    = pygame.Rect(60, 520, 60, 60)
        self.btn_down  = pygame.Rect(60, 620, 60, 60)
        self.btn_left  = pygame.Rect(0, 570, 60, 60)
        self.btn_right = pygame.Rect(120, 570, 60, 60)

        self.btn_A = pygame.Rect(1100, 580, 80, 80)
        self.btn_B = pygame.Rect(1000, 630, 70, 70)

        self.btn_start  = pygame.Rect(600, 680, 60, 30)
        self.btn_select = pygame.Rect(530, 680, 60, 30)

    def update(self, events):
        # Reset each frame
        for k in self.actions:
            self.actions[k] = False

        mouse = pygame.mouse.get_pos()
        pressed = pygame.mouse.get_pressed()[0]

        if pressed:
            if self.btn_up.collidepoint(mouse):
                self.actions["up"] = True
            if self.btn_down.collidepoint(mouse):
                self.actions["down"] = True
            if self.btn_left.collidepoint(mouse):
                self.actions["left"] = True
            if self.btn_right.collidepoint(mouse):
                self.actions["right"] = True

            if self.btn_A.collidepoint(mouse):
                self.actions["A"] = True
            if self.btn_B.collidepoint(mouse):
                self.actions["B"] = True

            if self.btn_start.collidepoint(mouse):
                self.actions["start"] = True
            if self.btn_select.collidepoint(mouse):
                self.actions["select"] = True

    def draw(self, surf):
        # Semi-transparent alpha
        SEMI = 160

        # Helper for pill buttons (Start/Select)
        def draw_pill(rect, color):
            pill = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(pill, color, (0, 0, rect.width, rect.height), border_radius=14)
            surf.blit(pill, rect.topleft)

        # --------------------------
        # D-PAD (Up / Down / Left / Right)
        # --------------------------
        arrow_color = (20, 20, 20)

        # Common background style
        def draw_dpad_button(rect):
            s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(s, (255, 255, 255, SEMI), (0, 0, rect.width, rect.height), border_radius=12)
            surf.blit(s, rect.topleft)

        # Draw shapes
        draw_dpad_button(self.btn_up)
        draw_dpad_button(self.btn_down)
        draw_dpad_button(self.btn_left)
        draw_dpad_button(self.btn_right)

        # Draw arrows
        # Up
        pygame.draw.polygon(
            surf, arrow_color,
            [(self.btn_up.centerx, self.btn_up.y + 10),
             (self.btn_up.centerx - 15, self.btn_up.y + 40),
             (self.btn_up.centerx + 15, self.btn_up.y + 40)]
        )
        # Down
        pygame.draw.polygon(
            surf, arrow_color,
            [(self.btn_down.centerx, self.btn_down.bottom - 10),
             (self.btn_down.centerx - 15, self.btn_down.bottom - 40),
             (self.btn_down.centerx + 15, self.btn_down.bottom - 40)]
        )
        # Left
        pygame.draw.polygon(
            surf, arrow_color,
            [(self.btn_left.x + 10, self.btn_left.centery),
             (self.btn_left.x + 40, self.btn_left.centery - 15),
             (self.btn_left.x + 40, self.btn_left.centery + 15)]
        )
        # Right
        pygame.draw.polygon(
            surf, arrow_color,
            [(self.btn_right.right - 10, self.btn_right.centery),
             (self.btn_right.right - 40, self.btn_right.centery - 15),
             (self.btn_right.right - 40, self.btn_right.centery + 15)]
        )

        # --------------------------
        # A & B Buttons (Circles)
        # --------------------------
        font = pygame.font.SysFont("Arial", 28, bold=True)

        # A
        A_surf = pygame.Surface((self.btn_A.width, self.btn_A.height), pygame.SRCALPHA)
        pygame.draw.circle(A_surf, (255, 255, 255, SEMI),
                           (self.btn_A.width//2, self.btn_A.height//2), self.btn_A.width//2)
        surf.blit(A_surf, self.btn_A.topleft)

        textA = font.render("A", True, (30, 30, 30))
        surf.blit(textA, (self.btn_A.centerx - textA.get_width()//2,
                          self.btn_A.centery - textA.get_height()//2))

        # B
        B_surf = pygame.Surface((self.btn_B.width, self.btn_B.height), pygame.SRCALPHA)
        pygame.draw.circle(B_surf, (255, 255, 255, SEMI),
                           (self.btn_B.width//2, self.btn_B.height//2), self.btn_B.width//2)
        surf.blit(B_surf, self.btn_B.topleft)

        textB = font.render("B", True, (30, 30, 30))
        surf.blit(textB, (self.btn_B.centerx - textB.get_width()//2,
                          self.btn_B.centery - textB.get_height()//2))

        # --------------------------
        # START & SELECT (pill-shaped)
        # --------------------------
        small_font = pygame.font.SysFont("Arial", 18, bold=True)

        draw_pill(self.btn_start, (255, 255, 255, SEMI))
        textStart = small_font.render("START", True, (30, 30, 30))
        surf.blit(textStart, (self.btn_start.centerx - textStart.get_width()//2,
                              self.btn_start.centery - textStart.get_height()//2))

        draw_pill(self.btn_select, (255, 255, 255, SEMI))
        textSelect = small_font.render("SELECT", True, (30, 30, 30))
        surf.blit(textSelect, (self.btn_select.centerx - textSelect.get_width()//2,
                               self.btn_select.centery - textSelect.get_height()//2))

