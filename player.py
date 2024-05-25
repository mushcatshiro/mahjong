import copy
import random

from game import Player, PlayAction


class GreedyPlayer(Player):
    """
    short sighted player that considers their hand only
    """

    def __init__(self, player_idx, house=False, debug=False, strategy="random"):
        super().__init__(player_idx, house)
        self.soft_locked_tiles = []
        self.distinct_tiles = {}
        self.conflicts = []

    def preprocess_hand(self):
        self.soft_locked_tiles = []  # reset

        tiles = copy.deepcopy(self.hand.tiles)

        self.soft_locked_tiles += self.hand.get_valid_eye_sets(tiles)

        shang_sets = self.hand.get_valid_shang_sets(tiles)
        for shang_set in shang_sets:
            self.soft_locked_tiles += shang_set

        peng_sets = self.hand.get_valid_peng_sets(tiles)
        for peng_set in peng_sets:
            self.soft_locked_tiles += peng_set
        self.soft_locked_tiles = list(set(self.soft_locked_tiles))

    def trim_possible_actions(self, possible_actions):
        trimmed_possible_actions = []
        for action in possible_actions:
            action: PlayAction
            if action.discard_tile and action.discard_tile in self.soft_locked_tiles:
                continue
            trimmed_possible_actions.append(action)
        return trimmed_possible_actions

    def play_turn_strategy(self, possible_actions) -> PlayAction:
        """
        TODO dealing with tiles used in multiple sets
        peng, shang, eyes
        shang + peng is ok to keep all
        shang + peng + gang need to think
        """
        self.preprocess_hand()
        trimmed_possible_actions = self.trim_possible_actions(possible_actions)
        return random.choice(trimmed_possible_actions)

    def call_strategy(self, possible_actions, played_tile, **kwargs) -> PlayAction:
        if not possible_actions:
            return []
        for action in possible_actions:
            if action.action == "hu":
                return action
        # BUG remove locked discards then randomly choose?
        return random.choice(possible_actions)

    def gang_discard_strategy(self, possible_actions) -> PlayAction:
        self.preprocess_hand()
        trimmed_possible_actions = self.trim_possible_actions(possible_actions)
        return random.choice(trimmed_possible_actions)
