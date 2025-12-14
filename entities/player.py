"""Entidade do jogador, contendo atributos e lógica de ataque."""

from __future__ import annotations

import pygame

from systems.collision import move_with_collisions


class Player:
    """Representa o jogador com estado próprio e ações básicas."""

    def __init__(
        self,
        spawn_pos: tuple[int, int],
        size: int = 32,
        speed: float = 200.0,
        max_hp: float = 100.0,
        max_mana: float = 100.0,
        attack_damage: float = 12.0,
        skill: str | None = None,
    ) -> None:
        self.rect = pygame.Rect(0, 0, size, size)
        self.rect.center = spawn_pos
        self.vel = pygame.Vector2()
        self.speed = speed
        self.max_hp = max_hp
        self.hp = max_hp
        self.max_mana = max_mana
        self.mana = max_mana
        self.alive = True
        self.invulnerability_duration = 0.4
        self.invulnerability_timer = 0.0
        self.facing_direction = pygame.Vector2(1, 0)
        self.skill = skill

        self.attack_cooldown = 0.0
        self.attack_duration = 0.1
        self.attack_timer = 0.0
        self.attack_range = size + 24
        self.attack_damage = attack_damage
        self.last_attack_rect: pygame.Rect | None = None

    def move(
        self, direction: pygame.Vector2, delta_time: float, colliders: list[pygame.Rect]
    ) -> None:
        """Atualiza a posição com colisão e mantém direção/física básica."""

        if direction.length_squared() > 0:
            direction = direction.normalize()
            self.facing_direction = direction

        movement = direction * self.speed * delta_time
        self.vel = movement
        self.rect = move_with_collisions(self.rect, movement, colliders)

    def update(
        self, direction: pygame.Vector2, delta_time: float, colliders: list[pygame.Rect]
    ) -> None:
        """Move o jogador e avança temporizadores em um único passo."""

        if not self.alive:
            self.vel = pygame.Vector2()
            self.update_timers(delta_time)
            return

        self.move(direction, delta_time, colliders)
        self.update_timers(delta_time)

    def update_timers(self, delta_time: float) -> None:
        """Avança temporizadores relacionados ao ataque e invulnerabilidade."""

        self.attack_cooldown = max(0.0, self.attack_cooldown - delta_time)
        self.attack_timer = max(0.0, self.attack_timer - delta_time)
        self.invulnerability_timer = max(0.0, self.invulnerability_timer - delta_time)

    def can_attack(self) -> bool:
        """Indica se o ataque básico está pronto para uso."""

        return self.alive and self.attack_cooldown == 0

    def take_damage(self, amount: float) -> bool:
        """Aplica dano respeitando i-frames e retorna se o golpe foi aceito."""

        if not self.alive or self.invulnerability_timer > 0:
            return False

        self.hp = max(0.0, self.hp - amount)
        if self.hp == 0:
            self.alive = False

        self.invulnerability_timer = self.invulnerability_duration
        return True

    def is_invulnerable(self) -> bool:
        """Indica se o jogador está dentro da janela de invulnerabilidade."""

        return self.invulnerability_timer > 0

    def invulnerability_flash_on(self) -> bool:
        """Alterna o estado de flash para feedback visual durante i-frames."""

        if not self.is_invulnerable():
            return False

        flash_interval = 0.1
        return int(self.invulnerability_timer / flash_interval) % 2 == 0

    def attack(
        self, enemies: list["Enemy"], colliders: list[pygame.Rect]
    ) -> tuple[pygame.Rect, list["Enemy"]] | None:
        """Realiza o ataque na direção atual e aplica dano nos inimigos."""

        if self.attack_cooldown > 0:
            return None

        attack_rect = self._build_attack_rect()
        self.last_attack_rect = attack_rect
        self.attack_cooldown = 0.45
        self.attack_timer = self.attack_duration

        defeated: list["Enemy"] = []
        for enemy in list(enemies):
            if not attack_rect.colliderect(enemy.rect):
                continue

            alive_before = enemy.alive
            enemy.take_damage(self.attack_damage)
            self._push_enemy(enemy, colliders)

            if alive_before and not enemy.alive:
                defeated.append(enemy)

        return attack_rect, defeated

    def _push_enemy(self, enemy: "Enemy", colliders: list[pygame.Rect]) -> None:
        """Empurra o inimigo atingido e corrige contra paredes em seguida."""

        knockback_distance = 16
        direction = pygame.Vector2(enemy.rect.center) - pygame.Vector2(self.rect.center)
        if direction.length_squared() == 0:
            direction = self.facing_direction

        movement = direction.normalize() * knockback_distance
        enemy.rect = move_with_collisions(enemy.rect, movement, colliders)

    def _build_attack_rect(self) -> pygame.Rect:
        """Cria um retângulo de ataque na direção em que o player está olhando."""

        horizontal = abs(self.facing_direction.x) >= abs(self.facing_direction.y)
        size = self.rect.width

        if horizontal:
            attack_width = self.attack_range
            attack_height = size
            offset = (size // 2 + attack_width // 2)
            if self.facing_direction.x < 0:
                offset *= -1
            center = (self.rect.centerx + offset, self.rect.centery)
            attack_rect = pygame.Rect(0, 0, attack_width, attack_height)
            attack_rect.center = center
            return attack_rect

        attack_width = size
        attack_height = self.attack_range
        offset = (size // 2 + attack_height // 2)
        if self.facing_direction.y < 0:
            offset *= -1
        center = (self.rect.centerx, self.rect.centery + offset)
        attack_rect = pygame.Rect(0, 0, attack_width, attack_height)
        attack_rect.center = center
        return attack_rect

