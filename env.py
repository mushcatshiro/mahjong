import os
from typing import Dict

from game import Mahjong, Player
from model import PlayResult
from player import PlayAction
from tiles import TilesSequence


class EnvPlayAction:
    """
    To be reimplemented is the agent implementation is different
    """

    def __init__(self, possible_actions):
        self.possible_actions = possible_actions

    def model_to_tensor(possible_actions):
        # idx 0 is the current hand
        # idx 1 - 31 is the potential next state hand TODO validate 30 is max
        # idx 32 - 34 is the other players open hand
        return

    def tensor_to_model(self, selected_action_idx):
        return self.possible_actions[selected_action_idx]


class EnvPlayer(Player):
    def __init__(self, player_idx, debug=False):
        super().__init__(player_idx, debug=debug)

    def draw_stage(self):
        # TODO port back to initial implementation in `Player`
        raise NotImplementedError

    def step(self, state) -> PlayAction:
        raise NotImplementedError

    def execute_play_turn_strategy(
        self, action: PlayAction, tile_sequence: TilesSequence
    ):
        # TODO port back to initial implementation in `Player`
        play_result: PlayResult = self.hand.resolve(action)
        if play_result.need_replacement:
            if tile_sequence.is_empty():
                return PlayResult(draw=True), False
            tile = tile_sequence.replace(1)
            self.replacement_tile_count += self.hand.add_tiles(
                tile, "replace", action.action
            )
            replacement_result = self.resolve_tile_replacement(tile_sequence)
            if not replacement_result.complete:
                return PlayResult(draw=True), False
            possible_discards = self.hand.get_discardable_tiles()
            return possible_discards, True
        return play_result, False

    def execute_gang_discard_strategy(self, action):
        # TODO port back to initial implementation in `Player`
        pass


class EnvMahjong(Mahjong):
    def __init__(self, players: Dict[int, EnvPlayer]):
        for player in dict.values():
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
        current_player.draw_stage()
        self.stage = "draw"
        self.next_stage = "play_turn_strategy"
        return

    def get_call_sequence(self):
        return [x for x in range(self.current_player_idx, 4)] + [
            x for x in range(0, self.current_player_idx)
        ]

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

    def play_round(self, action: PlayAction):
        """
        if player can proceed till discard, stop prior to collecting calls
        if player need play turn strategy, stop at call turn strategy
          once action provided, continue till discard
        **need a way to break out from endless call to next player draw**
        **only move self.current_player_idx ahead when there is no call**
        """
        action = tensor_to_model(action)

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
            outcome, has_gang_discard = current_player.execute_play_turn_strategy(
                action
            )
            # outcome is either a PlayResult or a list of PlayAction
            # BUG process play result
            if has_gang_discard:
                outcome: PlayAction
                self.state = "gang_discard_strategy"
            else:
                outcome: PlayResult
                self.discarded_pool.append(outcome.discarded_tile)
                self.done = self.process_play_result(outcome, self.current_player_idx)
                if self.done:
                    return
                self.state = "call"
                self.call_sequence = self.get_call_sequence()
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
                    current_player.draw_stage()
                    self.state = "play_turn_strategy"
                    return
                play_result, resolve_to = self.resolve_call(self.call_responses)
                self.done = self.process_play_result(play_result, resolve_to)
                if self.done:
                    return
                self.call_sequence = self.get_call_sequence()
            else:
                self.update_call_responses(current_player.player_idx, action)
        return

    def get_state(self, use_oracle=False):
        # discarded pool, current player hand, other players showed tiles, tile sequence
        state = []
        # ensure self hand is at position 0
        current_player: EnvPlayer = self.players[self.current_player_idx]
        state.append(current_player.hand.get_hand(use_oracle=True))
        seq = self.get_call_sequence()
        for player_idx in seq:
            player: EnvPlayer = self.players[player_idx]
            state.append(player.hand.get_hand(use_oracle=use_oracle))
        return model_to_tensor(state)

    def round_summary(self):
        return super().round_summary()
