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
        self.valid_actions = []

    def reset(self):
        super().reset()
        self.valid_actions = []

    def step(self, state) -> PlayAction:
        raise NotImplementedError

    def execute_gang_discard_strategy(self, action):
        play_result = self.hand.resolve(action)
        return play_result

    def update_valid_actions(self, valid_actions):
        self.valid_actions = valid_actions

    def reset_valid_actions(self):
        self.valid_actions = []

    def get_state(
        self,
        use_oracle,
        stage,
        to_tensor=False,
        discard_player_idx=None,
        discarded_tile=None,
        need_call_check=False,
    ):
        # print(f"@ {self.player_idx} get_state")
        # print(f"args: {use_oracle}, {stage}, {to_tensor}, {discard_player_idx}, {discarded_tile}, {need_call_check}")
        valid_actions = []
        no_action_flag = False
        if stage == "call" and need_call_check:
            # print("in call")
            # print(self.hand.tiles)
            self.valid_actions = self.call_check(discarded_tile, discard_player_idx)
            valid_actions += self.valid_actions
            if not valid_actions:
                no_action_flag = True
        elif stage == "play_turn_strategy" or stage == "gang_discard_strategy":
            # print("in strategy")
            # print(self.hand.tiles)
            valid_actions += self.valid_actions
        # print(len(valid_actions))
        distinct_tiles = self.hand.get_hand(use_oracle=use_oracle)
        # print(discarded_tile)
        if to_tensor:
            state = self.model_to_tensor(distinct_tiles, valid_actions, no_action_flag)
        # print(state.shape)
        return state

    def draw_stage(self, tile_sequence: TilesSequence):
        outcome = super().draw_stage(tile_sequence)
        if self.terminate_check(outcome):
            return True
        self.valid_actions = outcome
        return False

    def execute_strategy(self, action: PlayAction, tile_sequence: TilesSequence):
        outcome, has_gang_discard = super().execute_strategy(action, tile_sequence)
        if has_gang_discard:
            outcome: List[PlayAction]  # list of gang discard options
            self.valid_actions = outcome
        return outcome, has_gang_discard

    def call_resolve(self, action: PlayAction, tile_sequence: TilesSequence):
        if action.action == "hu":
            if action.is_hai_di_lao_yue:
                self.winning_conditions.append("海底捞月")
            if action.is_qiang_gang_hu:
                self.winning_conditions.append("抢杠胡")
            if action.is_jue_zhang:
                self.winning_conditions.append("和绝张")
            if action.hu_by == "jiang":
                self.winning_conditions.append("单骑对子")
            self.hand.add_tiles([action.target_tile], "hu-add", action.hu_by)
            return self.hand.get_hu_play_result(), False
        outcome, has_gang_discard = self.execute_strategy(action, tile_sequence)
        # if has_gang_discard:
        # print(f"in call resovle {outcome}, {has_gang_discard}, setting valid actions")
        # self.valid_actions = outcome
        return outcome, has_gang_discard

    def model_to_tensor(
        self,
        distinct_tiles: dict,
        possible_actions: List[PlayAction] = False,
        no_action_flag=False,
    ):
        # print(f"m2t: {distinct_tiles}, {possible_actions}, {no_action_flag}")
        assert possible_actions is not None  # pragma: no cover; for brute force testing
        hand_state = np.zeros((1, 36, 4))
        for tile, count in distinct_tiles.items():
            hand_state[0, TILE_INDEX[tile], :count] = 1
        if possible_actions:
            action_state = np.zeros((44, 36, 4))
            max_idx = np.sum(hand_state, axis=2).astype(int)
            for action_idx, possible_action in enumerate(possible_actions):
                possible_action: PlayAction
                tmp = np.copy(hand_state)
                if possible_action.discard_tile:
                    discard_idx = TILE_INDEX[possible_action.discard_tile]
                    tmp[
                        0, discard_idx, max_idx[0, discard_idx] - 1
                    ] = 0  # should make a copy of state
                if possible_action.target_tile:
                    target_idx = TILE_INDEX[possible_action.target_tile]
                    tmp[0, target_idx, max_idx[0, target_idx] - 1] = 1
                action_state[action_idx] = tmp
            assert action_state.sum() != 0  # pragma: no cover; for brute force testing
            hand_state = np.concatenate((hand_state, action_state), axis=0)
        if no_action_flag:
            hand_state = np.concatenate((hand_state, np.zeros((44, 36, 4))), axis=0)
        return hand_state

    def tensor_to_model(self, selected_action_idx):
        # print(f"sampled: {self.valid_actions[selected_action_idx]}")
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
            # print(self.call_sequence)
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
        # for player in self.players.values():
        #     print(f"player: {player.player_idx} is {'house' if player.house else 'not house'}")
        #     print(f"hand: {player.hand.tiles}")

        current_player: EnvPlayer = self.players[self.current_player_idx]
        self.done = current_player.draw_stage(self.tile_sequence)
        if self.done:
            return
        self.stage = "play_turn_strategy"
        # print("exit reset")
        return

    def get_call_sequence(self, player_idx):
        full_seq = [x for x in range(player_idx, 4)] + [x for x in range(0, player_idx)]
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

    def reset_valid_actions(self, skip=None):
        # TODO needed?
        for idx, player in self.players.items():
            if skip is not None and idx == skip:
                continue
            player: EnvPlayer
            player.reset_valid_actions()

    def is_done(self):
        return self.done or self.tile_sequence.is_empty()

    def resolve_call(self, responses):
        resolve_to, play_action = self.resolve_call_priority(responses)
        if play_action.action == "hu":
            if self.tile_sequence.is_empty():
                play_action: PlayAction
                play_action.is_hai_di_lao_yue = True
            called_tile = play_action.target_tile
            showed_tiles = []
            ctr = 0
            for player in self.players.values():
                showed_tiles += player.hand.get_showable_tiles()
            for tile in showed_tiles:
                if tile == called_tile:
                    ctr += 1
            if ctr == 3:
                play_action.is_jue_zhang = True
        outcome, has_gang_discard = self.players[resolve_to].call_resolve(
            play_action, self.tile_sequence
        )
        return outcome, has_gang_discard, resolve_to

    def play_round(self, action: PlayAction, call_player_idx: int = None):
        """
        if player can proceed till discard, stop prior to collecting calls
        if player need play turn strategy, stop at call turn strategy
          once action provided, continue till discard
        **need a way to break out from endless call to next player draw**
        **only move self.current_player_idx ahead when there is no call**
        """

        # print(self.current_player_idx)
        current_player: EnvPlayer = self.players[
            self.current_player_idx
        ]  # TODO consider using `get_current_player_idx`
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
                # print("in post play turn strategy")
                outcome: PlayResult
                self.discarded_pool.append(outcome.discarded_tile)
                self.done = self.process_play_result(outcome, self.current_player_idx)
                if self.done:
                    return
                self.stage = "call"
                self.call_sequence = self.get_call_sequence(current_player.player_idx)
                # print(f"in {self.stage} set call sequence")
        elif self.stage == "gang_discard_strategy":
            # finish gang discard, add to discarded pool
            # move on to
            # 1. call
            play_result = current_player.execute_gang_discard_strategy(action)
            self.done = self.process_play_result(play_result, self.current_player_idx)
            if self.done:
                return
            self.discarded_pool.append(action.discard_tile)
            self.stage = "call"
            self.call_sequence = self.get_call_sequence(current_player.player_idx)
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
                outcome, has_gang_discard, resolve_to = self.resolve_call(
                    self.call_responses
                )
                # print("post resolve call")
                if has_gang_discard:
                    # print(f"reset and skip {resolve_to}")
                    self.reset_valid_actions(skip=resolve_to)
                    self.call_responses = {}  # reset
                    outcome: PlayAction
                    self.stage = "gang_discard_strategy"
                    self.current_player_idx = resolve_to
                else:
                    self.reset_valid_actions()
                    self.call_responses = {}  # reset
                    outcome: PlayAction
                    self.done = self.process_play_result(outcome, resolve_to)
                    if self.done:
                        return
                    self.call_sequence = self.get_call_sequence(
                        current_player.player_idx
                    )
            else:
                self.update_call_responses(call_player_idx, action)
                # print(f"call resp: {self.call_responses}")
                # print(action)
        return

    def get_state(
        self,
        input_player_idx,
        use_oracle=False,
        to_tensor=False,
    ):
        # discarded pool, current player hand, other players showed tiles, tile sequence
        full_state = []
        # ensure self hand is at position 0
        current_player: EnvPlayer = self.players[input_player_idx]
        full_state.append(
            current_player.get_state(
                use_oracle=True,
                stage=self.stage,
                to_tensor=to_tensor,
                discarded_tile=self.discarded_pool[-1]
                if self.stage == "call"
                else None,
                discard_player_idx=self.current_player_idx
                if self.stage == "call"
                else None,
                need_call_check=True if self.stage == "call" else False,
            )
        )
        seq = self.get_call_sequence(input_player_idx)
        for player_idx in seq:
            player: EnvPlayer = self.players[player_idx]
            s = player.get_state(
                use_oracle=use_oracle,
                stage=self.stage,
                to_tensor=to_tensor,
            )
            # print(f"{player_idx}, {s.shape}")
            full_state.append(s)
        if to_tensor:
            full_state = np.concatenate(full_state)
        return full_state

    def round_summary(self):
        return super().round_summary()
