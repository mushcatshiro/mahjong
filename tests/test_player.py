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
    ts = MockTilesSequence(
        [
            "1万",
            "1万",
            "1万",
            "1万",
            "春",
            "夏",
            "秋",
            "冬",
            "梅",
            "蘭",
            "菊",
            "竹",
            "2万",
            "3万",
            "4万",
            "5万",
            "6万",
            "7万",
            "8万",
            "9万",
        ]
    )
    p = Player(0, True)
    for _ in range(3):
        p.initial_draw(ts, 4, False)
    p.resolve_tile_replacement(ts)
    assert len(p.hand.tiles) == 12
    assert len(p.hand.flower_tiles) == 8
    assert p.hand.tiles == ["1万"] * 4 + ["9万", "8万", "7万", "6万", "5万", "4万", "3万", "2万"]


def test_play_turn():
    # fmt: off
    ts = MockTilesSequence(["1万", "9万", "1筒", "9筒", "1索", "9索", "东", "南", "西", "北", "白", "發", "中", "2万", "3万", "4万", "5万"])
    # fmt: on
    p = DummyPlayer(0, True)
    for _ in range(3):
        p.initial_draw(ts, 4, False)
    p.initial_draw(ts, 2, True)
    p.play_turn(ts)
    assert len(p.hand.tiles) == 13

    # fmt: off
    ts = MockTilesSequence(["1万", "1万", "9万", "1筒", "9筒", "1索", "9索", "东", "南", "西", "北", "白", "發", "中"])
    # fmt: on
    p = DummyPlayer(0, False)
    for _ in range(3):
        p.initial_draw(ts, 4, False)
    p.initial_draw(ts, 1, False)  # not house
    resp = p.play_turn(ts)
    assert resp.hu


def test_player_init():
    # check self.previous_player, self.next_player
    p1 = Player(0)
    assert p1.next_player_idx == 1
    assert p1.previous_player_idx == 3

    p2 = Player(1)
    assert p2.next_player_idx == 2
    assert p2.previous_player_idx == 0

    p3 = Player(2)
    assert p3.next_player_idx == 3
    assert p3.previous_player_idx == 1

    p4 = Player(3)
    assert p4.next_player_idx == 0
    assert p4.previous_player_idx == 2


def test_call(monkeypatch):
    def mock_call_strategy(self, call_actions, played_tile):
        # bypass call strategy to check all possible call actions
        return call_actions

    monkeypatch.setattr(DummyPlayer, "call_strategy", mock_call_strategy)

    # peng
    ts = MockTilesSequence(["1万", "1万", "5万", "6万"])
    p = DummyPlayer(0, True)
    p.initial_draw(ts, 4, False)
    play_actions = p.call("1万", 3)
    assert len(play_actions) == 2
    assert play_actions[0].action == "peng"

    # ming gang
    ts = MockTilesSequence(["1万", "1万", "1万", "6万", "1万", "4万"])
    p = DummyPlayer(0, True)
    p.initial_draw(ts, 4, False)
    play_actions = p.call("1万", 3)
    assert len(play_actions) == 1
    assert play_actions[0].action == "ming_gang"

    # shang
    ts = MockTilesSequence(["1万", "2万", "6万", "7万"])
    p = DummyPlayer(0, True)
    p.initial_draw(ts, 4, False)
    play_actions = p.call("3万", 3)
    assert len(play_actions) == 2
    assert play_actions[0].action == "shang"

    # can not shang
    ts = MockTilesSequence(["1万", "2万", "6万", "7万"])
    p = DummyPlayer(0, True)
    p.initial_draw(ts, 4, False)
    play_actions = p.call("3万", 1)
    assert not play_actions

    # hu
    ts = MockTilesSequence(
        ["1万", "1万", "1万", "2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万", "1筒", "2筒"]
    )
    p = DummyPlayer(0, True)
    for _ in range(3):
        p.initial_draw(ts, 4, False)
    p.initial_draw(ts, 1, False)
    play_actions = p.call("3筒", 3)
    assert play_actions.action == "hu"


def test_call_resolve():
    # peng
    ts = MockTilesSequence(["1万", "1万", "5万", "6万"])
    p = DummyPlayer(0, True)
    p.initial_draw(ts, 4, False)
    play_action = p.call("1万", 3)
    assert play_action.action == "peng"
    resp = p.call_resolve(play_action, ts)
    assert p.hand.distinct_tile_count["1万"] == 3
    assert "1万" in p.hand.peng_history
    assert resp.discarded_tile == play_action.discard_tile

    # ming gang
    ts = MockTilesSequence(["1万", "1万", "1万", "6万", "1万", "4万"])
    p = DummyPlayer(0, True)
    p.initial_draw(ts, 4, False)
    play_action = p.call("1万", 3)
    assert play_action.action == "ming_gang"
    resp = p.call_resolve(play_action, ts)
    assert p.hand.distinct_tile_count["1万"] == 4
    assert "1万" in p.hand.gang_history
    assert len(p.hand.tiles) == 2  # 4 remove 3, replace 1
    assert resp.need_replacement

    # shang
    ts = MockTilesSequence(["1万", "2万", "6万", "7万"])
    p = DummyPlayer(0, True)
    p.initial_draw(ts, 4, False)
    play_action = p.call("3万", 3)
    assert play_action.action == "shang"
    resp = p.call_resolve(play_action, ts)
    assert p.hand.shang_history == ["1万", "2万", "3万"]
    assert resp.discarded_tile == play_action.discard_tile

    # hu
    ts = MockTilesSequence(
        ["1万", "1万", "1万", "2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万", "1筒", "2筒"]
    )
    p = DummyPlayer(0, True)
    for _ in range(3):
        p.initial_draw(ts, 4, False)
    p.initial_draw(ts, 1, False)
    play_action = p.call("3筒", 3)
    assert play_action.action == "hu"
    resp = p.call_resolve(play_action, ts)
    assert resp.hu
