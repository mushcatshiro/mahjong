import copy
import random
from typing import List


from save_state import State
from hand import Hand
from tiles import TilesSequence
from model import ReplacementResult, PlayResult, PlayAction


__all__ = ["Player", "DummyPlayer", "GreedyPlayer"]


class Player(State):
    def __init__(self, player_idx, house=False):
        # TODO add player turn count/call count?
        self.player_idx = player_idx
        self.previous_player_idx = (player_idx - 1) % 4
        self.next_player_idx = (player_idx + 1) % 4
        self.hand = Hand(player_idx)
        self.action_history = []
        self.house = house
        self.men_feng = None
        self.replacement_tile_count = 0
        self.winning_conditions = []
        self.result_fan = None

    def reset(self):
        self.hand.reset()
        self.action_history = []
        self.winning_conditions = []
        self.result_fan = None

    def initial_draw(self, tile_sequence: TilesSequence, total, jump: bool):
        tiles = tile_sequence.draw(total, jump)
        self.replacement_tile_count += self.hand.add_tiles(tiles, "add", "draw")

    def _replace_tiles(self, tile_sequence: TilesSequence):
        replaced_tiles = tile_sequence.replace(self.replacement_tile_count)
        self.replacement_tile_count -= len(replaced_tiles)
        self.replacement_tile_count += self.hand.add_tiles(replaced_tiles, "replace")

    def resolve_tile_replacement(
        self, tile_sequence: TilesSequence
    ) -> ReplacementResult:
        if self.replacement_tile_count == 0:
            return ReplacementResult(complete=True)
        while self.replacement_tile_count > 0:
            try:
                self._replace_tiles(tile_sequence)
            except IndexError:
                return ReplacementResult(complete=False)
        return ReplacementResult(complete=True)

    def play_turn(self, tile_sequence: TilesSequence) -> PlayResult:
        possible_actions = []
        if self.house and len(self.hand.tiles) == 14:
            if self.hand.is_winning_hand():
                self.winning_conditions.append("自摸")
                return self.hand.get_hu_play_result()
            possible_actions += self.hand.get_discardable_tiles()
        else:
            drawed_tile = tile_sequence.draw()  # guaranteed
            if tile_sequence.is_empty():
                self.winning_conditions.append("妙手回春")
            self.replacement_tile_count += self.hand.add_tiles(
                drawed_tile, "add", "draw"
            )
            replacement_result = self.resolve_tile_replacement(tile_sequence)
            if "妙手回春" not in self.winning_conditions and tile_sequence.is_empty():
                self.winning_conditions.append("妙手回春")
            if not replacement_result.complete:
                return PlayResult(draw=True)

            if self.hand.is_winning_hand():
                self.winning_conditions.append("自摸")
                return self.hand.get_hu_play_result()

            possible_actions += self.hand.get_discardable_tiles()
            possible_actions += self.hand.get_gang_candidates(
                drawed_tile=drawed_tile[0]
            )
        action: PlayAction = self.play_turn_strategy(possible_actions)
        assert action.action in ["an_gang", "jia_gang", "discard"]
        play_result = self.hand.resolve(action)
        if play_result.need_replacement:
            if tile_sequence.is_empty():
                return PlayResult(draw=True)
            tile = tile_sequence.replace(1)
            self.replacement_tile_count += self.hand.add_tiles(
                tile, "replace", action.action
            )
            replacement_result = self.resolve_tile_replacement(tile_sequence)
            if not replacement_result.complete:
                return PlayResult(draw=True)
            possible_discards = self.hand.get_discardable_tiles()
            discard_play_action = self.gang_discard_strategy(possible_discards)
            play_result = self.hand.resolve(discard_play_action)
        return play_result

    def call(self, played_tile, player) -> PlayAction:
        # to include pass option
        call_actions = []
        is_hu = self.hand.is_winning_hand(call_tile=played_tile)
        call_actions += self.hand.get_peng_candidates(played_tile, is_hu)
        call_actions += self.hand.get_gang_candidates(played_tile, is_hu)

        if is_hu:
            call_actions += self.hand.get_shang_candidates(played_tile, is_hu)
            # 1. allow skip hu 2. track winning conditions
        elif player == self.previous_player_idx:
            call_actions += self.hand.get_shang_candidates(played_tile, is_hu)

        if not call_actions and is_hu:
            # imply dan qi dui zi
            call_actions += [
                PlayAction(action="hu", target_tile=played_tile, hu_by="jiang")
            ]
        if not call_actions:
            return []
        call_action = self.call_strategy(call_actions, played_tile)
        return call_action

    def call_resolve(
        self, action: PlayAction, tile_sequence: TilesSequence
    ) -> PlayResult:
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
            return self.hand.get_hu_play_result()
        play_result: PlayResult = self.hand.resolve(action)
        if play_result.need_replacement:
            if tile_sequence.is_empty():
                return PlayResult(draw=True)
            tile = tile_sequence.replace(1)
            self.replacement_tile_count += self.hand.add_tiles(
                tile, "replace", action.action
            )
            replacement_result = self.resolve_tile_replacement(tile_sequence)
            if not replacement_result.complete:
                return PlayResult(draw=True)
            if self.hand.is_winning_hand():
                self.winning_conditions.append("杠上开花")
                return self.hand.get_hu_play_result()
            possible_discards = self.hand.get_discardable_tiles()
            discard_play_action = self.gang_discard_strategy(possible_discards)
            play_result = self.hand.resolve(discard_play_action)
        return play_result

    def play_turn_strategy(self, possible_actions, **kwargs) -> PlayAction:
        """
        implementation details:
        always return `PlayAction` object
        """
        raise NotImplementedError  # pragma: no cover

    def call_strategy(self, possible_actions, played_tile, **kwargs) -> PlayAction:
        """
        implementation details:
        always return `PlayAction` object
        """
        raise NotImplementedError  # pragma: no cover

    def gang_discard_strategy(self, possible_actions, **kwargs) -> PlayAction:
        # TODO to make in to general `discard_strategy`?
        raise NotImplementedError  # pragma: no cover

    def round_summary(self):
        """
        for winner to calculate fan,
        for other players to calculate how far they are from winning?
        """
        import calculate_fan

        self.result_fan = calculate_fan.ResultFan()
        calculate_fan.calculate_fan(
            self.result_fan,
            self.winning_conditions,
            self.hand.tiles_history,
            self.hand.tiles,
            self.hand.peng_history,
            self.hand.gang_history,
            self.hand.shang_history,
            self.hand.an_gang_history,
            self.hand.flower_tiles,
            self.hand.jiangs,
        )
        return


