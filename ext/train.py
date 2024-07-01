import sys
import random

random.seed(0)

sys.path.append(".")

from env import EnvMahjong, EnvPlayer

# from player import GreedyPlayer


class EnvGreedyPlayer(EnvPlayer):
    def step(self, state):
        # print(self.valid_actions)
        assert state.shape == (48, 36, 4), f"receive shape: {state.shape}"
        if state[1:45, :, :].sum() == 0:
            # print("pass")
            return []
        # implementing random?
        action = self.tensor_to_model(0)  # BUG valid actions does not include pass
        # print(action)
        return action


environment = EnvMahjong(
    players={
        0: EnvGreedyPlayer(0),
        1: EnvGreedyPlayer(1),
        2: EnvGreedyPlayer(2),
        3: EnvGreedyPlayer(3),
    }
)
environment.reset()


class Model:
    def step(self, state, **kwargs):
        return 0


m = Model()

r = 0
while r < 1_000_000:
    print(f"in round: {r}")
    while not environment.is_done():
        # print(f"in stage: {environment.stage}")
        current_player_idx = environment.get_current_player_idx()
        # print(current_player_idx)
        current_player: EnvPlayer = environment.players[current_player_idx]
        state = environment.get_state(
            current_player_idx,
            use_oracle=True,
            to_tensor=True,
        )
        action = current_player.step(state)
        # print(f"action: {action}")
        reward = environment.play_round(action, current_player_idx)
    # print(environment.round_summary())
    # print("-" * 80)
    if environment.winner is not None:
        print(f"Winner: {environment.winner}")
    environment.reset()
    r += 1
