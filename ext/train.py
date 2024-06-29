import sys
import random

random.seed(0)

sys.path.append(".")

from env import EnvMahjong, EnvPlayer

# from player import GreedyPlayer


class EnvGreedyPlayer(EnvPlayer):
    def step(self, state):
        print(state.shape)
        # BUG call shape and play shape are different
        assert state.shape == (48, 36, 4) or state.shape == (4, 36, 4)
        if state[1:, :, :].sum() == 0:
            return []
        return 0


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
while r < 1:
    while not environment.done:
        print(environment.stage)
        current_player_idx = environment.get_current_player_idx()
        print(current_player_idx)
        current_player: EnvPlayer = environment.players[current_player_idx]
        state = environment.get_state(
            current_player_idx,
            include_valid_actions=True,
            use_oracle=True,
            to_tensor=True,
        )
        action = current_player.step(state)
        print(f"sampled action: {action}")
        reward = environment.play_round(action, current_player_idx)
    print(environment.round_summary())
    environment.reset()
    r += 1
