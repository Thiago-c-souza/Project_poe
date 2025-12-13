from core.game import Game
from scenes.play import PlayScene


def main() -> None:
    game = Game()
    game.set_scene(PlayScene(game))
    game.run()


if __name__ == "__main__":
    main()
