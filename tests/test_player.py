from game import Player, TilesSequence

import pytest


class MockTilesSequence(TilesSequence):
    def __init__(self, tiles):
        self.tiles = tiles
        assert self.tiles != []


class MockPlayer(Player):
    def strategy(self, possible_actions):
        if possible_actions.endswith("gang"):
            possible_actions = "gang"
        self.pending_resolve = getattr(self, f"resolve_{possible_actions}")


def test_player_deal_stage_without_replacement():
    ts = MockTilesSequence(
        [
            "1万",
            "2万",
            "3万",
            "4万",
            "5万",
            "6万",
            "7万",
            "8万",
            "9万",
            "1筒",
            "2筒",
            "3筒",
            "4筒",
            "5筒",
            "6筒",
            "7筒",
            "8筒",
        ]
    )
    p = Player(0, True)

    for i in range(3):
        p.initial_draw(ts, 4, False)
    p.initial_draw(ts, 2, True)

    assert len(p.hand.tiles) == 14


def test_player_deal_stage_with_replacement():
    # ("春", "夏", "秋", "冬", "梅", "蘭")
    ts = MockTilesSequence(
        [
            "1万",
            "2万",
            "3万",
            "4万",
            "5万",
            "6万",
            "7万",
            "8万",
            "9万",
            "1筒",
            "2筒",
            "3筒",
            "菊",
            "4筒",
            "5筒",
            "6筒",
            "7筒",
            "8筒",
            "竹",
        ]
    )
    p = Player(0, True)

    for i in range(3):
        p.initial_draw(ts, 4, False)
    p.initial_draw(ts, 2, True)

    assert len(p.hand.tiles) == 13
    assert len(p.hand.non_playable_tiles) == 1

    p.replace_tiles(ts)
    assert len(p.hand.tiles) == 13
    assert len(p.hand.non_playable_tiles) == 2

    p.replace_tiles(ts)
    assert len(p.hand.tiles) == 14
    assert len(p.hand.non_playable_tiles) == 2


def test_player_resolve_tile_replacement():
    pass


def test_peng():
    p = Player(0, True)
    p.hand.add_tiles(["1万"] * 2)

    assert p.peng("1万")

    p.hand.add_tiles(["2万"] * 2)
    assert p.peng("1万")

    p.hand.add_tiles(["1万"] * 1)
    with pytest.raises(AssertionError):
        assert p.peng("1万")


def test_peng_resolve():
    p = MockPlayer(0, True)
    p.hand.add_tiles(["1万"] * 2 + ["2万"])
    p.strategy("peng")
    assert p.pending_resolve.__name__ == "resolve_peng"
    p.resolve(["1万"], "2万")
    assert p.hand.distinct_tile_count["1万"] == 3
    assert p.hand.distinct_tile_count["2万"] == 0


def test_gang():
    # an gang
    p = Player(0, True)
    p.hand.add_tiles(["1万"] * 3)
    p.hand.add_tiles(["1万"] * 1)  # simulate a draw
    assert p.an_gang("1万")

    # ming gang
    p = Player(0, True)
    p.hand.add_tiles(["1万"] * 3)
    assert p.ming_gang("1万")

    # jia gang
    p = Player(0, True)
    p.hand.add_tiles(["1万"] * 2)
    assert p.peng("1万")
    p.hand.add_tiles(["1万"] * 1, is_peng=True)  # simulate peng resolve w/o discard
    assert p.jia_gang("1万")


def test_gang_resolve():
    ts = MockTilesSequence(["2万"] * 4)
    # an gang
    p = MockPlayer(0, True)
    p.hand.add_tiles(["1万"] * 4)
    p.strategy("an_gang")
    p.resolve(["1万"], None, ts)
    assert p.hand.distinct_tile_count["1万"] == 4
    assert p.hand.distinct_tile_count["2万"] == 1


def test_shang():
    p = Player(0, True)
    assert p.previous_player == 3

    p = Player(1, True)
    assert p.previous_player == 0

    p = Player(2, True)
    assert p.previous_player == 1

    p = Player(3, True)
    assert p.previous_player == 2

    p.hand.add_tiles(["2万", "3万"])
    assert p.shang("1万", 2)

    with pytest.raises(AssertionError):
        assert p.shang(["4万"], 0)
