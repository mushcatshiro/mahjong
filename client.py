from game import Mahjong, HumanPlayer, DummyPlayer, TilesSequence


def main():
    while True:
        # to replace while True with standard 24 rounds or 1 round
        # associate round summary/game summary code need to behave correctly
        game = Mahjong(
            {0: HumanPlayer(0), 1: DummyPlayer(1), 2: DummyPlayer(2), 3: DummyPlayer(3)}
        )
        game.start()
        input("Press Enter to continue or ctrl+c to exit...")


if __name__ == "__main__":
    main()
