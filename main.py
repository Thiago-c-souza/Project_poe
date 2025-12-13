from core.game import Game
from scenes.game_scene import GameScene


def main() -> None:
    game = Game()
    game.set_scene(GameScene(game))
    game.run()


if __name__ == "__main__":
    main()
