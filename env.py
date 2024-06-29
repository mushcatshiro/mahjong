import os
from typing import Dict, List

from game import Mahjong, Player
from model import PlayResult
from player import PlayAction
from tiles import TilesSequence

try:
    import numpy as np
except ImportError:
    raise ImportError("Please install numpy")


# fmt: off
TILE_INDEX = {
    "1万": 0, "2万": 1, "3万": 2, "4万": 3, "5万": 4, "6万": 5, "7万": 6, "8万": 7, "9万": 8,
    "1筒": 9, "2筒": 10, "3筒": 11, "4筒": 12, "5筒": 13, "6筒": 14, "7筒": 15, "8筒": 16, "9筒": 17,
    "1索": 18, "2索": 19, "3索": 20, "4索": 21, "5索": 22, "6索": 23, "7索": 24, "8索": 25, "9索": 26,
    "东": 27, "南": 28, "西": 29, "北": 30,
    "白": 31, "發": 32, "中": 33,
    "春": 34, "夏": 34, "秋": 34, "冬": 34,
    "梅": 35, "蘭": 35, "菊": 35, "竹": 35,
}
# fmt: on


class EnvPlayer(Player):
    def __init__(self, player_idx):
        super().__init__(player_idx)
        self.valid_actions = None

    def reset(self):
        super().reset()
        self.valid_actions = None

    def step(self, state) -> PlayAction:
        raise NotImplementedError

    def execute_gang_discard_strategy(self, action):
        play_result = self.hand.resolve(action)
        return play_result

    def update_valid_actions(self, valid_actions):
        self.valid_actions = valid_actions

    def reset_valid_actions(self):
        self.valid_actions = None

    def get_state(self, use_oracle, include_valid_actions, to_tensor=False):
        hand_state = self.hand.get_hand(use_oracle=use_oracle)
        valid_actions = []
        if include_valid_actions:
            valid_actions = self.valid_actions
        if to_tensor:
            state = self.model_to_tensor(hand_state, valid_actions)

        return state

    def draw_stage(self, tile_sequence: TilesSequence):
        outcome = super().draw_stage(tile_sequence)
        self.update_valid_actions(outcome)
        if self.terminate_check(outcome):
            return True
        return False

    def model_to_tensor(self, hand_state, possible_actions: List[PlayAction] = None):
        state = np.zeros((36, 4))
        for tile, count in hand_state.items():
            state[TILE_INDEX[tile], :count] = 1
        if possible_actions:
            action_state = np.zeros((44, 36, 4))
            max_idx = np.sum(state, axis=1)
            for action_idx, possible_action in enumerate(possible_actions):
                possible_action: PlayAction
                if possible_action.discard_tile:
                    discard_idx = TILE_INDEX[possible_action.discard_tile]
                    action_state[
                        action_idx, discard_idx, int(max_idx[discard_idx]) - 1
                    ] = 0
                if possible_action.target_tile:
                    target_idx = TILE_INDEX[possible_action.target_tile]
                    action_state[action_idx, target_idx, max_idx[target_idx]] = 1
            state = state.reshape(1, 36, 4)
            state = np.concatenate((state, action_state), axis=0)
        else:
            state = state.reshape(1, 36, 4)
        return state

    def tensor_to_model(self, selected_action_idx):
        print(self.valid_actions[selected_action_idx])
        return self.valid_actions[selected_action_idx]


