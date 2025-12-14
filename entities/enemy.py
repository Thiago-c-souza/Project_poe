"""Entidade simples de inimigo com IA de perseguição."""
from __future__ import annotations

import pygame

from systems.collision import move_with_collisions

ENEMY_COLOR = (200, 90, 90)
ENEMY_DEAD_COLOR = (80, 60, 60)


class Enemy:
    """Inimigo básico que busca o player e pode morrer ao receber dano."""

    def __init__(
        self,
        spawn_pos: tuple[int, int],
        size: int = 28,
        speed: float = 140.0,
        health: int = 30,
        contact_damage: float = 10.0,
    ) -> None:
        self.rect = pygame.Rect(0, 0, size, size)
        self.rect.center = spawn_pos
        self.speed = speed
        self.max_health = health
        self.health = float(health)
        self.alive = True
        self.contact_damage = contact_damage

    def update(
        self,
        delta_time: float,
        player_center: tuple[float, float],
        colliders: list[pygame.Rect],
    ) -> None:
        """Move em direção ao player enquanto estiver vivo."""

        if not self.alive:
            return

        direction = pygame.Vector2(player_center) - pygame.Vector2(self.rect.center)
        if direction.length_squared() == 0:
            return

        direction = direction.normalize()
        movement = direction * self.speed * delta_time
        self.rect = move_with_collisions(self.rect, movement, colliders)

    def take_damage(self, amount: float) -> None:
        """Reduz vida e marca como morto quando chega a 0."""

        if not self.alive:
            return

        self.health = max(0.0, self.health - amount)
        if self.health == 0:
            self.alive = False

    def draw(self, surface: pygame.Surface, camera_apply) -> None:
        """Desenha o inimigo com barra de vida simples."""

        screen_rect = camera_apply(self.rect)
        color = ENEMY_COLOR if self.alive else ENEMY_DEAD_COLOR
        pygame.draw.rect(surface, color, screen_rect)

        # Barra de vida acima da cabeça
        bar_width = screen_rect.width
        bar_height = 6
        bar_x = screen_rect.left
        bar_y = screen_rect.top - bar_height - 2
        outline_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(surface, (25, 20, 20), outline_rect)

        if self.max_health > 0:
            health_ratio = self.health / self.max_health
            inner_width = int(bar_width * health_ratio)
            inner_rect = pygame.Rect(bar_x, bar_y, inner_width, bar_height)
            pygame.draw.rect(surface, (150, 220, 120), inner_rect)

