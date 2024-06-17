from game import Mahjong, Player, DummyPlayer, TilesSequence, PlayAction

import pytest
from unittest.mock import patch


class MockTilesSequence(TilesSequence):
    def __init__(self, tiles):
        self.tiles = tiles
        assert self.tiles != []

    def shuffle(self, start):
        pass


@pytest.mark.parametrize("execution_number", range(100))
def test_up_to_deal(monkeypatch, execution_number):
    monkeypatch.setattr(Mahjong, "play", lambda x: x)
    monkeypatch.setattr(Mahjong, "round_summary", lambda x: x)

    game = Mahjong({0: Player(0), 1: Player(1), 2: Player(2), 3: Player(3)})
    game.start_game()
    for player_idx in game.round_player_sequence:
        if game.players[player_idx].house:
            house_player_idx = player_idx
            assert len(game.players[player_idx].hand.tiles) == 14, (
                f"round sequence: {game.round_player_sequence}; "
                f"house player: {house_player_idx}; "
                f"tiles: {[[idx, len(game.players[idx].hand.tiles)] for idx in range(4)]}"
            )
        else:
            assert len(game.players[player_idx].hand.tiles) == 13, (
                f"round sequence: {game.round_player_sequence}; "
                f"house player: {house_player_idx}; "
                f"player: {player_idx}; "
                f"tiles: {[[idx, len(game.players[idx].hand.tiles)] for idx in range(4)]}"
            )

    assert game.round_player_sequence[0] == house_player_idx
    assert game.round_player_sequence[1] == (house_player_idx + 1) % 4
    assert game.round_player_sequence[2] == (house_player_idx + 2) % 4
    assert game.round_player_sequence[3] == (house_player_idx + 3) % 4


def test_house_winning_immediately(monkeypatch):
    def mock_randint(a, b):
        return 1

    def mock_round_summary(self):
        pass

    import random  # noqa

    monkeypatch.setattr(random, "randint", mock_randint)
    monkeypatch.setattr(Mahjong, "round_summary", mock_round_summary)

    # 天胡
    # fmt: off
    ts = MockTilesSequence([
        "1万", "9万", "1筒", "9筒",  # 0
        "2万", "3万", "4万", "5万",  # 1
        "2万", "3万", "4万", "5万",  # 2
        "1筒", "2筒", "3筒", "4筒",  # 3
        "1索", "9索", "东", "南",  # 0
        "6万", "7万", "8万", "9万",  # 1
        "6万", "7万", "8万", "9万",  # 2
        "1筒", "2筒", "3筒", "4筒",  # 3
        "西", "北", "中", "發",  # 0
        "2万", "2万", "3万", "4万",  # 1
        "3万", "3万", "7万", "8万",  # 2
        "5筒", "6筒", "7筒", "8筒",  # 3
        "白",  # 0
        "5万", # 1
        "9万",  # 2
        "9筒",  # 3
        "白",  # 0
        "6筒",  # ensure `ts` is not empty
    ])
    # fmt: on
    game = Mahjong(
        {
            0: DummyPlayer(0, True),
            1: DummyPlayer(1),
            2: DummyPlayer(2),
            3: DummyPlayer(3),
        }
    )
    game.tile_sequence = ts
    game.start()
    game.deal()
    game.play()
    assert game.winner == 0


