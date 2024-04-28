from game import Player, TilesSequence, DummyPlayer

import pytest


class MockTilesSequence(TilesSequence):
    def __init__(self, tiles):
        self.tiles = tiles
        assert self.tiles != []


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


def test_player_deal_stage_with_replacement_in_steps():
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

    p.resolve_tile_replacement(ts)
    assert len(p.hand.tiles) == 14
    assert len(p.hand.flower_tiles) == 2

    # replace once
    ts = MockTilesSequence(["1万", "1万", "1万", "春", "2万", "3万", "4万"])
    p = Player(0, True)
    p.initial_draw(ts, 4, False)
    p.resolve_tile_replacement(ts)
    assert len(p.hand.tiles) == 4
    assert len(p.hand.flower_tiles) == 1
    assert p.hand.tiles == ["1万"] * 3 + ["4万"]

    # replace twice
    ts = MockTilesSequence(["1万", "1万", "春", "夏", "2万", "3万", "4万"])
    p = Player(0, True)
    p.initial_draw(ts, 4, False)
    p.resolve_tile_replacement(ts)
    assert len(p.hand.tiles) == 4
    assert len(p.hand.flower_tiles) == 2
    assert p.hand.tiles == ["1万"] * 2 + ["4万", "3万"]

    # replace eight times
    ts = MockTilesSequence(["1万", "1万", "1万", "1万", "春", "夏", "秋", "冬", "梅", "蘭", "菊", "竹", "2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万"])
    p = Player(0, True)
    for _ in range(3):
        p.initial_draw(ts, 4, False)
    p.resolve_tile_replacement(ts)
    assert len(p.hand.tiles) == 12
    assert len(p.hand.flower_tiles) == 8
    assert p.hand.tiles == ["1万"] * 4 + ["9万", "8万", "7万", "6万", "5万", "4万", "3万", "2万"]


def test_play_turn():
    ts = MockTilesSequence(["1万", "1万", "1万", "2万", "1万", "2万", "3万", "4万"])
    p = DummyPlayer(0, True)
    p.initial_draw(ts, 4, False)  # no replacement needed
    p.play_turn(ts)
    assert len(p.hand.tiles) == 4


def test_player_init():
    # check self.previous_player, self.next_player
    p1 = Player(0)
    assert p1.next_player == 1
    assert p1.previous_player == 3

    p2 = Player(1)
    assert p2.next_player == 2
    assert p2.previous_player == 0

    p3 = Player(2)
    assert p3.next_player == 3
    assert p3.previous_player == 1

    p4 = Player(3)
    assert p4.next_player == 0
    assert p4.previous_player == 2


def test_call_and_call_resolve():
    # TODO test fail
    # peng
    ts = MockTilesSequence(["1万", "1万", "5万", "6万", "7万"])
    p = DummyPlayer(0, True)
    p.initial_draw(ts, 4, False)
    play_actions = p.call("1万", 3)
    assert len(play_actions) == 2
    assert play_actions[0].action == "peng"
    resp = p.call_resolve(play_actions[0], ts)
    assert p.hand.distinct_tile_count["1万"] == 3
    assert "1万" in p.hand.peng_history
    assert resp == play_actions[0].discard_tile

    # ming gang
    ts = MockTilesSequence(["1万", "1万", "1万", "6万", "1万", "4万"])
    p = DummyPlayer(0, True)
    p.initial_draw(ts, 4, False)
    play_actions = p.call("1万", 3)
    assert len(play_actions) == 1
    assert play_actions[0].action == "ming_gang"
    resp = p.call_resolve(play_actions[0], ts)
    assert p.hand.distinct_tile_count["1万"] == 4
    assert "1万" in p.hand.gang_history
    assert len(p.hand.tiles) == 2  # 4 remove 3, replace 1
    assert not resp

    # shang
    ts = MockTilesSequence(["1万", "2万", "6万", "7万"])
    p = DummyPlayer(0, True)
    p.initial_draw(ts, 4, False)
    play_actions = p.call("3万", 3)
    assert len(play_actions) == 2
    assert play_actions[0].action == "shang"
    resp = p.call_resolve(play_actions[0], ts)
    assert p.hand.shang_history == ["1万", "2万", "3万"]
    assert resp == play_actions[0].discard_tile

    # can not shang
    ts = MockTilesSequence(["1万", "2万", "6万", "7万"])
    p = DummyPlayer(0, True)
    p.initial_draw(ts, 4, False)
    play_actions = p.call("3万", 1)
    assert not play_actions
    # not calling
