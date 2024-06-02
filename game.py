import random
import pickle
import json
import copy
from typing import Dict, List
from dataclasses import dataclass, field

from tiles import (
    HUAS,
    FENGS,
    Tiles,
    SHANG_LUT,
    SHANG_EXCLUDE,
    REVERSED_SHANG_LUT,
    SHANG_REF,
    SUITES,
)


class State:
    def save(self, pickled=True, json_format=False):
        if pickled:
            with open("save.pkl", "wb") as f:
                pickle.dump(self.__dict__.items(), f)
        if json_format:
            with open("save.json", "w") as f:
                json.dump(self.__dict__, f)

    def load(self, pickled=True, json_format=False):
        if pickled:
            with open("save.pkl", "rb") as f:
                for k, v in pickle.load(f):
                    setattr(self, k, v)
        if json_format:
            with open("save.json", "r") as f:
                for k, v in json.load(f).items():
                    setattr(self, k, v)


class TilesSequence(State):
    def __init__(self):
        self.tiles: list = []
        for card, count in Tiles.items():
            self.tiles += [card] * count
        self.initial_sequence = copy.deepcopy(self.tiles)

    def shuffle(self, start):
        random.shuffle(self.tiles)
        self.tiles = self.tiles[start:] + self.tiles[:start]

    def draw(self, total=1, jump=False):
        if jump:
            assert total == 2
            return [self.tiles.pop(0), self.tiles.pop(3)]
        else:
            assert total in [1, 4]

            if total == 1:
                return [self.tiles.pop(0)]
            else:
                return [self.tiles.pop(0) for _ in range(total)]

    def replace(self, total):
        """
        replace with last tile. used when there is a "gang" or getting a non
        playable tile
        """
        rv = []
        for _ in range(total):
            rv.append(self.tiles.pop(-1))
        return rv

    def is_empty(self):
        return len(self.tiles) == 0

    def only_flowers(self):
        rv = [1 if x in HUAS else 0 for x in self.tiles]
        if all(rv):
            return True
        return False


@dataclass
class PlayAction(State):
    """
    `PlayAction` is one of possible actions that a player can take
    after drawing a tile. It acts as a message to `Player` for
    `play_turn_strategy` and `call_strategy`.
    """

    action: str = None
    target_tile: str = None
    move_tiles: List[str] = field(default_factory=list)
    discard_tile: str = None
    is_jue_zhang: bool = False
    is_qiang_gang_hu: bool = False
    is_hai_di_lao_yue: bool = False
    hu_by: str = ""

    REQUIRED_DISCARD = ["peng", "shang", "discard"]

    def __post_init__(self):
        assert self.action in [
            "peng",
            "an_gang",
            "ming_gang",
            "jia_gang",
            "shang",
            "hu",
            "discard",
            "pass",
        ]
        if self.action in self.REQUIRED_DISCARD:
            assert self.discard_tile is not None


@dataclass
class PlayResult(State):
    """
    act as a message passing from `Hand` to `Player` for
    subsequent calls.
    """

    discarded_tile: str = None
    need_replacement: bool = False
    hu: bool = False
    draw: bool = False


@dataclass
class ReplacementResult(State):
    complete: bool = False


