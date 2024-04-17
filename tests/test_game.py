from game import Mahjong, Player, DummyPlayer, TilesSequence

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
    game.start()
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


def test_player_sequence(monkeypatch):
    def mock_deal(self: Mahjong):
        for player_idx in self.round_player_sequence:
            player: Player = self.players[player_idx]
            player.initial_draw(self.tile_sequence, 4, False)

    def mock_start(self: Mahjong):
        self.current_player_idx = 0
        self.round_player_sequence = [0, 1, 2, 3]
        self.deal()
        self.play()

    monkeypatch.setattr(Mahjong, "start", mock_start)
    monkeypatch.setattr(Mahjong, "deal", mock_deal)

    # force peng by player 0 plays 1万
    ts = MockTilesSequence(
        [
            "1万", "1筒", "4筒", "7筒",
            "5万", "6万", "7万", "8万",
            "1万", "1万", "9万", "1筒",
            "2筒", "4筒", "4筒", "5筒",
            "1索", "7筒", "8筒",
        ]
    )
    game = Mahjong({0: DummyPlayer(0), 1: DummyPlayer(1), 2: DummyPlayer(2), 3: DummyPlayer(3)})
    game.tile_sequence = ts
    game.start()


@patch("random.randint", 0)
def test_resolve_call():
    game = Mahjong({0: Player(0), 1: Player(1), 2: Player(2), 3: Player(3)})
    # hu has the highest priority
    resolved_to = game.resolve_call({
        "hu": [0],
        "peng": [1],
    })
    assert resolved_to == 0

    resolved_to = game.resolve_call({
        "peng": 1,
        "shang": 2,
    })
    assert resolved_to == 1

    resolved_to = game.resolve_call({
        "ming_gang": 2,
        "shang": 1,
    })
    assert resolved_to == 2

    resolved_to = game.resolve_call({
        "an_gang": 2,
        "shang": 1,
    })
    assert resolved_to == 2

    resolved_to = game.resolve_call({
        "jia_gang": 2,
        "shang": 1,
    })
    assert resolved_to == 2

    resolved_to = game.resolve_call({
        "hu": [1, 2]
    })
    assert resolved_to == 1

    resolved_to = game.resolve_call({
        "hu": [1, 3],
    })
    assert resolved_to == 1


def _test_play_one_round():
    import os, json
    with open(os.path.join(os.path.dirname(__file__), "test_scenario.json")) as rf:
        game_scenario = json.load(rf)
    
    for scenario in game_scenario:
        # load game scenario
        # assert stuff
        pass