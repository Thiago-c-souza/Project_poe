"""Itens simples que podem ser coletados após derrotar inimigos."""
from __future__ import annotations

import pygame

COIN_COLOR = (230, 210, 80)
ITEM_COLOR = (120, 200, 220)
OUTLINE_COLOR = (25, 20, 20)


class LootPickup:
    """Pequeno item estático que o player pode coletar."""

    def __init__(self, position: tuple[int, int], kind: str) -> None:
        self.kind = kind
        size = 18 if kind == "coin" else 22
        self.rect = pygame.Rect(0, 0, size, size)
        self.rect.center = position

    def draw(self, surface: pygame.Surface, camera_apply) -> None:
        """Desenha o item no chão com uma borda simples."""

        screen_rect = camera_apply(self.rect)
        color = COIN_COLOR if self.kind == "coin" else ITEM_COLOR
        pygame.draw.rect(surface, color, screen_rect)
        pygame.draw.rect(surface, OUTLINE_COLOR, screen_rect, width=2)
