"""Cena principal com mapa de tiles e colisão básica."""

from __future__ import annotations

import pygame
import random

from core.camera import Camera
from core.scene import Scene
from entities.enemy import Enemy
from entities.player import Player
from entities.pickup import LootPickup

TILE_SIZE = 48
PLAYER_SIZE = 32
PLAYER_COLOR = (230, 230, 120)
PLAYER_ATTACK_COLOR = (255, 200, 160)
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
        self.player = Player(self._find_spawn_point(), size=PLAYER_SIZE, speed=200)
        self.camera = Camera(game.size)
        self.wall_rects = self._build_walls()
        self.enemies = self._spawn_enemies()
        self.pickups: list[LootPickup] = []
        self.coins_collected = 0
        self.items_collected = 0
        self.font = pygame.font.SysFont(None, 22)

    def enter(self) -> None:
        self.camera.follow(self.player.rect.center)

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

        self.player.move(direction, delta_time, self.wall_rects)
        self._update_attack(delta_time)
        for enemy in self.enemies:
            enemy.update(delta_time, self.player.rect.center, self.wall_rects)
        self._check_pickup_collisions()
        self.camera.follow(self.player.rect.center)

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

        for pickup in self.pickups:
            pickup.draw(surface, self.camera.apply)

        player_rect = self.camera.apply(self.player.rect)
        pygame.draw.rect(surface, PLAYER_COLOR, player_rect)

        if self.player.last_attack_rect and self.player.attack_timer > 0:
            pygame.draw.rect(
                surface,
                PLAYER_ATTACK_COLOR,
                self.camera.apply(self.player.last_attack_rect),
                width=2,
            )

        for enemy in self.enemies:
            enemy.draw(surface, self.camera.apply)

        self._draw_hud(surface)

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

    def _spawn_enemies(self) -> list[Enemy]:
        """Cria inimigos em pontos pré-definidos do mapa."""

        spawn_tiles = [(15, 8), (9, 4)]
        enemies: list[Enemy] = []
        for x, y in spawn_tiles:
            center = (x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2)
            enemies.append(Enemy(center))
        return enemies

    def _update_attack(self, delta_time: float) -> None:
        """Processa input de ataque e delega dano ao jogador."""

        keys = pygame.key.get_pressed()
        self.player.update_timers(delta_time)

        if keys[pygame.K_SPACE]:
            attack_result = self.player.attack(self.enemies)
            if attack_result:
                _, defeated = attack_result
                for enemy in defeated:
                    self._spawn_loot(enemy.rect.center)
                    if enemy in self.enemies:
                        self.enemies.remove(enemy)

    def _spawn_loot(self, position: tuple[int, int]) -> None:
        """Sorteia um drop simples quando o inimigo morre."""

        loot_type = "coin" if random.random() < 0.6 else "item"
        self.pickups.append(LootPickup(position, loot_type))

    def _check_pickup_collisions(self) -> None:
        """Remove itens coletados e atualiza contadores."""

        for pickup in list(self.pickups):
            if self.player.rect.colliderect(pickup.rect):
                if pickup.kind == "coin":
                    self.coins_collected += 1
                else:
                    self.items_collected += 1
                self.pickups.remove(pickup)

    def _draw_hud(self, surface: pygame.Surface) -> None:
        """Exibe contadores simples de drops no canto superior esquerdo."""

        hud_lines = [
            f"Moedas: {self.coins_collected}",
            f"Itens: {self.items_collected}",
        ]
        for i, text in enumerate(hud_lines):
            rendered = self.font.render(text, True, (230, 230, 230))
            surface.blit(rendered, (12, 12 + i * 22))

