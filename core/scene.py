import pygame


class Scene:
    """Interface base para cenas do jogo."""

    def __init__(self, game: "Game") -> None:
        self.game = game

    def enter(self) -> None:
        """Chamado quando a cena é ativada."""

    def handle_event(self, event: pygame.event.Event) -> None:
        """Processa eventos de input da cena."""

    def update(self, delta_time: float) -> None:
        """Atualiza lógica da cena."""

    def draw(self, surface: pygame.Surface) -> None:
        """Desenha a cena na superfície alvo."""
