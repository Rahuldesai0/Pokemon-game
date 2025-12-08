# virtual_controls.py
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

        # Touch-button rectangles
        self.buttons = {
            "up": pygame.Rect(60, 520, 60, 60),
            "down": pygame.Rect(60, 620, 60, 60),
            "left": pygame.Rect(0, 570, 60, 60),
            "right": pygame.Rect(120, 570, 60, 60),
            "A": pygame.Rect(1100, 580, 80, 80),
            "B": pygame.Rect(1000, 630, 70, 70),
            "start": pygame.Rect(600, 680, 60, 30),
            "select": pygame.Rect(530, 680, 60, 30)
        }

    def update(self, events):
        mouse = pygame.mouse.get_pos()
        pressed = pygame.mouse.get_pressed()[0]

        # Reset clean each frame (fixes sticky-touch bug)
        for name in self.actions:
            self.actions[name] = False

        # Touch press → button active
        if pressed:
            for name, rect in self.buttons.items():
                if rect.collidepoint(mouse):
                    self.actions[name] = True

    def draw(self, surf):
        SEMI = 160
        OPAQUE = 255

        DEFAULT_COLOR = (200, 200, 200)
        PRESSED_COLOR = (80, 80, 80)
        DEFAULT_TEXT = (30, 30, 30)
        PRESSED_TEXT = (255, 255, 255)
        arrow_color = (20, 20, 20)

        def draw_pill(rect, pressed=False):
            color = PRESSED_COLOR if pressed else DEFAULT_COLOR
            alpha = OPAQUE if pressed else SEMI
            pill = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(pill, (*color, alpha), (0, 0, rect.width, rect.height), border_radius=14)
            surf.blit(pill, rect.topleft)

        def draw_dpad_button(rect, pressed=False):
            color = PRESSED_COLOR if pressed else DEFAULT_COLOR
            alpha = OPAQUE if pressed else SEMI
            s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(s, (*color, alpha), (0, 0, rect.width, rect.height), border_radius=12)
            surf.blit(s, rect.topleft)

        # D-pad
        BTN = self.buttons
        draw_dpad_button(BTN["up"], self.actions["up"])
        draw_dpad_button(BTN["down"], self.actions["down"])
        draw_dpad_button(BTN["left"], self.actions["left"])
        draw_dpad_button(BTN["right"], self.actions["right"])

        # Arrows
        pygame.draw.polygon(surf, arrow_color, [
            (BTN["up"].centerx, BTN["up"].y + 10),
            (BTN["up"].centerx - 15, BTN["up"].y + 40),
            (BTN["up"].centerx + 15, BTN["up"].y + 40)
        ])
        pygame.draw.polygon(surf, arrow_color, [
            (BTN["down"].centerx, BTN["down"].bottom - 10),
            (BTN["down"].centerx - 15, BTN["down"].bottom - 40),
            (BTN["down"].centerx + 15, BTN["down"].bottom - 40)
        ])
        pygame.draw.polygon(surf, arrow_color, [
            (BTN["left"].x + 10, BTN["left"].centery),
            (BTN["left"].x + 40, BTN["left"].centery - 15),
            (BTN["left"].x + 40, BTN["left"].centery + 15)
        ])
        pygame.draw.polygon(surf, arrow_color, [
            (BTN["right"].right - 10, BTN["right"].centery),
            (BTN["right"].right - 40, BTN["right"].centery - 15),
            (BTN["right"].right - 40, BTN["right"].centery + 15)
        ])

        # A & B buttons
        font = pygame.font.SysFont("Arial", 28, bold=True)
        for action in ["A", "B"]:
            btn = BTN[action]
            pressed = self.actions[action]
            color = PRESSED_COLOR if pressed else DEFAULT_COLOR
            text_color = PRESSED_TEXT if pressed else DEFAULT_TEXT

            s = pygame.Surface((btn.width, btn.height), pygame.SRCALPHA)
            pygame.draw.circle(
                s,
                (*color, OPAQUE if pressed else SEMI),
                (btn.width // 2, btn.height // 2),
                btn.width // 2
            )
            surf.blit(s, btn.topleft)

            surf.blit(font.render(action, True, text_color),
                (btn.centerx - font.size(action)[0]//2,
                 btn.centery - font.size(action)[1]//2))

        # Start & Select
        small_font = pygame.font.SysFont("Arial", 18, bold=True)
        for key, label in [("start", "START"), ("select", "SELECT")]:
            draw_pill(BTN[key], self.actions[key])
            txt_color = PRESSED_TEXT if self.actions[key] else DEFAULT_TEXT
            surf.blit(
                small_font.render(label, True, txt_color),
                (BTN[key].centerx - small_font.size(label)[0]//2,
                 BTN[key].centery - small_font.size(label)[1]//2)
            )
