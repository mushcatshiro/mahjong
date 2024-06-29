import copy
from typing import List

from tiles import (
    HUAS,
    SHANG_EXCLUDE,
    REVERSED_SHANG_LUT,
    SHANG_REF,
    SUITES,
)

from save_state import State
from model import PlayAction, PlayResult
import calculate_fan


__all__ = ["Hand"]


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
        self.jiangs = ""

    def reset(self):
        self.tiles = []
        self.tiles_history = {}
        self.flower_tiles = []
        self.distinct_tile_count = {}
        self.peng_history = []
        self.gang_history = []
        self.an_gang_history = []
        self.shang_history = []
        self.jiangs = ""

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
        self.tiles_history[f"{len(self.tiles_history)}"] = {
            "action": "resolve",
            "play_action": action.action,
        }
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

    def add_tiles(self, tiles: List, action: str = "add", play_action: str = "") -> int:
        """
        add tile to hand

        Args:
        tiles: list of tiles to be added to hand (expected to be a list,
        check `draw` and `replace` method in `TilesSequence` class)

        Returns:
        replacement_tile_count: number of replacement tiles added to hand
        """
        replacement_tile_count = 0
        self.tiles_history[f"{len(self.tiles_history)}"] = {
            "action": action,
            "play_action": play_action,
            "tile": tiles,
        }
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
        if self.distinct_tile_count[tile] == 0:
            del self.distinct_tile_count[tile]
        self.tiles_history[f"{len(self.tiles_history)}"] = {
            "action": "remove",
            "play_action": method,
            "tile": tile,
        }
        return tile

    def get_valid_jiangs(self, free_tiles):
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

        valid_jiangs = self.get_valid_jiangs(tiles)
        if not valid_jiangs:
            return rv
        else:
            for jiangs in valid_jiangs:
                tmp_tiles = copy.deepcopy(tiles)
                for _ in range(2):
                    tmp_tiles.remove(jiangs)

                rv = self._dp_search(tmp_tiles)
                if rv:
                    self.jiangs = jiangs
                    return rv
        return rv

    def is_winning_hand(self, call_tile=None):
        tiles = copy.deepcopy(self.tiles)
        if call_tile:
            tiles.append(call_tile)
        # 十三幺 TODO bring back
        if calculate_fan.fan.shi_san_yao(tiles):
            return True
        # 对对胡
        distinct_tiles = calculate_fan.get_distinct_tiles(tiles)
        if calculate_fan.check_qi_dui_hu(distinct_tiles):
            return True
        return self.dp_search(tiles)

    def get_hu_play_result(self):
        return PlayResult(hu=True)

    def get_showable_tiles(self):
        return self.gang_history + self.peng_history + self.shang_history

    def get_hand(self, use_oracle=False):
        # hand = [self.gang_history, self.peng_history, self.shang_history]
        # if use_oracle:
        #     hand = [self.tiles + self.flower_tiles] + hand + self.an_gang_history
        # else:
        #     hand = [self.flower_tiles] + hand
        # return hand
        return self.distinct_tile_count
