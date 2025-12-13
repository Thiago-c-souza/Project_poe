"""Implementação simples de câmera 2D que segue um alvo."""

from __future__ import annotations

import pygame


class Camera:
    """Mantém um offset para renderizar mundo relativo à tela."""

    def __init__(self, viewport_size: tuple[int, int]) -> None:
        self.viewport = pygame.Vector2(viewport_size)
        self.position = pygame.Vector2(0, 0)

    def follow(self, target_center: tuple[float, float]) -> None:
        """Centraliza a câmera no ``target_center``."""

        target = pygame.Vector2(target_center)
        self.position = target - self.viewport / 2

    def apply(self, rect: pygame.Rect) -> pygame.Rect:
        """Retorna um novo ``Rect`` ajustado pelo offset da câmera."""

        return rect.move(-int(self.position.x), -int(self.position.y))

