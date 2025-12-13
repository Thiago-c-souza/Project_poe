import pygame

from core.scene import Scene


class Game:
    """Loop principal do jogo e gerenciamento de cenas."""

    def __init__(self, width: int = 960, height: int = 540, target_fps: int = 60) -> None:
        pygame.init()
        self.size = (width, height)
        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption("ARPG Prototype")
        self.clock = pygame.time.Clock()
        self.target_fps = target_fps
        self.active_scene: Scene | None = None
        self.running = True

    def set_scene(self, scene: Scene) -> None:
        self.active_scene = scene
        scene.enter()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if self.active_scene:
                self.active_scene.handle_event(event)

    def update(self, delta_time: float) -> None:
        if self.active_scene:
            self.active_scene.update(delta_time)

    def draw(self) -> None:
        if self.active_scene:
            self.active_scene.draw(self.screen)
        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            delta_time = self.clock.tick(self.target_fps) / 1000.0
            self.handle_events()
            self.update(delta_time)
            self.draw()
        pygame.quit()
