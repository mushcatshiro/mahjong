import time
from game import Mahjong, DummyPlayer


"""
TODO to replace `DummyPlayer` with something reasonable

two option to bench
- bench `play_one_round` directly
- bench `play` / total rounds
"""

l = []

# TODO support random house
for i in range(10000):
    g = Mahjong(
        {
            0: DummyPlayer(0, True),
            1: DummyPlayer(1),
            2: DummyPlayer(2),
            3: DummyPlayer(3),
        }
    )
    g.prepare()
    g.play()