def test_resolve_call_priority():
    game = Mahjong({0: Player(0), 1: Player(1), 2: Player(2), 3: Player(3)})
    # hu has the highest priority
    resolved_to, _ = game.resolve_call_priority(
        {
            "hu": [[0, PlayAction(action="hu")]],
            "peng": [
                1,
                PlayAction(action="peng", target_tile="1万", discard_tile="2万"),
            ],
        }
    )
    assert resolved_to == 0

    resolved_to, _ = game.resolve_call_priority(
        {
            "peng": [
                1,
                PlayAction(action="peng", target_tile="1万", discard_tile="2万"),
            ],
            "shang": [
                2,
                PlayAction(action="shang", target_tile="1万", discard_tile="2万"),
            ],
        }
    )
    assert resolved_to == 1

    resolved_to, _ = game.resolve_call_priority(
        {
            "ming_gang": [
                2,
                PlayAction(action="ming_gang", target_tile="1万"),
            ],
            "shang": [
                1,
                PlayAction(action="shang", target_tile="1万", discard_tile="2万"),
            ],
        }
    )
    assert resolved_to == 2

    resolved_to, _ = game.resolve_call_priority(
        {
            "an_gang": [
                2,
                PlayAction(action="an_gang", target_tile="1万"),
            ],
            "shang": [
                1,
                PlayAction(action="shang", target_tile="1万", discard_tile="2万"),
            ],
        }
    )
    assert resolved_to == 2

    resolved_to, _ = game.resolve_call_priority(
        {
            "jia_gang": [
                2,
                PlayAction(action="jia_gang", target_tile="1万"),
            ],
            "shang": [
                1,
                PlayAction(action="shang", target_tile="1万", discard_tile="2万"),
            ],
        }
    )
    assert resolved_to == 2

    resolved_to, _ = game.resolve_call_priority(
        {
            "hu": [
                [1, PlayAction(action="hu")],
                [2, PlayAction(action="hu")],
            ]
        }
    )
    assert resolved_to == 1

    resolved_to, _ = game.resolve_call_priority(
        {
            "hu": [
                [1, PlayAction(action="hu")],
                [3, PlayAction(action="hu")],
            ]
        }
    )
    assert resolved_to == 1

    resolved_to, _ = game.resolve_call_priority(
        {
            "shang": [
                2,
                PlayAction(action="shang", target_tile="1万", discard_tile="2万"),
            ],
        }
    )
    assert resolved_to == 2

    resolved_to, play_action = game.resolve_call_priority(
        {
            "hu": [
                [1, PlayAction(action="hu", target_tile="1万")],
            ],
            "ming_gang": [
                2,
                PlayAction(action="ming_gang", target_tile="1万"),
            ],
        }
    )
    assert resolved_to == 1
    assert play_action.is_qiang_gang_hu

    resolved_to, play_action = game.resolve_call_priority(
        {
            "hu": [
                [1, PlayAction(action="hu", target_tile="1万")],
            ],
            "jia_gang": [
                2,
                PlayAction(action="jia_gang", target_tile="1万"),
            ],
        }
    )
    assert resolved_to == 1
    assert play_action.is_qiang_gang_hu

    resolved_to, play_action = game.resolve_call_priority(
        {
            "hu": [
                [1, PlayAction(action="hu", target_tile="1万")],
                [3, PlayAction(action="hu", target_tile="1万")],
            ],
            "jia_gang": [
                2,
                PlayAction(action="jia_gang", target_tile="1万"),
            ],
        }
    )
    assert resolved_to == 1
    assert play_action.is_qiang_gang_hu


def _test_play_one_round():
    import os, json

    with open(os.path.join(os.path.dirname(__file__), "test_scenario.json")) as rf:
        game_scenario = json.load(rf)

    for scenario in game_scenario:
        # load game scenario
        # assert stuff
        pass


def test_play_with_multiple_resolve_conditions(monkeypatch):
    """
    - peng -> shang -> hu
    - shang -> peng
    - multiple hu
    """

    def mock_randint(a, b):
        return 1

    def mock_round_summary(self):
        pass

    import random  # noqa

    monkeypatch.setattr(random, "randint", mock_randint)
    monkeypatch.setattr(Mahjong, "round_summary", mock_round_summary)

    # multiple hu; 1, 2 hu -> resolve to 1
    # fmt: off
    ts = MockTilesSequence([
        "1万", "1万", "1万", "1万",  # 0
        "2万", "3万", "4万", "5万",  # 1
        "2万", "3万", "4万", "5万",  # 2
        "1筒", "2筒", "3筒", "4筒",  # 3
        "1索", "2索", "3索", "4索",  # 0
        "6万", "7万", "8万", "9万",  # 1
        "6万", "7万", "8万", "9万",  # 2
        "1筒", "2筒", "3筒", "4筒",  # 3
        "5索", "6索", "7索", "8索",  # 0
        "2万", "2万", "3万", "4万",  # 1
        "3万", "3万", "7万", "8万",  # 2
        "5筒", "6筒", "7筒", "8筒",  # 3
        "9索", # 0
        "5万", # 1
        "9万",  # 2
        "9筒",  # 3
        "9筒", # 0, jump
        "6筒",  # ensure `ts` is not empty
    ])
    # fmt: on
    game = Mahjong(
        {
            0: DummyPlayer(0, True),
            1: DummyPlayer(1),
            2: DummyPlayer(2),
            3: DummyPlayer(3),
        }
    )
    game.tile_sequence = ts
    game.start()
    game.deal()
    game.play()
    assert game.round_player_sequence == [0, 1, 2, 3]
    # fmt: off
    assert game.players[0].hand.tiles == ["1万", "1万", "1万", "1索", "2索", "3索", "4索", "5索", "6索", "7索", "8索", "9索", "9筒"]
    assert sorted(game.players[1].hand.tiles) == sorted(["1万", "2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万", "2万", "2万", "3万", "4万", "5万"])
    assert game.players[2].hand.tiles == ["2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万", "3万", "3万", "7万", "8万", "9万"]
    assert game.players[3].hand.tiles == ["1筒", "2筒", "3筒", "4筒", "1筒", "2筒", "3筒", "4筒", "5筒", "6筒", "7筒", "8筒", "9筒"]
    # fmt: on
    assert game.winner == 1

    # peng -> shang -> hu; 2 peng -> 3 shang -> 1 hu
    # fmt: off
    ts = MockTilesSequence([
        "1万", "2万", "3万", "4万",  # 0
        "1索", "2索", "3索", "4索",  # 1
        "1万", "1万", "1筒", "2筒",  # 2
        "2筒", "3筒", "1索", "5万",  # 3
        "5万", "6万", "7万", "8万",  # 0
        "5索", "6索", "7索", "8索",  # 1
        "6万", "7万", "8万", "9万",  # 2
        "1筒", "2筒", "3筒", "4筒",  # 3
        "9万", "1筒", "2筒", "3筒",  # 0
        "9索", "2索", "3索", "4索",  # 1
        "3万", "3万", "7万", "8万",  # 2
        "5筒", "6筒", "7筒", "8筒",  # 3
        "4筒", # 0
        "4索", # 1
        "9万",  # 2
        "9筒",  # 3
        "5筒", # 0, jump
        "6筒",  # ensure `ts` is not empty
    ])
    # fmt: on
    game = Mahjong(
        {
            0: DummyPlayer(0, True),
            1: DummyPlayer(1),
            2: DummyPlayer(2),
            3: DummyPlayer(3),
        }
    )
    game.tile_sequence = ts
    game.start()
    game.deal()
    game.play()
    assert game.round_player_sequence == [0, 1, 2, 3]
    assert game.winner == 1
    assert game.players[2].hand.peng_history == ["1万", "1万", "1万"]
    assert sorted(game.players[3].hand.shang_history) == sorted(["1筒", "2筒", "3筒"])


