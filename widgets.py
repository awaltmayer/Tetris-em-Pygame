import pygame
import time 
import config

class TextInputBox:
    def __init__(self, x, y, w, h, font, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = config.COR_INPUT_BORDA_INATIVA
        self.color_active = config.COR_INPUT_BORDA_ATIVA
        self.color = self.color_inactive
        self.text = text
        self.font = font
        self.txt_surface = self.font.render(text, True, config.COR_INPUT_TEXTO)
        self.active = False
        self.prompt_text = "Digite seu Nickname"
        self.prompt_surface = self.font.render(self.prompt_text, True, config.COR_INPUT_PROMPT)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                    self.color = self.color_inactive
                    return "enter"
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, config.COR_INPUT_TEXTO)
        return None

    def draw(self, screen):
        pygame.draw.rect(screen, config.COR_INPUT_FUNDO, self.rect, 0, 5)
        pygame.draw.rect(screen, self.color, self.rect, 2, 5)

        if not self.text and not self.active:
            screen.blit(self.prompt_surface, (self.rect.x + 10, self.rect.y + 10))
        else:
            screen.blit(self.txt_surface, (self.rect.x + 10, self.rect.y + 10))

        if self.active:
            if (time.time() * 2) % 2 < 1:
                cursor_x = self.rect.x + 10 + self.txt_surface.get_width()
                cursor_rect = pygame.Rect(cursor_x, self.rect.y + 10, 2, self.txt_surface.get_height())
                pygame.draw.rect(screen, config.COR_INPUT_TEXTO, cursor_rect)