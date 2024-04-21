from game import Player, TilesSequence

import pytest


class MockTilesSequence(TilesSequence):
    def __init__(self, tiles):
        self.tiles = tiles
        assert self.tiles != []


class MockPlayer(Player):
    def play_turn_strategy(self, possible_actions, input_tile):
        # TODO too many hacks and assumptions here
        if type(possible_actions) == str:
            self.pending_resolve = getattr(self, f"resolve_{possible_actions}")
            return possible_actions
        elif type(possible_actions) == dict:
            for k, v in possible_actions.items():
                if v:
                    self.pending_resolve = getattr(self, f"resolve_{k}")
                    return {
                        "resolve": True,
                        "input_tile": input_tile,
                        "tile_sequence": True
                        if k in ["ming_gang", "jia_gang", "an_gang"]
                        else False,
                        "discard_tile": None,
                    }
            return {
                "resolve": False,
                "input_tile": input_tile,
                "tile_sequence": False,
                "discard_tile": "鬼牌",
            }

    def call_strategy(self, possible_actions, played_tile):
        for k, v in possible_actions.items():
            if v:
                return {
                    "action": k,
                    "input_tile": played_tile,
                    "tile_sequence": True
                    if k in ["ming_gang", "jia_gang", "an_gang"]
                    else False,
                    "discard_tile": "鬼牌" if k in ["peng", "shang"] else None,
                }
        return {"action": None}


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
    assert len(p.hand.flower_tiles) == 1

    p._replace_tiles(ts)
    assert len(p.hand.tiles) == 13
    assert len(p.hand.flower_tiles) == 2

    p._replace_tiles(ts)
    assert len(p.hand.tiles) == 14
    assert len(p.hand.flower_tiles) == 2


def test_player_resolve_tile_replacement():
    # replace once
    ts = MockTilesSequence(["2万", "3万", "4万"])
    p = Player(0, True)
    p.hand.add_tiles(["1万"] * 3 + ["春"])
    p.resolve_tile_replacement(ts)
    assert len(p.hand.tiles) == 4
    assert len(p.hand.flower_tiles) == 1
    assert p.hand.tiles == ["1万"] * 3 + ["4万"]

    # replace twice
    ts = MockTilesSequence(["2万", "3万", "4万"])
    p = Player(0, True)
    p.hand.add_tiles(["1万"] * 3 + ["春", "夏"])
    p.resolve_tile_replacement(ts)
    assert len(p.hand.tiles) == 5
    assert len(p.hand.flower_tiles) == 2
    assert p.hand.tiles == ["1万"] * 3 + ["4万", "3万"]

    # replace eight times
    ts = MockTilesSequence(["2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万"])
    p = Player(0, True)
    p.hand.add_tiles(["1万"] * 3 + ["春", "夏", "秋", "冬", "梅", "蘭", "菊", "竹"])
    p.resolve_tile_replacement(ts)
    assert len(p.hand.tiles) == 11
    assert len(p.hand.flower_tiles) == 8
    assert p.hand.tiles == ["1万"] * 3 + ["9万", "8万", "7万", "6万", "5万", "4万", "3万", "2万"]


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
    p.play_turn_strategy("peng", None)  # str
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
    # TODO probably need more testings
    ts = MockTilesSequence(["2万"] * 4)

    # an gang
    p = MockPlayer(0, True)
    p.hand.add_tiles(["1万"] * 4)
    assert p.an_gang("1万")
    p.play_turn_strategy("an_gang", None)  # str
    p.resolve(["1万"], None, ts)
    assert p.hand.distinct_tile_count["1万"] == 4
    assert p.hand.distinct_tile_count["2万"] == 1

    ts = MockTilesSequence(["2万"] * 4)
    # ming gang
    p = MockPlayer(0, True)
    p.hand.add_tiles(["1万"] * 3)
    assert p.ming_gang("1万")
    p.play_turn_strategy("ming_gang", None)  # str
    p.resolve(["1万"], None, ts)
    assert p.hand.distinct_tile_count["1万"] == 4
    assert p.hand.distinct_tile_count["2万"] == 1

    ts = MockTilesSequence(["2万"] * 4)
    # jia gang
    p = MockPlayer(0, True)
    p.hand.add_tiles(["1万"] * 2)
    assert p.peng("1万")
    p.hand.add_tiles(["1万"] * 1, is_peng=True)  # simulate peng resolve w/o discard
    assert p.jia_gang("1万")
    p.play_turn_strategy("jia_gang", None)  # str
    p.resolve(["1万"], None, ts)
    assert p.hand.distinct_tile_count["1万"] == 4
    assert p.hand.distinct_tile_count["2万"] == 1

    # gang with replacement


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


