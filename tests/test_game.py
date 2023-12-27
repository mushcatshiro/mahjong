from game import Mahjong, Player

import pytest


@pytest.mark.parametrize("execution_number", range(100))
def test_up_to_deal(monkeypatch, execution_number):
    monkeypatch.setattr(Mahjong, "play", lambda x: x)
    monkeypatch.setattr(Mahjong, "round_summary", lambda x: x)

    game = Mahjong({0: Player(0), 1: Player(1), 2: Player(2), 3: Player(3)})
    game.start()
    for player_idx in game.current_round_player_sequence:
        if game.players[player_idx].house:
            house_player_idx = player_idx
            assert len(game.players[player_idx].hand.tiles) == 14, (
                f"round sequence: {game.current_round_player_sequence}; "
                f"house player: {house_player_idx}; "
                f"tiles: {[[idx, len(game.players[idx].hand.tiles)] for idx in range(4)]}"
            )
        else:
            assert len(game.players[player_idx].hand.tiles) == 13, (
                f"round sequence: {game.current_round_player_sequence}; "
                f"house player: {house_player_idx}; "
                f"player: {player_idx}; "
                f"tiles: {[[idx, len(game.players[idx].hand.tiles)] for idx in range(4)]}"
            )

    assert game.current_round_player_sequence[0] == house_player_idx
    assert game.current_round_player_sequence[1] == (house_player_idx + 1) % 4
    assert game.current_round_player_sequence[2] == (house_player_idx + 2) % 4
    assert game.current_round_player_sequence[3] == (house_player_idx + 3) % 4
