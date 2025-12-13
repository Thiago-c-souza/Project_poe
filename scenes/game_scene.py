"""Cena principal com mapa de tiles e colisão básica."""

from __future__ import annotations

import pygame

from core.camera import Camera
from core.scene import Scene
from systems.collision import move_with_collisions

TILE_SIZE = 48
PLAYER_SIZE = 32
PLAYER_COLOR = (230, 230, 120)
FLOOR_COLOR = (40, 45, 60)
WALL_COLOR = (90, 110, 145)
BACKGROUND_COLOR = (20, 20, 30)

TILEMAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]


class GameScene(Scene):
    """Mapeia um tilemap simples e impede o player de atravessar paredes."""

    def __init__(self, game: "Game") -> None:
        super().__init__(game)
        self.speed = 200
        self.player_rect = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
        self.player_rect.center = self._find_spawn_point()
        self.camera = Camera(game.size)
        self.wall_rects = self._build_walls()

    def enter(self) -> None:
        self.camera.follow(self.player_rect.center)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.running = False

    def update(self, delta_time: float) -> None:
        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            direction.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            direction.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            direction.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            direction.x += 1

        if direction.length_squared() > 0:
            direction = direction.normalize()

        movement = direction * self.speed * delta_time
        self.player_rect = move_with_collisions(
            self.player_rect, movement, self.wall_rects
        )
        self.camera.follow(self.player_rect.center)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BACKGROUND_COLOR)

        for y, row in enumerate(TILEMAP):
            for x, tile in enumerate(row):
                world_rect = pygame.Rect(
                    x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE
                )
                screen_rect = self.camera.apply(world_rect)
                color = WALL_COLOR if tile == 1 else FLOOR_COLOR
                pygame.draw.rect(surface, color, screen_rect)

        player_rect = self.camera.apply(self.player_rect)
        pygame.draw.rect(surface, PLAYER_COLOR, player_rect)

    def _build_walls(self) -> list[pygame.Rect]:
        walls: list[pygame.Rect] = []
        for y, row in enumerate(TILEMAP):
            for x, tile in enumerate(row):
                if tile == 1:
                    walls.append(
                        pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    )
        return walls

    def _find_spawn_point(self) -> tuple[int, int]:
        for y, row in enumerate(TILEMAP):
            for x, tile in enumerate(row):
                if tile == 0:
                    return (
                        x * TILE_SIZE + TILE_SIZE // 2,
                        y * TILE_SIZE + TILE_SIZE // 2,
                    )
        return (TILE_SIZE, TILE_SIZE)

