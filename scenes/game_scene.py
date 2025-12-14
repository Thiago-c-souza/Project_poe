"""Cena principal com mapa de tiles e colisão básica."""

from __future__ import annotations

import json
import random
from pathlib import Path

import pygame

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
        self.classes = self._load_classes()
        self.selected_class = self._default_class_name()
        spawn_point = self._find_spawn_point()
        self.player = self._create_player(spawn_point, self.selected_class)
        self.camera = Camera(game.size)
        self.wall_rects = self._build_walls()
        self.enemies = self._spawn_enemies()
        self.pickups: list[LootPickup] = []
        self.attack_requested = False
        self.coins_collected = 0
        self.items_collected = 0
        self.font = pygame.font.SysFont(None, 22)

    def enter(self) -> None:
        self.camera.follow(self.player.rect.center)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.running = False
            elif event.key == pygame.K_SPACE:
                self.attack_requested = True

            class_name = self._class_name_from_key(event.key)
            if class_name:
                self._set_player_class(class_name)

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

        if self.attack_requested and self.player.can_attack():
            self._perform_attack()
        self.attack_requested = False

        self.player.update(direction, delta_time, self.wall_rects)
        for enemy in self.enemies:
            enemy.update(delta_time, self.player.rect.center, self.wall_rects)
        self._check_player_damage()
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

    def _perform_attack(self) -> None:
        """Executa o ataque do jogador e processa inimigos derrotados."""

        attack_result = self.player.attack(self.enemies)
        if not attack_result:
            return

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
            f"Classe: {self.selected_class}",
            f"Vida: {int(self.player.hp)}/{int(self.player.max_hp)}",
            f"Mana: {int(self.player.mana)}/{int(self.player.max_mana)}",
            f"Moedas: {self.coins_collected}",
            f"Itens: {self.items_collected}",
        ]
        for i, text in enumerate(hud_lines):
            rendered = self.font.render(text, True, (230, 230, 230))
            surface.blit(rendered, (12, 12 + i * 22))

    def _load_classes(self) -> dict[str, dict[str, float | str]]:
        classes_path = Path(__file__).resolve().parent.parent / "data" / "classes.json"
        with classes_path.open(encoding="utf-8") as file:
            class_data = json.load(file)

        if not class_data:
            raise ValueError("Nenhuma classe configurada encontrada em classes.json")
        return class_data

    def _default_class_name(self) -> str:
        if "warrior" in self.classes:
            return "warrior"
        return next(iter(self.classes))

    def _create_player(self, spawn_pos: tuple[int, int], class_name: str) -> Player:
        stats = self.classes.get(class_name)
        if stats is None:
            raise ValueError(f"Classe '{class_name}' não encontrada na configuração")

        return Player(
            spawn_pos,
            size=PLAYER_SIZE,
            speed=float(stats.get("speed", 200)),
            max_hp=float(stats.get("hp", 100)),
            max_mana=float(stats.get("mana", 100)),
            attack_damage=float(stats.get("damage", 12)),
            skill=stats.get("skill"),
        )

    def _class_name_from_key(self, key: int) -> str | None:
        available_classes = list(self.classes.keys())
        hotkeys = {
            pygame.K_1: available_classes[0] if len(available_classes) > 0 else None,
            pygame.K_2: available_classes[1] if len(available_classes) > 1 else None,
            pygame.K_3: available_classes[2] if len(available_classes) > 2 else None,
        }
        return hotkeys.get(key)

    def _set_player_class(self, class_name: str) -> None:
        if class_name not in self.classes or class_name == self.selected_class:
            return

        current_position = self.player.rect.center
        self.selected_class = class_name
        self.player = self._create_player(current_position, class_name)
        self.camera.follow(self.player.rect.center)

    def _check_player_damage(self) -> None:
        """Aplica dano por contato dos inimigos, respeitando i-frames."""

        if not self.player.alive:
            return

        for enemy in self.enemies:
            if enemy.alive and enemy.rect.colliderect(self.player.rect):
                if self.player.take_damage(enemy.contact_damage):
                    break

