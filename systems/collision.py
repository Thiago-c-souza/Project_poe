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


def soft_separate(
    rect_a: pygame.Rect, rect_b: pygame.Rect, colliders: list[pygame.Rect]
) -> tuple[pygame.Rect, pygame.Rect]:
    """Empurra dois ``pygame.Rect`` sobrepostos no eixo de menor invasão.

    A função calcula o retângulo de interseção (overlap) e aplica um deslocamento
    apenas no eixo com menor sobreposição. Cada parte recebe metade do empurrão,
    o que evita teleporte e reduz tremedeira.
    """

    if not rect_a.colliderect(rect_b):
        return rect_a, rect_b

    overlap = rect_a.clip(rect_b)
    if overlap.width == 0 or overlap.height == 0:
        return rect_a, rect_b

    push_x_smaller = overlap.width < overlap.height
    if push_x_smaller:
        direction_sign = 1 if rect_a.centerx >= rect_b.centerx else -1
        push_vector = pygame.Vector2(direction_sign * (overlap.width / 2 + 0.5), 0)
    else:
        direction_sign = 1 if rect_a.centery >= rect_b.centery else -1
        push_vector = pygame.Vector2(0, direction_sign * (overlap.height / 2 + 0.5))

    resolved_a = move_with_collisions(rect_a, push_vector, colliders)
    resolved_b = move_with_collisions(rect_b, -push_vector, colliders)

    return resolved_a, resolved_b

