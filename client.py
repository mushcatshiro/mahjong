from game import Mahjong
from player import Player, DummyPlayer, GreedyPlayer
from model import PlayAction


__all__ = ["MahjongClient", "HumanPlayer"]


class HumanPlayer(Player):
    def print_hand(self, played_tile=None, **kwargs):
        # TODO move to `Player`
        print(f"hand: {sorted(self.hand.tiles)}")
        if played_tile:
            print(f"played_tile: {played_tile}")
        print(f"peng_history: {self.hand.peng_history}")
        print(f"shang_history: {self.hand.shang_history}")
        print(f"gang_history: {self.hand.gang_history}")

    def play_turn_strategy(self, possible_actions):
        self.print_hand()
        print(f"possible actions: ")
        for idx, action in enumerate(possible_actions):
            print(f"{idx}: {action}")
        resp = int(input("Choose an action: "))
        assert len(possible_actions) > resp
        print(f"action: {possible_actions[resp]}")
        return possible_actions[resp]

    def call_strategy(self, possible_actions, played_tile) -> PlayAction:
        self.print_hand(played_tile)
        print("possible actions: ")
        for idx, action in enumerate(possible_actions):
            print(f"{idx}: {action}")
        resp = int(input("Choose an action or -1 to pass: "))
        if resp == -1:
            return []
        else:
            assert len(possible_actions) > resp
            print(f"action: {possible_actions[resp]}")
            return possible_actions[resp]

    def gang_discard_strategy(self, possible_actions) -> PlayAction:
        self.print_hand()
        print("possible actions: ")
        for idx, action in enumerate(possible_actions):
            print(f"{idx}: {action}")
        resp = int(input("Choose an action: "))
        assert len(possible_actions) > resp
        print(f"action: {possible_actions[resp]}")
        return possible_actions[resp]


class MahjongClient(Mahjong):
    def __init__(self, players):
        super().__init__(players)

    def resolve_call(self, responses):
        print(f"responses: {responses}")
        play_result, resolve_to = super().resolve_call(responses)
        print(f"resolve_to: {resolve_to}")
        print(f"play_result: {play_result}")
        return play_result, resolve_to

    def play_one_round(self):
        print(f"current round sequence {self.current_round_sequence}")
        print(f"current player idx {self.current_player_idx}")
        print(f"discarded pool: {self.discarded_pool}")
        print("-" * 80)
        super().play_one_round()
        print("=" * 80)


def main():
    while True:
        # to replace while True with standard 24 rounds or 1 round
        # associate round summary/game summary code need to behave correctly
        game = MahjongClient(
            {
                0: HumanPlayer(0),
                1: GreedyPlayer(1),
                2: GreedyPlayer(2),
                3: GreedyPlayer(3),
            }
        )
        game.start_game()
        input("Press Enter to continue or ctrl+c to exit...")


if __name__ == "__main__":
    main()
