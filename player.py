import copy
from typing import List

from game import Player, PlayAction


class GreedyPlayer(Player):
    """
    short sighted player that considers their hand only
    """

    def __init__(self, player_idx, house=False, weights=None):
        super().__init__(player_idx, house)
        if weights is None:
            weights = {
                "jiang": 20,
                "shang": 10,
                "peng": 10,
                "an_gang": -10,
                "jia_gang": 10,
                "ming_gang": 1,
                "hu": 1000,
                "an_ke": 100,
                "an_shang": 80,
                "discard": 0,
            }
        self.weights = weights

    def calculate_play_action_score(self, action: PlayAction) -> int:
        score = 0
        if action.action == "hu":
            return self.weights[action.action]
        resulting_hand: list = copy.deepcopy(self.hand.tiles)
        if self.hand.gang_history:
            score += (
                len(self.hand.gang_history)
                * (self.weights["ming_gang"] + self.weights["jia_gang"])
                / 2
            )
        if self.hand.peng_history:
            score += len(self.hand.peng_history) * self.weights["peng"]
        if self.hand.shang_history:
            score += len(self.hand.shang_history) * self.weights["shang"]
        if self.hand.an_gang_history:
            score += len(self.hand.an_gang_history) * self.weights["an_gang"]
        # action score
        score += self.weights[action.action]
        # remove gang/peng/shang tiles
        if action.action == "jia_gang":
            resulting_hand.remove(action.move_tiles[0])
        else:
            for tile in action.move_tiles:
                resulting_hand.remove(tile)
        if action.discard_tile:
            resulting_hand.remove(action.discard_tile)
        # remaining score
        score += len(self.hand.get_valid_jiangs(resulting_hand)) * self.weights["jiang"]
        score += (
            len(self.hand.get_valid_peng_sets(resulting_hand)) * self.weights["an_ke"]
        )
        score += (
            len(self.hand.get_valid_shang_sets(resulting_hand))
            * self.weights["an_shang"]
        )
        return score

    def play_turn_strategy(self, possible_actions: List[PlayAction]) -> PlayAction:
        play_action_scores = {}
        for idx, action in enumerate(possible_actions):
            play_action_scores[idx] = self.calculate_play_action_score(action)
        max_play_action_score = max(play_action_scores, key=play_action_scores.get)
        return possible_actions[max_play_action_score]

    def call_strategy(self, possible_actions, played_tile, **kwargs) -> PlayAction:
        call_action_scores = {}
        for idx, action in enumerate(possible_actions):
            call_action_scores[idx] = self.calculate_play_action_score(action)
        max_call_action_score = max(call_action_scores, key=call_action_scores.get)
        return possible_actions[max_call_action_score]

    def gang_discard_strategy(self, possible_actions) -> PlayAction:
        gang_discard_action_scores = {}
        for idx, action in enumerate(possible_actions):
            gang_discard_action_scores[idx] = self.calculate_play_action_score(action)
        max_gang_discard_action_score = max(
            gang_discard_action_scores, key=gang_discard_action_scores.get
        )
        return possible_actions[max_gang_discard_action_score]


class AssistedPlayer:
    """听牌 is implemented here
    expect to be slower than non-assisted player
    """

    pass
