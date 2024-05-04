import sys

sys.path.append(".")

from game import Mahjong, DummyPlayer


def main():
    # TODO support random house
    while True:
        # to replace while True with standard 24 rounds or 1 round
        # associate round summary/game summary code need to behave correctly
        game = Mahjong(
            {
                0: DummyPlayer(0, debug=True, strategy="dummy"),
                1: DummyPlayer(1, debug=True, strategy="random"),
                2: DummyPlayer(2, debug=True, strategy="dummy"),
                3: DummyPlayer(3, debug=True, strategy="random"),
            }
        )
        game.start()
        if game.winner is None:
            assert game.tile_sequence.is_empty()
        else:
            assert game.winner is not None


if __name__ == "__main__":
    main()
