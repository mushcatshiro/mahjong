from game import Mahjong, Player, PlayAction, DummyPlayer


class HumanPlayer(Player):
    def play_turn_strategy(self, possible_actions):
        print(f"hand: {sorted(self.hand.tiles)}")
        print(f"peng_history: {self.hand.peng_history}")
        print(f"shang_history: {self.hand.shang_history}")
        print(f"gang_history: {self.hand.gang_history}")
        print(f"possible actions: ")
        for idx, action in enumerate(possible_actions):
            print(f"{idx}: {action}")
        resp = int(input("Choose an action: "))
        assert len(possible_actions) > resp
        print(f"action: {possible_actions[resp]}")
        return possible_actions[resp]

    def call_strategy(self, possible_actions, played_tile) -> PlayAction:
        print(f"hand: {sorted(self.hand.tiles)}")
        print(f"played_tile: {played_tile}")
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
        super().play_one_round()
        print("=" * 80)


def main():
    while True:
        # to replace while True with standard 24 rounds or 1 round
        # associate round summary/game summary code need to behave correctly
        game = MahjongClient(
            {0: HumanPlayer(0), 1: DummyPlayer(1), 2: DummyPlayer(2), 3: DummyPlayer(3)}
        )
        game.start()
        input("Press Enter to continue or ctrl+c to exit...")


if __name__ == "__main__":
    main()