class DummyPlayer(Player):
    def __init__(self, player_idx, house=False, debug=False, strategy="dummy"):
        assert strategy in ["dummy", "random"]
        self.stragetgy = strategy
        self.debug = debug
        super().__init__(player_idx=player_idx, house=house)

    def play_turn_strategy(self, possible_actions):
        if self.debug:
            print(f"hand: {sorted(self.hand.tiles)}")
            print(f"peng_history: {self.hand.peng_history}")
            print(f"shang_history: {self.hand.shang_history}")
            print(f"gang_history: {self.hand.gang_history}")
        for action in possible_actions:
            if action.action == "hu":
                return action
        if self.stragetgy == "dummy":
            action = possible_actions[0]
        else:
            action = random.choice(possible_actions)
        if self.debug:
            print(f"turn action chosen: {action}")
        return action

    def call_strategy(self, possible_actions, played_tile):
        if not possible_actions:
            return []
        if self.debug:
            print(f"hand: {sorted(self.hand.tiles)}")
            print(f"played_tile: {played_tile}")
            print(f"peng_history: {self.hand.peng_history}")
            print(f"shang_history: {self.hand.shang_history}")
            print(f"gang_history: {self.hand.gang_history}")
        for action in possible_actions:
            if action.action == "hu":
                return action
        if self.stragetgy == "dummy":
            action = possible_actions[0]
        else:
            action = random.choice(possible_actions)
        if self.debug:
            print(f"call action chosen: {action}")
        return action

    def gang_discard_strategy(self, possible_actions) -> PlayAction:
        if self.debug:
            print(f"hand: {sorted(self.hand.tiles)}")
            print(f"gang_history: {self.hand.gang_history}")
        if self.stragetgy == "dummy":
            action = possible_actions[0]
        else:
            action = random.choice(possible_actions)
        if self.debug:
            print(f"gang discard action chosen: {action}")
        return action


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
