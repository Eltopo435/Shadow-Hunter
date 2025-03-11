# Sergio Gabriel Pérez A.
# 23-EISN-2-028

import pygame

class Popup:
    def __init__(self, message, duration, font, pos):
        self.message = message
        self.duration = duration  # en frames
        self.remaining = duration
        self.font = font
        self.pos = pos  # posición en pantalla

    def update(self):
        if self.remaining > 0:
            self.remaining -= 1

    def render(self, surface):
        # Calcular opacidad basada en el tiempo restante
        alpha = int(255 * (self.remaining / self.duration))
        text_surf = self.font.render(self.message, True, (255, 255, 255))
        text_surf.set_alpha(alpha)
        # Fondo semi-transparente para el popup
        bg_surf = pygame.Surface(
            (text_surf.get_width()+20, text_surf.get_height()+10), pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, int(alpha*0.6)))
        # Dibujar fondo y texto en la posición especificada
        bg_rect = bg_surf.get_rect(center=self.pos)
        text_rect = text_surf.get_rect(center=self.pos)
        surface.blit(bg_surf, bg_rect)
        surface.blit(text_surf, text_rect)
