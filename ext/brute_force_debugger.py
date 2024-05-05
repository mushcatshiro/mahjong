import sys
import yaml

sys.path.append(".")

from game import Mahjong, DummyPlayer


def main():
    # TODO support random house
    ctr = 0
    complete_games = 0
    draw_games = 0
    while True:
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
        if game.winner is None:
            draw_games += 1
            assert game.tile_sequence.is_empty()
        else:
            complete_games += 1
            assert game.winner is not None
    print(f"total games: {ctr}; complete games: {complete_games}; draw games: {draw_games}")


if __name__ == "__main__":
    import random
    random.seed(0)
    main()
