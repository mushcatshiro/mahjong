import sys
import yaml
import time

sys.path.append(".")

from game import Mahjong, DummyPlayer


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
                if player.house:
                    print(f"Player {i} is house")
                print(
                    f"Player {i} history: \n\n{yaml.dump(player.hand.tiles_history, allow_unicode=True, sort_keys=False)}"
                )
                print(
                    f"Player {i} hand: {player.hand.tiles}; flower: {player.hand.flower_tiles}"
                )
                print(
                    f"Player {i} peng: {player.hand.peng_history}; gang: {player.hand.gang_history}; shang: {player.hand.shang_history}"
                )
                print("\n")
            print(f"{game.tile_sequence.tiles}")
            break
        ctr += 1
        end = time.monotonic()
        sys.stdout.flush()
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
        # print(f"game {ctr} took {end - start} seconds")
    print(
        f"total games: {ctr}; complete games: {complete_games}; draw games: {draw_games}"
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
