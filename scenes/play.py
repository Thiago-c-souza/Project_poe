import pygame

from core.scene import Scene

PLAYER_SIZE = 32
PLAYER_COLOR = (230, 230, 120)
BACKGROUND_COLOR = (25, 30, 40)
FLOOR_COLOR = (60, 70, 90)
BORDER_COLOR = (120, 140, 180)


class PlayScene(Scene):
    """Cena inicial para validar movimento e colisão em top-down."""

    def __init__(self, game: "Game") -> None:
        super().__init__(game)
        self.player_pos = pygame.Vector2(game.size[0] / 2, game.size[1] / 2)
        self.speed = 220
        self.arena_rect = pygame.Rect(64, 48, game.size[0] - 128, game.size[1] - 96)

    def enter(self) -> None:
        pass

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
        self.player_pos += direction * self.speed * delta_time
        self._clamp_player()

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BACKGROUND_COLOR)
        pygame.draw.rect(surface, FLOOR_COLOR, self.arena_rect)
        pygame.draw.rect(surface, BORDER_COLOR, self.arena_rect, width=3)
        player_rect = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
        player_rect.center = self.player_pos
        pygame.draw.rect(surface, PLAYER_COLOR, player_rect)

    def _clamp_player(self) -> None:
        half_size = PLAYER_SIZE / 2
        min_x = self.arena_rect.left + half_size
        max_x = self.arena_rect.right - half_size
        min_y = self.arena_rect.top + half_size
        max_y = self.arena_rect.bottom - half_size
        self.player_pos.x = max(min_x, min(self.player_pos.x, max_x))
        self.player_pos.y = max(min_y, min(self.player_pos.y, max_y))