class Hand(State):
    """
    `Hand` class is a representation of a player's hand. It includes
    4 main methods to be called by `Player`:
    - `get_*_candidates`: to get possible actions
      - expected output is a list of `PlayAction` objects
    - `is_winning_hand`: to check if the hand is a winning hand
      - checked after each draw and in call check
    - `dp_search`: to search for winning hand i.e. inform player minimum
        change of times to win
      - `get_valid_*_sets` methods are supporting methods for `dp_search`
    """

    def __init__(self, player_idx: int, replacement_tiles=HUAS):
        self.tiles = []
        self.player_idx = player_idx
        self.replacement_tiles = [] if not replacement_tiles else replacement_tiles
        self.tiles_history = {}
        self.flower_tiles = []
        self.distinct_tile_count = {}
        self.peng_history = []
        self.gang_history = []
        self.an_gang_history = []
        self.shang_history = []

    def reset(self):
        self.tiles = []
        self.tiles_history = {}
        self.flower_tiles = []
        self.distinct_tile_count = {}
        self.peng_history = []
        self.gang_history = []
        self.an_gang_history = []
        self.shang_history = []

    def shang(self, action: PlayAction):
        for tile in action.move_tiles:
            self.remove_tile(tile, "shang-move")
            self.shang_history.append(tile)
        self.shang_history.append(action.target_tile)
        self.remove_tile(action.discard_tile, "shang-discard")
        return PlayResult(discarded_tile=action.discard_tile)

    def get_shang_candidates(self, played_tile, is_hu=False):
        if played_tile in SHANG_EXCLUDE:
            return []
        shang_candidates = []
        suite = played_tile[-1]
        corresponding_tiles = REVERSED_SHANG_LUT[played_tile[:-1]]
        for tile_group in corresponding_tiles:
            if (
                f"{tile_group[0]}{suite}" in self.tiles
                and f"{tile_group[1]}{suite}" in self.tiles
            ):
                free_tiles = copy.deepcopy(self.tiles)  # can deduplicate here
                free_tiles.remove(f"{tile_group[0]}{suite}")
                free_tiles.remove(f"{tile_group[1]}{suite}")
                for tile in free_tiles:
                    shang_candidates.append(
                        PlayAction(
                            action="hu" if is_hu else "shang",
                            target_tile=played_tile,
                            move_tiles=[
                                f"{tile_group[0]}{suite}",
                                f"{tile_group[1]}{suite}",
                            ],
                            discard_tile=tile,
                            hu_by="shang" if is_hu else "",
                        )
                    )
                free_tiles = None
        return shang_candidates

    def is_locked(self, tile):
        free_tiles = self._get_discardable_tiles()
        if not free_tiles:
            return True
        if tile in free_tiles:
            return False
        return True

    def peng(self, action: PlayAction):
        for tile in action.move_tiles:
            self.remove_tile(tile, "peng-move")
        self.peng_history += [action.target_tile] * 3
        self.distinct_tile_count[action.target_tile] = 3
        self.remove_tile(action.discard_tile, "peng-discard")
        return PlayResult(discarded_tile=action.discard_tile)

    def get_peng_candidates(self, played_tile, is_hu=False):
        discardables = self._get_discardable_tiles(
            exclude_tile=played_tile, exclude_all=True
        )
        if (
            played_tile not in self.distinct_tile_count
            or self.distinct_tile_count[played_tile] != 2
        ):
            return []
        return (
            [
                PlayAction(
                    action="hu" if is_hu else "peng",
                    target_tile=played_tile,
                    move_tiles=[played_tile, played_tile],
                    discard_tile=discard_tile,
                    hu_by="peng" if is_hu else "",
                )
                for discard_tile in discardables
            ]
            if self.distinct_tile_count[played_tile] == 2
            else []
        )

    def gang(self, action: PlayAction):
        """
        ming_gang: hand 3 + call
        jia_gang: peng + draw
        an_gang: hand 4
        """
        if action.action == "ming_gang":
            for tile in action.move_tiles:
                self.remove_tile(tile, "ming-gang-move")
            self.gang_history += [action.target_tile] * 4
            self.distinct_tile_count[action.target_tile] = 4
        elif action.action == "an_gang":
            for tile in action.move_tiles:
                self.remove_tile(tile, "an-gang-move")
            self.an_gang_history += [action.move_tiles[0]] * 4
            self.distinct_tile_count[action.move_tiles[0]] = 4
        elif action.action == "jia_gang":
            for tile in action.move_tiles:
                self.peng_history.remove(tile)
            self.remove_tile(action.target_tile, "jia-gang-move")
            self.gang_history += [action.target_tile] * 4
            self.distinct_tile_count[action.target_tile] = 4
        return PlayResult(need_replacement=True)

    def get_gang_candidates(self, played_tile=None, drawed_tile=None, is_hu=False):
        check = played_tile if played_tile else drawed_tile
        # ensuring the tile is in the hand
        if not check:
            return []
        if check not in self.distinct_tile_count.keys():
            return []
        if played_tile:
            return (
                [
                    PlayAction(
                        action="hu" if is_hu else "ming_gang",
                        target_tile=played_tile,
                        move_tiles=[played_tile, played_tile, played_tile],
                        hu_by="ming_gang" if is_hu else "",
                    )
                ]
                if self.distinct_tile_count[played_tile] == 3
                and not self.is_locked(played_tile)
                else []
            )
        elif drawed_tile:
            if drawed_tile in self.peng_history:
                action = "jia_gang"
                return [
                    PlayAction(
                        action="hu" if is_hu else action,
                        target_tile=drawed_tile,
                        move_tiles=[drawed_tile, drawed_tile, drawed_tile],
                        hu_by="jia_gang" if is_hu else "",
                    )
                ]
            elif self.distinct_tile_count[drawed_tile] == 4:
                action = "an_gang"
                return [
                    PlayAction(
                        action="hu" if is_hu else action,
                        move_tiles=[drawed_tile, drawed_tile, drawed_tile, drawed_tile],
                        hu_by="an_gang" if is_hu else "",
                    )
                ]
            else:
                return []

    def resolve(self, action: PlayAction) -> PlayResult:
        resolve_to = (
            action.action if "_" not in action.action else action.action.split("_")[1]
        )
        fn = getattr(self, resolve_to)
        self.tiles_history[f"{len(self.tiles_history)}-resolve"] = str(action)
        result: PlayResult = fn(action)
        return result

    def discard(self, action: PlayAction):
        self.remove_tile(action.discard_tile, "turn-discard")
        return PlayResult(discarded_tile=action.discard_tile)

    def _get_discardable_tiles(self, exclude_tile=None, exclude_all=False):
        """
        private method to address `peng` but allows `shang`
        """
        non_locked_tiles: list = copy.deepcopy(self.tiles)

        if exclude_tile not in non_locked_tiles:  # TODO add test
            return non_locked_tiles
        if exclude_all:
            for _ in range(self.distinct_tile_count[exclude_tile]):
                non_locked_tiles.remove(exclude_tile)
            return non_locked_tiles
        if exclude_tile:
            non_locked_tiles.remove(exclude_tile)
        return non_locked_tiles

    def get_discardable_tiles(self):
        return [
            PlayAction(action="discard", discard_tile=tile)
            for tile in self._get_discardable_tiles()
        ]

    def add_tiles(self, tiles: List, method: str = "") -> int:
        """
        add tile to hand

        Args:
        tiles: list of tiles to be added to hand (expected to be a list,
        check `draw` and `replace` method in `TilesSequence` class)

        Returns:
        replacement_tile_count: number of replacement tiles added to hand
        """
        replacement_tile_count = 0
        self.tiles_history[f"{len(self.tiles_history)}-{method}-add"] = tiles
        for tile in tiles:
            if tile in self.replacement_tiles:
                self.flower_tiles.append(tile)
                replacement_tile_count += 1
            else:
                self.tiles.append(tile)
                if tile not in self.distinct_tile_count:
                    self.distinct_tile_count[tile] = 1
                else:
                    self.distinct_tile_count[tile] += 1
        return replacement_tile_count

    def remove_tile(self, tile, method: str = ""):
        """
        Args:
        tile: tile to be removed from hand

        Returns:
        tile: tile that is removed
        """
        self.tiles.remove(tile)
        self.distinct_tile_count[tile] -= 1
        assert self.distinct_tile_count[tile] >= 0
        self.tiles_history[f"{len(self.tiles_history)}-{method}-remove"] = tile
        return tile

    def get_valid_eye_sets(self, free_tiles):
        rv = []
        distinct_tile_count = {}
        for tiles in free_tiles:
            if tiles not in distinct_tile_count:
                distinct_tile_count[tiles] = 1
            else:
                distinct_tile_count[tiles] += 1
        return [k for k, v in distinct_tile_count.items() if v >= 2]

    def get_valid_shang_sets(self, remaining_tiles):
        """
        return list of valid shang sets and remaining tiles
        """
        valid_shang_sets = []
        for s in SUITES:
            distinct_tiles = {}
            for tile in remaining_tiles:
                if tile.endswith(s):
                    if tile not in distinct_tiles:
                        distinct_tiles[tile[:-1]] = 1
                    else:
                        distinct_tiles[tile[:-1]] += 1
            for group in SHANG_REF:
                if all([x in distinct_tiles for x in group]):
                    candidates = []
                    for x in group:
                        candidates.append(x)
                    valid_shang_sets.append([f"{x}{s}" for x in candidates])
        return valid_shang_sets

    def get_valid_peng_sets(self, remaining_tiles: list):
        valid_peng_sets = []
        distinct_tile = set(remaining_tiles)
        for tile in distinct_tile:
            if remaining_tiles.count(tile) == 3:
                valid_peng_sets.append([tile] * 3)
        return valid_peng_sets

    def _dp_search(self, remaining_tiles: list):
        if not remaining_tiles:
            return True

        rv = False
        valid_shang_sets = self.get_valid_shang_sets(remaining_tiles)
        valid_peng_sets = self.get_valid_peng_sets(remaining_tiles)
        valid_sets = valid_shang_sets + valid_peng_sets

        # implies not able to form any sets of 3
        if not valid_sets:
            return rv

        for valid_set in valid_sets:
            new_remaining_tiles = copy.deepcopy(remaining_tiles)
            for tile in valid_set:
                new_remaining_tiles.remove(tile)
            rv = self._dp_search(new_remaining_tiles)
            if rv:
                return rv
        return rv

    def dp_search(self, tiles):
        """
        basic check if the hand is a winning hand
        """
        rv = False

        # save guard, technically should not be called
        if len(tiles) % 3 != 2:
            raise ValueError(f"invalid hand: {tiles}")

        valid_eye_sets = self.get_valid_eye_sets(tiles)
        if not valid_eye_sets:
            return rv
        else:
            for eye_set in valid_eye_sets:
                tmp_tiles = copy.deepcopy(tiles)
                for _ in range(2):
                    tmp_tiles.remove(eye_set)

                rv = self._dp_search(tmp_tiles)
                if rv:
                    return rv
        return rv

    def is_winning_hand(self, call_tile=None):
        # 十三幺
        distinct_tiles = list(set(self.tiles))
        if sorted(distinct_tiles) == sorted(
            ["1万", "9万", "1筒", "9筒", "1索", "9索", "东", "南", "西", "北", "白", "發", "中"]
        ) and (
            sum([x == 2 for x in self.distinct_tile_count.values()]) == 1
            and sum([x == 1 for x in self.distinct_tile_count.values()]) == 12
        ):
            return True
        # 对对胡
        elif all([x == 2 for x in self.distinct_tile_count.values() if x > 0]):
            return True
        tiles = copy.deepcopy(self.tiles)
        if call_tile:
            tiles.append(call_tile)
        return self.dp_search(tiles)

    def get_hu_play_result(self):
        return PlayResult(hu=True)

    def get_showable_tiles(self):
        return self.gang_history + self.peng_history + self.shang_history


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
        self.replacement_tile_count += self.hand.add_tiles(tiles, "init-draw")

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
            self.replacement_tile_count += self.hand.add_tiles(drawed_tile, "turn-draw")
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
                tile, f"{action.action}-replace"
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
            self.hand.add_tiles([action.target_tile], f"hu-{action.hu_by}")
            return self.hand.get_hu_play_result()
        play_result: PlayResult = self.hand.resolve(action)
        if play_result.need_replacement:
            if tile_sequence.is_empty():
                return PlayResult(draw=True)
            tile = tile_sequence.replace(1)
            self.replacement_tile_count += self.hand.add_tiles(
                tile, f"{action.action}-replace"
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

    def gang_discard_strategy(self, possible_actions) -> PlayAction:
        # TODO to make in to general `discard_strategy`?
        raise NotImplementedError  # pragma: no cover

    def round_summary(self):
        """
        for winner to calculate fan,
        for other players to calculate how far they are from winning?
        """
        import calculate_fan

        self.result_fan = calculate_fan.ResultFan()
        calculate_fan.calculate_win_mode_fan(
            self.result_fan,
            self.winning_conditions,
            self.hand.tiles_history,
            self.hand.tiles,
            self.hand.distinct_tile_count,
            self.hand.peng_history,
            self.hand.gang_history,
            self.hand.shang_history,
            self.hand.an_gang_history,
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


class Mahjong:
    def __init__(self, players: Dict[int, Player]):
        self.players: Dict[int, Player] = players
        self.tile_sequence = None
        self.current_player_idx = 0
        self.round_player_sequence = []
        self.current_round_sequence = 0
        self.winner = None
        self.discarded_pool = []  # TODO testing
        self.debug = False
        self.quan_feng = None
        self.FENGS = FENGS
        self.current_game_round = -1

    def reset(self):
        self.tile_sequence = TilesSequence()
        self.current_round_sequence = 0
        self.winner = None
        self.discarded_pool = []
        self.quan_feng = None
        for player in self.players.values():
            player.hand.reset()

    def start(self):
        # throw dice twice
        self.current_game_round += 1
        val_player_sequence = random.randint(1, 13)
        # 东 0 南 1 西 2 北 3
        self.current_player_idx = (val_player_sequence - 1) % 4
        self.players[self.current_player_idx].house = True
        self.round_player_sequence = [x for x in range(self.current_player_idx, 4)] + [
            x for x in range(0, self.current_player_idx)
        ]
        for feng, player_idx in zip(self.FENGS, self.round_player_sequence):
            self.players[player_idx].men_feng = feng
        self.quan_feng = self.FENGS[self.current_game_round % 4]

        val_start_sequence = random.randint(1, 13) + val_player_sequence
        self.tile_sequence.shuffle(val_start_sequence)

    def start_game(self):
        self.reset()
        self.start()
        self.deal()
        self.play()
        self.round_summary()

    def start_full_game(self):
        while self.current_game_round < 15:
            self.start_game()

    def deal(self):
        # (4, 4, 4) * 3, 2 跳, 1, 1, 1
        for _ in range(3):
            for player_idx in self.round_player_sequence:
                player: Player = self.players[player_idx]
                player.initial_draw(self.tile_sequence, 4, False)
        for player_idx in self.round_player_sequence:
            player: Player = self.players[player_idx]
            if player.house:
                player.initial_draw(self.tile_sequence, 2, True)
            else:
                player.initial_draw(self.tile_sequence, 1, False)
        for player_idx in self.round_player_sequence:
            player: Player = self.players[player_idx]
            player.resolve_tile_replacement(self.tile_sequence)

    def resolve_call_priority(self, responses):
        """
        hu > peng/gang > shang
        multiple players can hu, player who sits right (1st) to the player that
        played tile wins
        ```
        responses = {
            "hu": [[0, PlayAction], [1, PlayAction]],
            "peng": [0, PlayAction],
        }
        ```
        """
        is_qiang_gang_hu = False
        if "hu" in responses:
            if "ming_gang" in responses or "jia_gang" in responses:
                is_qiang_gang_hu = True
            if len(responses["hu"]) > 1:
                hu_order = [x for x in range(self.current_player_idx, 4)] + [
                    x for x in range(0, self.current_player_idx)
                ]
                # e.g. 2 3 0 1
                for player_idx in hu_order:
                    for response in responses["hu"]:
                        if player_idx == response[0]:
                            player_idx = response[0]
                            play_action = response[1]
                            play_action.is_qiang_gang_hu = is_qiang_gang_hu
                            return [player_idx, play_action]
            else:
                player_idx = responses["hu"][0][0]
                play_action: PlayAction = responses["hu"][0][1]
                play_action.is_qiang_gang_hu = is_qiang_gang_hu
                return [player_idx, play_action]
        elif "peng" in responses:
            return responses["peng"]
        elif "ming_gang" in responses:
            return responses["ming_gang"]
        elif "jia_gang" in responses:
            return responses["jia_gang"]
        elif (
            "an_gang" in responses
        ):  # TODO technically an_gang is not need to resolve here
            return responses["an_gang"]
        elif "shang" in responses:
            return responses["shang"]
        else:
            raise ValueError(
                "no valid response"
            )  # pragma: no cover; for brute force testing

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
        play_result: PlayResult = self.players[resolve_to].call_resolve(
            play_action, self.tile_sequence
        )
        return play_result, resolve_to

    def play_one_round(self):
        current_player = self.players[self.current_player_idx]
        play_result: PlayResult = current_player.play_turn(self.tile_sequence)
        if play_result.hu:
            self.winner = current_player.player_idx
            return
        elif play_result.draw:
            return

        check_responses = {}
        while True:
            for _, player in self.players.items():
                if player.player_idx == current_player.player_idx:
                    continue
                player: Player
                play_action = player.call(
                    play_result.discarded_tile, current_player.player_idx
                )
                if not play_action:
                    continue
                if (
                    play_action.action == "hu"
                    and play_action.action not in check_responses
                ):
                    check_responses[play_action.action] = [
                        [player.player_idx, play_action]
                    ]
                elif (
                    play_action.action == "hu" and play_action.action in check_responses
                ):
                    check_responses[play_action.action].append(
                        [player.player_idx, play_action]
                    )
                else:
                    check_responses[play_action.action] = [
                        player.player_idx,
                        play_action,
                    ]
            if not check_responses:
                self.discarded_pool.append(play_result.discarded_tile)
                next_player_idx = current_player.next_player_idx
                break
            elif len(check_responses) >= 1:
                play_result, resolve_to = self.resolve_call(check_responses)
                if play_result.hu:
                    self.winner = resolve_to
                    return
                elif play_result.draw:
                    return
                elif play_result.discarded_tile:
                    discarded_tile = play_result.discarded_tile
                    self.discarded_pool.append(discarded_tile)
                    current_player = self.players[resolve_to]
                elif play_result.need_replacement:
                    # TODO break didnt work previously, check if ever branched here
                    raise ValueError(
                        "replacement should be resolved at Player"
                    )  # pragma: no cover; for brute force testing
            else:
                raise ValueError(
                    "invalid response"
                )  # pragma: no cover; for brute force testing
            check_responses = {}

        self.current_round_sequence += 1
        self.current_player_idx = next_player_idx

    def play(self):
        while not self.winner:
            if self.tile_sequence.is_empty():
                break
            self.play_one_round()
            if self.winner is not None:
                break

    def round_summary(self):
        if self.winner is not None:
            self.players[self.winner].round_summary()