def test_shang_resolve():
    p = MockPlayer(0, True)
    p.hand.add_tiles(["2万", "3万", "4万"])
    assert "1万" not in p.hand.distinct_tile_count.keys()
    assert p.hand.distinct_tile_count["2万"] == 1
    assert p.hand.distinct_tile_count["3万"] == 1
    assert p.hand.distinct_tile_count["4万"] == 1
    assert len(p.hand.tiles) == 3
    assert p.shang("1万", 3)
    p.play_turn_strategy("shang", None)  # str
    p.resolve(["1万"], "4万")
    assert p.hand.distinct_tile_count["1万"] == 1
    assert p.hand.distinct_tile_count["2万"] == 1
    assert p.hand.distinct_tile_count["3万"] == 1
    assert p.hand.distinct_tile_count["4万"] == 0
    assert len(p.hand.tiles) == 3


def test_play_turn():
    # draw_check
    ts = MockTilesSequence(["1万", "2万", "3万", "4万"])
    p = MockPlayer(0, True)
    p.hand.add_tiles(["1万"] * 3)  # force an gang
    p.play_turn(1, ts)
    assert len(p.hand.tiles) == 5
    assert p.hand.distinct_tile_count["1万"] == 4

    # no draw_check
    ts = MockTilesSequence(["1万", "2万", "3万", "4万"])
    p = MockPlayer(0, True)
    p.hand.add_tiles(["1万", "鬼牌"])  # force an gang
    p.play_turn(1, ts)
    assert len(p.hand.tiles) == 2
    assert p.hand.distinct_tile_count["1万"] == 2
    assert p.hand.distinct_tile_count["鬼牌"] == 0


def test_call():
    # peng
    ts = MockTilesSequence(["1万", "2万", "3万", "4万"])
    p = MockPlayer(0, True)
    p.hand.add_tiles(["1万"] * 2 + ["鬼牌"])
    response = p.call("1万", 3)
    response["action"] == "peng"
    p.resolve(
        response["input_tile"],
        response["discard_tile"],
        ts if response["tile_sequence"] else None,
    )
    assert p.hand.distinct_tile_count["1万"] == 3
    assert p.hand.distinct_tile_count["鬼牌"] == 0

    # ming gang
    ts = MockTilesSequence(["1万", "2万", "3万", "4万"])
    p = MockPlayer(0, True)
    p.hand.add_tiles(["1万"] * 3)
    response = p.call("1万", 3)
    response["action"] == "ming_gang"
    p.resolve(
        response["input_tile"],
        response["discard_tile"],
        ts if response["tile_sequence"] else None,
    )
    assert p.hand.distinct_tile_count["1万"] == 4
    assert p.hand.distinct_tile_count["4万"] == 1

    # shang
    ts = MockTilesSequence(["1万", "2万", "3万", "4万"])
    p = MockPlayer(0, True)
    p.hand.add_tiles(["2万", "3万", "鬼牌"])
    response = p.call("1万", 3)
    response["action"] == "shang"
    p.resolve(
        response["input_tile"],
        response["discard_tile"],
        ts if response["tile_sequence"] else None,
    )
    assert p.hand.distinct_tile_count["1万"] == 1
    assert p.hand.distinct_tile_count["2万"] == 1
    assert p.hand.distinct_tile_count["3万"] == 1

    ts = MockTilesSequence(["1万", "2万", "3万", "4万"])
    p = MockPlayer(0, True)
    p.hand.add_tiles(["2万", "3万"])
    response = p.call("1万", 2)
    with pytest.raises(AssertionError):
        assert response["action"]

    # not calling


def test_dummy_player():
    pass