def test_play_shang_peng(monkeypatch):
    def mock_randint(a, b):
        return 1

    def mock_round_summary(self):
        pass

    import random  # noqa

    monkeypatch.setattr(random, "randint", mock_randint)
    monkeypatch.setattr(Mahjong, "round_summary", mock_round_summary)
    # shang -> peng; 1 shang -> 3 peng -> next player 0
    # fmt: off
    ts = MockTilesSequence([
        "1万", "2万", "3万", "4万",  # 0
        "2万", "3万", "3索", "4索",  # 1
        "2万", "3万", "4万", "2筒",  # 2
        "3索", "3索", "1索", "5万",  # 3
        "4万", "4万", "5万", "6万",  # 0
        "5索", "6索", "7索", "8索",  # 1
        "6万", "7万", "8万", "9万",  # 2
        "1筒", "2筒", "3筒", "4筒",  # 3
        "9万", "1筒", "2筒", "3筒",  # 0
        "9索", "2索", "3索", "4索",  # 1
        "3万", "3万", "7万", "8万",  # 2
        "5筒", "6筒", "7筒", "8筒",  # 3
        "4筒",  # 0
        "4筒",  # 1
        "9万",  # 2
        "9筒",  # 3
        "5筒",  # 0, jump
        "6筒",  # ensure `ts` is not empty
        ]
    )
    # fmt: on
    game = Mahjong(
        {
            0: DummyPlayer(0, True),
            1: DummyPlayer(1),
            2: DummyPlayer(2),
            3: DummyPlayer(3),
        }
    )
    game.tile_sequence = ts
    game.start()
    game.deal()
    game.play()
    assert sorted(game.players[1].hand.shang_history) == sorted(["1万", "2万", "3万"])
    assert game.players[3].hand.peng_history == ["3索", "3索", "3索"]
    assert (
        game.current_player_idx == 1
    )  # is 1 because 0 will finish the turn and move to 1
    assert game.winner is None


def test_quan_feng(monkeypatch):
    def mock_deal(self):
        pass

    def mock_play(self):
        pass

    def mock_round_summary(self):
        # check if self.history exists
        self.history.append(self.quan_feng)

    monkeypatch.setattr(Mahjong, "deal", mock_deal)
    monkeypatch.setattr(Mahjong, "play", mock_play)
    monkeypatch.setattr(Mahjong, "round_summary", mock_round_summary)

    g = Mahjong(
        {
            0: DummyPlayer(0),
            1: DummyPlayer(1),
            2: DummyPlayer(2),
            3: DummyPlayer(3),
        }
    )
    g.history = []
    g.start_full_game()
    # fmt: off
    # assert g.history == ["东", "东", "东", "东", "南", "南", "南", "南", "西", "西", "西", "西", "北", "北", "北", "北"]
    # fmt: on


@patch("random.randint", side_effect=[2, 2, 0, 2, 3, 2, 1, 2])
def test_men_feng(monkeypatch):
    def mock_randint(a, b):
        return 1

    g = Mahjong(
        {
            0: DummyPlayer(0),
            1: DummyPlayer(1),
            2: DummyPlayer(2),
            3: DummyPlayer(3),
        }
    )
    g.tile_sequence = ["东", "南", "西", "北", "东", "南", "西", "北"]
    # g.start()
    # assert
