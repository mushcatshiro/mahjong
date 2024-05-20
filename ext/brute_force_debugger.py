import sys
import yaml
import time

sys.path.append(".")

from game import Mahjong, DummyPlayer


def print_details(player):
    # fmt: off
    if player.house:
        print(f"Player {player.player_idx} is house")
    print(f"Player {player.player_idx} history: \n\n{yaml.dump(player.hand.tiles_history, allow_unicode=True, sort_keys=False)}")
    print(f"Player {player.player_idx} hand: {player.hand.tiles}; flower: {player.hand.flower_tiles}")
    print(f"Player {player.player_idx} peng: {player.hand.peng_history};\n gang: {player.hand.gang_history};\n shang: {player.hand.shang_history}")
    print("\n")
    # fmt: on


def main(rounds, debug):
    # TODO support random house
    ctr = 0
    winning_game_time_avg = 0
    draw_game_time_avg = 0
    complete_games = 0
    draw_games = 0
    while ctr <= rounds:
        # to replace while True with standard 24 rounds or 1 round
        # associate round summary/game summary code need to behave correctly
        try:
            start = time.monotonic()
            game = Mahjong(
                {
                    0: DummyPlayer(0, debug=debug, strategy="dummy"),
                    1: DummyPlayer(1, debug=debug, strategy="random"),
                    2: DummyPlayer(2, debug=debug, strategy="dummy"),
                    3: DummyPlayer(3, debug=debug, strategy="random"),
                }
            )
            game.start()
        except Exception as e:
            # print stack trace
            import traceback

            print(f"Exception occurred {e}: ")
            print("".join(traceback.format_exception(*sys.exc_info())))
            for i, player in game.players.items():
                print_details(player)
            print(f"{game.tile_sequence.tiles}")
            break
        else:
            end = time.monotonic()
            if game.winner is None:
                draw_games += 1
                assert game.tile_sequence.is_empty()
                draw_game_time_avg = (
                    (draw_game_time_avg * (draw_games - 1)) + (end - start)
                ) / draw_games
                print(f"{ctr} draw game time avg: {draw_game_time_avg}")
            else:
                complete_games += 1
                assert game.winner is not None
                winning_game_time_avg = (
                    (winning_game_time_avg * (complete_games - 1)) + (end - start)
                ) / complete_games
                print(f"{ctr} winning game time avg: {winning_game_time_avg}")
            if debug:
                for i, player in game.players.items():
                    print_details(player)
        finally:
            ctr += 1
            sys.stdout.flush()

    print(
        f"total games: {ctr}; "
        f"complete games: {complete_games} @ avg {winning_game_time_avg}s; "
        f"draw games: {draw_games} @ avg {draw_game_time_avg}s;"
    )


if __name__ == "__main__":
    import random
    import argparse

    random.seed(0)
    parser = argparse.ArgumentParser()
    parser.add_argument("--rounds", default=1_000_000, type=int)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    main(args.rounds, args.debug)