class EnvMahjong(Mahjong):
    def __init__(self, players: Dict[int, EnvPlayer]):
        for player in players.values():
            if not isinstance(player, EnvPlayer):
                raise ValueError("Player must be a subclass of `EnvPlayer`")
        super().__init__(players)
        self.done = False
        self.stage = ""
        self.call_sequence = []
        self.call_responses = (
            {}
        )  # TODO might want to consider creating a class for this

    def get_current_player_idx(self):
        # BUG must be validated
        if self.stage == "play_turn_strategy" or self.stage == "gang_discard_strategy":
            return self.current_player_idx
        elif self.stage == "call":
            print(self.call_sequence)
            if len(self.call_sequence) != 0:
                return self.call_sequence.pop(0)
            else:
                raise ValueError(
                    "No more players to call"
                )  # pragma: no cover; for brute force testing

    def reset(self):
        super().reset()
        self.done = False
        self.prepare()
        self.deal()

        current_player: EnvPlayer = self.players[self.current_player_idx]
        self.done = current_player.draw_stage(self.tile_sequence)
        if self.done:
            return
        self.stage = "play_turn_strategy"
        return

    def get_call_sequence(self):
        full_seq = [x for x in range(self.current_player_idx, 4)] + [
            x for x in range(0, self.current_player_idx)
        ]
        return full_seq[1:]

    def update_call_responses(self, player_idx, action: PlayAction):
        # TODO port back to initial implementation in `Mahjong`
        if not action:
            return
        if action.action == "hu":
            if action.action not in self.call_responses:
                self.call_responses["hu"] = [[player_idx, action]]
            else:
                self.call_responses["hu"].append([player_idx, action])
        else:
            self.call_responses[action.action] = [player_idx, action]

    def post_play_turn_strategy_check(self, action: PlayAction):
        if action.action == "hu":
            self.winner = self.current_player_idx
            return True
        elif action.action == "draw":
            return True
        return False

    def process_play_result(self, play_result: PlayResult, resolve_to):
        if self.stage == "call":
            self.call_sequence = []
            self.call_responses = {}  # reset
        if play_result.hu:
            self.winner = resolve_to
            return True
        elif play_result.draw:
            return True
        elif play_result.discarded_tile:
            self.discarded_pool.append(play_result.discarded_tile)
            self.current_player_idx = resolve_to
            return False

    def reset_valid_actions(self):
        for player in self.players:
            player: EnvPlayer
            player.reset_valid_actions()

    def play_round(self, action: PlayAction, call_player_idx: int = None):
        """
        if player can proceed till discard, stop prior to collecting calls
        if player need play turn strategy, stop at call turn strategy
          once action provided, continue till discard
        **need a way to break out from endless call to next player draw**
        **only move self.current_player_idx ahead when there is no call**
        """

        print(self.current_player_idx)
        current_player: EnvPlayer = self.players[
            self.current_player_idx
        ]  # TODO consider using `get_current_player_idx`
        action = current_player.tensor_to_model(action)
        if self.stage == "play_turn_strategy":
            # move on to
            # 1. gang discard
            # 2. call
            self.done = self.post_play_turn_strategy_check(action)
            if self.done:
                return
            outcome, has_gang_discard = current_player.execute_strategy(
                action, self.tile_sequence
            )
            if has_gang_discard:
                outcome: PlayAction
                self.stage = "gang_discard_strategy"
            else:
                print("in post play turn strategy")
                outcome: PlayResult
                self.discarded_pool.append(outcome.discarded_tile)
                self.done = self.process_play_result(outcome, self.current_player_idx)
                if self.done:
                    return
                self.stage = "call"
                self.call_sequence = self.get_call_sequence()
                print(f"in {self.stage} set call sequence")
        elif self.stage == "gang_discard_strategy":
            # finish gang discard, add to discarded pool
            # move on to
            # 1. call
            play_result = current_player.execute_gang_discard_strategy(action)
            self.discarded_pool.append(action.discard_tile)
            self.stage = "call"
        elif self.stage == "call":
            # append action to self.call_response
            # if all players called, resolve and move to
            # 1. gang discard
            # 2. call
            if (
                len(self.call_sequence) == 0
            ):  # enter the condition when all players have called
                if not self.call_responses:
                    self.current_player_idx = current_player.next_player_idx
                    current_player = self.players[self.current_player_idx]
                    self.reset_valid_actions()
                    self.done = current_player.draw_stage(self.tile_sequence)
                    if self.done:
                        return
                    self.stage = "play_turn_strategy"
                    return
                play_result, resolve_to = self.resolve_call(self.call_responses)
                self.reset_valid_actions()
                self.done = self.process_play_result(play_result, resolve_to)
                if self.done:
                    return
                self.call_sequence = self.get_call_sequence()
            else:
                print(f"call resp: {self.call_responses}")
                print(action)
                self.update_call_responses(call_player_idx, action)
        return

    def get_state(
        self,
        current_player_idx,
        include_valid_actions,
        use_oracle=False,
        to_tensor=False,
    ):
        # discarded pool, current player hand, other players showed tiles, tile sequence
        full_state = []
        # ensure self hand is at position 0
        current_player: EnvPlayer = self.players[current_player_idx]
        full_state.append(
            current_player.get_state(
                use_oracle=True,
                include_valid_actions=include_valid_actions,
                to_tensor=to_tensor,
            )
        )
        seq = self.get_call_sequence()
        for player_idx in seq:
            player: EnvPlayer = self.players[player_idx]
            full_state.append(
                player.get_state(
                    use_oracle=use_oracle,
                    include_valid_actions=False,
                    to_tensor=to_tensor,
                )
            )
        if to_tensor:
            full_state = np.concatenate(full_state)
        return full_state

    def round_summary(self):
        return super().round_summary()
