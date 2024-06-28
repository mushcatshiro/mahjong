import copy
from save_state import State
import random


__all__ = [
    "TilesSequence",
    "HUAS",
    "FENGS",
    "JIANS",
    "Tiles",
    "RENDER_TILES",
    "SHANGS",
    "SHANG_LUT",
    "REVERSED_SHANG_LUT",
    "SHANG_REF",
    "SHANG_EXCLUDE",
    "SUITES",
]


HUAS = ("春", "夏", "秋", "冬", "梅", "蘭", "菊", "竹")
FENGS = ("东", "南", "西", "北")
JIANS = ("中", "發", "白")

# fmt: off
Tiles = {
    "1万": 4, "2万": 4, "3万": 4, "4万": 4, "5万": 4, "6万": 4, "7万": 4, "8万": 4, "9万": 4,
    "1筒": 4, "2筒": 4, "3筒": 4, "4筒": 4, "5筒": 4, "6筒": 4, "7筒": 4, "8筒": 4, "9筒": 4,
    "1索": 4, "2索": 4, "3索": 4, "4索": 4, "5索": 4, "6索": 4, "7索": 4, "8索": 4, "9索": 4,
    "东": 4, "南": 4, "西": 4, "北": 4,
    "白": 4, "發": 4, "中": 4,
    "春": 1, "夏": 1, "秋": 1, "冬": 1,
    "梅": 1, "蘭": 1, "菊": 1, "竹": 1,
}

# TODO using 11x13 grid for rendering; 2 \u2587 as 1x1 pixel
RENDER_TILES = {}

# fmt: on

SHANGS = ("123", "234", "345", "456", "567", "678", "789")

SHANG_LUT = {
    "12": ["3"],
    "13": ["2"],
    "23": ["1", "4"],
    "24": ["3"],
    "34": ["2", "5"],
    "35": ["4"],
    "45": ["3", "6"],
    "46": ["5"],
    "56": ["4", "7"],
    "57": ["6"],
    "67": ["5", "8"],
    "68": ["7"],
    "78": ["6", "9"],
    "79": ["8"],
    "89": ["7"],
}

REVERSED_SHANG_LUT = {
    "1": ["23"],
    "2": ["13", "34"],
    "3": ["12", "24", "45"],
    "4": ["23", "35", "56"],
    "5": ["34", "46", "67"],
    "6": ["45", "57", "78"],
    "7": ["56", "68", "89"],
    "8": ["67", "79"],
    "9": ["78"],
}

SHANG_REF = [
    "123",
    "234",
    "345",
    "456",
    "567",
    "678",
    "789",
]

SHANG_EXCLUDE = (
    "东",
    "南",
    "西",
    "北",
    "白",
    "發",
    "中",
)

SUITES = ("万", "筒", "索")


class TilesSequence(State):
    def __init__(self):
        self.tiles: list = []
        for card, count in Tiles.items():
            self.tiles += [card] * count
        self.initial_sequence = copy.deepcopy(self.tiles)

    def shuffle(self, start):
        random.shuffle(self.tiles)
        self.tiles = self.tiles[start:] + self.tiles[:start]

    def draw(self, total=1, jump=False):
        if jump:
            assert total == 2
            return [self.tiles.pop(0), self.tiles.pop(3)]
        else:
            assert total in [1, 4]

            if total == 1:
                return [self.tiles.pop(0)]
            else:
                return [self.tiles.pop(0) for _ in range(total)]

    def replace(self, total):
        """
        replace with last tile. used when there is a "gang" or getting a non
        playable tile
        """
        rv = []
        for _ in range(total):
            rv.append(self.tiles.pop(-1))
        return rv

    def is_empty(self):
        return len(self.tiles) == 0

    def only_flowers(self):
        rv = [1 if x in HUAS else 0 for x in self.tiles]
        if all(rv):
            return True
        return False
