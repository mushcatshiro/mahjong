import sys
import yaml

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


def main(max_games):
    # TODO support random house
    ctr = 0
    complete_games = 0
    draw_games = 0
    while ctr <= max_games:
        # to replace while True with standard 24 rounds or 1 round
        # associate round summary/game summary code need to behave correctly
        try:
            game = Mahjong(
                {
                    0: DummyPlayer(0, debug=True, strategy="dummy"),
                    1: DummyPlayer(1, debug=True, strategy="random"),
                    2: DummyPlayer(2, debug=True, strategy="dummy"),
                    3: DummyPlayer(3, debug=True, strategy="random"),
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
            if game.winner is None:
                draw_games += 1
                assert game.tile_sequence.is_empty()
            else:
                complete_games += 1
                assert game.winner is not None
            for i, player in game.players.items():
                print_details(player)
        finally:
            ctr += 1
            sys.stdout.flush()
    print(
        f"total games: {ctr}; complete games: {complete_games}; draw games: {draw_games}"
    )


if __name__ == "__main__":
    import random
    import argparse

    random.seed(0)
    parser = argparse.ArgumentParser()
    parser.add_argument("--max_games", type=int, default=1_000_000)
    args = parser.parse_args()
    main(args.max_games)
