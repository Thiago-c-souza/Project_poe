"""Utilitários para resolução de colisão AABB."""

from __future__ import annotations

import pygame


def move_with_collisions(
    rect: pygame.Rect, movement: pygame.Vector2, colliders: list[pygame.Rect]
) -> pygame.Rect:
    """Move o ``rect`` considerando colisores AABB.

    O movimento é resolvido por eixo (primeiro X depois Y) para evitar que o
    retângulo atravesse paredes quando se move na diagonal.
    """

    resolved = rect.copy()
    step_x = int(round(movement.x))
    step_y = int(round(movement.y))

    if step_x:
        resolved.x += step_x
        for collider in colliders:
            if resolved.colliderect(collider):
                if step_x > 0:
                    resolved.right = collider.left
                else:
                    resolved.left = collider.right

    if step_y:
        resolved.y += step_y
        for collider in colliders:
            if resolved.colliderect(collider):
                if step_y > 0:
                    resolved.bottom = collider.top
                else:
                    resolved.top = collider.bottom

    return resolved

