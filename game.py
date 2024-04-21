import random
import pickle
import copy
from typing import Dict, List
from dataclasses import dataclass, field

DEFAULT_REPLACEMENT_TILES = ("春", "夏", "秋", "冬", "梅", "蘭", "菊", "竹")


Tiles = {
    "1万": 4,
    "2万": 4,
    "3万": 4,
    "4万": 4,
    "5万": 4,
    "6万": 4,
    "7万": 4,
    "8万": 4,
    "9万": 4,
    "1筒": 4,
    "2筒": 4,
    "3筒": 4,
    "4筒": 4,
    "5筒": 4,
    "6筒": 4,
    "7筒": 4,
    "8筒": 4,
    "9筒": 4,
    "1索": 4,
    "2索": 4,
    "3索": 4,
    "4索": 4,
    "5索": 4,
    "6索": 4,
    "7索": 4,
    "8索": 4,
    "9索": 4,
    "東": 4,
    "南": 4,
    "西": 4,
    "北": 4,
    "白": 4,
    "發": 4,
    "中": 4,
    "春": 1,
    "夏": 1,
    "秋": 1,
    "冬": 1,
    "梅": 1,
    "蘭": 1,
    "菊": 1,
    "竹": 1,
}

SHANG_LUT = {
    "12": ["3"],
    "13": ["2"],
    "23": ["1", "4"],
    "24": ["3"],
    "34": ["2", "5"],
    "35": ["4"],
    "45": ["3", "6"],
    "46": ["5"],
    "56": ["4", "7"],
    "57": ["6"],
    "67": ["5", "8"],
    "68": ["7"],
    "78": ["6", "9"],
    "79": ["8"],
    "89": ["7"],
}

SHANG_REF = [
    "123",
    "234",
    "345",
    "456",
    "567",
    "678",
    "789",
]

SUITES = ["万", "筒", "索"]


class State:
    """
    consider the following:
    state = [
        [0, 0, 0, 0,],
        [0, 0, 0, 0,],
        [0, 0, 0, 0,],
        [0, 0, 0, 0,],
        ...
    ]
    where state.shape = (36, 4)
    with a series of mask that allows us to check the state of the game including
    - tiles played by player i in (0, 1, 2, 3),
    - tiles owned
    - action space and action taken?

    action space:
    - peng
    - gang
    - shang
    - discard
    - hu

    converter between human readable state and machine readable state
    """

    def save(self, pickle=True):
        if not pickle:
            return self.__dict__.items()
        else:
            with open("save.pkl", "wb") as f:
                pickle.dump(self.__dict__.items(), f)


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


@dataclass
class PlayAction(State):
    """
    `PlayAction` is one of possible actions that a player can take
    after drawing a tile. It acts as a message to `Player` for
    `play_turn_strategy` and `call_strategy` The actions includes:
    - peng
    - gangs
    - shang
    - hu
    - discard
    """

    resolve: bool = False
    action: str = None
    target_tile: str = None
    add_tile: bool = False
    discard_tile: str = None
    RESOLVABLE_ACTIONS = [
        "peng",
        "ming_gang",
        "jia_gang",
        "an_gang",
        "shang",
        "hu",
    ]
    REQUIRED_DISCARD = ["peng", "shang"]

    def __post_init__(self):
        if self.resolve:
            assert self.target_tile is not None
            assert self.action in self.RESOLVABLE_ACTIONS
            if self.action in self.REQUIRED_DISCARD:
                assert self.discard_tile is not None
        else:
            assert self.action not in self.RESOLVABLE_ACTIONS
            assert self.discard_tile is not None


@dataclass
class PossibleActions(State):
    actions: List[PlayAction] = field(default_factory=list)


@dataclass
class PlayResult(State):
    """
    act as a message passing from `Hand` to `Player` for
    subsequent calls.
    """

    discarded_tile: str = None
    need_replacement: bool = False


class Hand(State):
    def __init__(self, player_idx: int, replacement_tiles=DEFAULT_REPLACEMENT_TILES):
        self.tiles = []
        self.player_idx = player_idx
        self.tiles_history = {}
        self.replacement_tiles = [] if not replacement_tiles else replacement_tiles
        self.flower_tiles = []
        self.distinct_tile_count = {}
        # TODO remove these 3 and make it `locked_tiles`
        # `locked_tiles` can have duplicates and is used to remove exact tiles from
        # `self.tiles`
        self.peng_history = []
        self.gang_history = []
        self.shang_history = []

    def shang(self, action: PlayAction):
        # TODO not tested
        self.shang_history += action.target_tile  # BUG `target_tile` is a list
        self.add_tiles(action.add_tile)  # BUG `add_tile` was bool but now is a tile
        self.remove_tile(action.discard_tile)
        return PlayResult(discarded_tile=action.discard_tile)

    def get_shang_candidates(self):
        shang_candidates = []
        for s in SUITES:
            # BUG peng and gang history entry can be duplicated
            candidates = sorted(
                list(
                    set(
                        [
                            x.replace(s, "")
                            for x in self.tiles
                            if x.endswith(s)
                            and x not in self.peng_history + self.gang_history
                        ]
                    )
                )
            )
            bptr = 0
            fptr = 2
            while fptr <= len(candidates):
                combination = "".join(candidates[bptr:fptr])
                if combination in SHANG_LUT:
                    shang_candidates += [f"{x}{s}" for x in SHANG_LUT[combination]]
                bptr += 1
                fptr += 1
        return shang_candidates

    def is_locked(self, tile):
        if tile in self.peng_history or tile in self.gang_history:
            return True
        return False

    def get_eye_candidates(self):
        return [
            k
            for k, v in self.distinct_tile_count.items()
            if v >= 2 and not self.is_locked(k)
        ]

    def peng(self, action: PlayAction):
        self.peng_history.append(action.target_tile)
        if action.add_tile:
            self.add_tiles([action.target_tile])
        self.remove_tile(action.discard_tile)
        return PlayResult(discarded_tile=action.discard_tile)

    def get_peng_candidates(self, played_tile=None):
        """
        if args `played_tile` is provided, assuming is in a call state.
        """
        if played_tile:
            discardables = self.get_discardable_tiles(exclude_tile=played_tile)
            return (
                [
                    PlayAction(
                        resolve=True,
                        action="peng",
                        target_tile=played_tile,
                        add_tile=True,
                        discard_tile=discard_tile,
                    )
                    for discard_tile in discardables
                ]
                if self.distinct_tile_count[played_tile] == 2
                else []
            )
        rv = []
        for tile, tile_count in self.distinct_tile_count.items():
            if tile_count == 3:
                rv += [
                    PlayAction(
                        resolve=True,
                        action="peng",
                        target_tile=tile,
                        discard_tile=discard_tile,
                    )
                    for discard_tile in self.get_discardable_tiles(exclude_tile=tile)
                ]
        return rv

    def gang(self, action: PlayAction):
        """
        ming_gang: hand 3 + call
        jia_gang: peng + draw
        an_gang: hand 4
        """
        if action.add_tile:
            self.add_tiles([action.target_tile])
        self.gang_history.append(action.target_tile)
        return PlayResult(need_replacement=True)

    def get_gang_candidates(self, played_tile=None, drawed_tile=None):
        """ """
        check = played_tile if played_tile else drawed_tile
        if check not in self.distinct_tile_count.keys():
            return []
        if played_tile:
            return (
                [
                    PlayAction(
                        resolve=True,
                        action="ming_gang",
                        add_tile=True,
                        target_tile=played_tile,
                    )
                ]
                if self.distinct_tile_count[played_tile] == 3
                else []
            )
        elif drawed_tile:
            if drawed_tile in self.peng_history:
                action = "jia_gang"
            elif self.distinct_tile_count[drawed_tile] == 4:
                action = "an_gang"
            else:
                return []  # for completeness
            return [PlayAction(resolve=True, action=action, target_tile=drawed_tile)]
        return []

    def resolve(self, action: PlayAction) -> PlayResult:
        resolve_to = (
            action.action if "_" not in action.action else action.action.split("_")[1]
        )
        fn = getattr(self, resolve_to)
        result: PlayResult = fn(action)
        return result

    def get_discardable_tiles(self, exclude_tile=None):
        """
        situation where player can discard a tile
        """
        # TODO potentially useless if condition
        if type(exclude_tile) != list:
            exclude_tile = [exclude_tile]
        # BUG peng and gang history entry can be duplicated
        return [
            x
            for x in self.tiles
            if x not in self.peng_history + exclude_tile + self.gang_history
        ]

    def add_tiles(self, tiles: List) -> int:
        """
        add tile to hand

        Args:
        tiles: list of tiles to be added to hand (expected to be a list,
        check `draw` and `replace` method in `TilesSequence` class)

        Returns:
        replacement_tile_count: number of replacement tiles added to hand
        """
        replacement_tile_count = 0
        self.tiles_history[f"{len(self.tiles_history)}add"] = tiles
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

    def remove_tile(self, tile):
        """
        Args:
        tile: tile to be removed from hand

        Returns:
        tile: tile that is removed
        """
        self.tiles.remove(tile)
        self.distinct_tile_count[tile] -= 1
        assert self.distinct_tile_count[tile] >= 0
        self.tiles_history[f"{len(self.tiles_history)}remove"] = tile
        return tile

    def get_valid_shang_sets(self, remaining_tiles):
        tiles = sorted(tiles)
        valid_shang_sets = []
        for s in SUITES:
            candidates = sorted(
                list(
                    set(
                        x
                        for x in tiles
                        if x.endswith(s)
                        and x not in self.peng_history + self.gang_history
                    )
                )
            )
            bptr = 0
            fptr = 3
            while fptr <= len(candidates):
                combination = "".join([x.replace(s, "") for x in candidates[bptr:fptr]])
                if combination in SHANG_REF:
                    valid_shang_sets.append([x for x in candidates[bptr:fptr]])
                bptr += 1
                fptr += 1
        return valid_shang_sets

    def get_valid_peng_sets(self):
        valid_peng_sets = []
        for tile, tile_count in self.distinct_tile_count.items():
            if tile_count == 3:
                valid_peng_sets.append(tile)
        return valid_peng_sets

    def get_valid_gang_sets(self):
        valid_gang_sets = []
        for tile, tile_count in self.distinct_tile_count.items():
            if tile_count == 4:
                valid_gang_sets.append(tile)
        return valid_gang_sets

    def _dp_search(self, remaining_tiles: list):
        """
        assuming there are correct number of tiles
        dp search for winning hand
        find 3 or gang and see what is left
        - left 2 -> eyes?
        - left > 2 and < 8/9 (excluding gang 4th tile)
          - has eyes?
          - check what's missing
        """
        combinations = []
        if len(remaining_tiles) == 2:
            return remaining_tiles

        valid_shang_sets = self.get_valid_shang_sets(remaining_tiles)

        if not valid_shang_set:
            return []
        if len(valid_shang_sets) == 1:
            return remaining_tiles

        for valid_shang_set in valid_shang_sets:
            thread = []
            remaining_tiles = copy.deepcopy(remaining_tiles)
            for tile in valid_shang_set:
                remaining_tiles.remove(tile)
            valid_set = self._dp_search(remaining_tiles)
            if valid_set:
                thread += valid_set
            combinations.append(thread)
        return combinations

    def dp_search(self):
        tiles = copy.deepcopy(self.tiles)
        tiles = sorted(tiles)

        valid_gang_sets = self.get_valid_gang_sets()
        valid_peng_sets = self.get_valid_peng_sets()

        if valid_gang_sets:
            for gang_set in valid_gang_sets:
                for _ in range(4):
                    tiles.remove(gang_set)

        if valid_peng_sets:
            for peng_set in valid_peng_sets:
                for _ in range(3):
                    tiles.remove(peng_set)

        combinations = self._dp_search(tiles)
        for thread in combinations:
            if valid_gang_sets:
                for gang_set in valid_gang_sets:
                    # TODO should be wrong, append might not be in place
                    thread.append([gang_set * 4])
            if valid_peng_sets:
                for peng_set in valid_peng_sets:
                    thread.append([peng_set * 3])
        rv = {}
        for thread in combinations:
            l = len(thread)
            if l not in rv:
                rv[l] = [thread]
            else:
                rv[l].append(thread)
        return rv

    def is_winning_hand(self):
        # 十三幺
        distinct_tiles = list(self.distinct_tile_count.keys())
        if sorted(distinct_tiles) == sorted(
            ["1万", "9万", "1筒", "9筒", "1索", "9索", "东", "南", "西", "北", "白", "發", "中"]
        ) and (
            sum([x == 2 for x in self.distinct_tile_count.values()]) == 1
            and sum([x == 1 for x in self.distinct_tile_count.values()]) == 12
        ):
            return True
        # 对对胡
        elif all([x == 2 for x in self.distinct_tile_count.values()]):
            return True
        elif len(self.tiles) % 3 != 2:
            return False
        # basic winning condition 3 sets of 3 (peng/gang or shang) + 1 pair
        # gang will be considered as 3
        # if (
        #     len(self.tiles) % 3 == 2
        #     and
        # ):

        return False


class Player(State):
    def __init__(self, player_idx, house=False):
        # TODO add player turn count/call count?
        self.player_idx = player_idx
        self.previous_player = (player_idx - 1) % 4  # TODO validate
        self.next_player = (player_idx + 1) % 4  # TODO validate
        self.hand = Hand(player_idx)
        self.action_history = []
        self.house = house
        self.pending_resolve = None

    def initial_draw(self, tile_sequence: TilesSequence, total, jump):
        tiles = tile_sequence.draw(total, jump)
        self.hand.add_tiles(tiles)

    def _replace_tiles(self, tile_sequence: TilesSequence):
        """
        TODO
        - test
          hand "春 夏"
          got replacement "秋 冬"
          then get two more replacement "1 2"
          instead of getting 4 in a go
        - check for non dealing stage replacement is always 1?
        """
        total = len(self.hand.flower_tiles[self.hand.non_playable_tiles_ptr :])
        replaced_tiles = tile_sequence.replace(total)
        self.hand.add_tiles(replaced_tiles, total)
        return replaced_tiles

    def resolve_tile_replacement(self, tile_sequence: TilesSequence, drawed_tile=None):
        while True:
            if len(self.hand.flower_tiles) > self.hand.non_playable_tiles_ptr:
                drawed_tile = self._replace_tiles(tile_sequence)
            else:
                break
        return drawed_tile

    def play_turn(self, tile_sequence: TilesSequence):
        self.pending_resolve = None  # reset
        self.possible_actions = None

        drawed_tile = tile_sequence.draw()
        self.hand.add_tiles(drawed_tile)

        drawed_tile = self.resolve_tile_replacement(tile_sequence, drawed_tile)

        self.possible_actions: PossibleActions = PossibleActions()
        self.draw_check(drawed_tile)
        self.get_discardable_tiles()
        action: PlayAction = self.play_turn_strategy()
        if action.resolve:
            self.pending_resolve = getattr(self, f"resolve_{action.action}")
            self.resolve(
                action.target_tile,
                action.discard_tile,
                tile_sequence if action.tile_sequence else None,
            )
            return action.discard_tile
        else:
            self.hand.remove_tile(action.discard_tile)
            return action.discard_tile
        # TODO mandatory discard?

    def call(self, played_tile, player):
        self.pending_resolve = None

        possible_actions = self.call_check(played_tile, player)
        action: PlayAction = self.call_strategy(possible_actions, played_tile)
        self.pending_resolve = (
            getattr(self, f"resolve_{action.action}") if action.action else None
        )
        # TODO mandatory discard?
        return action.action

    def play_turn_strategy(self, possible_actions, input_tile):
        """
        implementation details:
        always return `PlayAction` object
        set `self.pending_resolve` to the function that will be called if `resolve` is True
        """
        raise NotImplementedError

    def call_strategy(self, possible_actions, played_tile):
        """
        implementation details:
        always return `PlayAction` object
        set `self.pending_resolve` to the function that will be called if `resolve` is True
        """
        raise NotImplementedError

    def round_summary(self):
        """
        for winner to calculate fan,
        for other players to calculate how far they are from winning?
        """
        return


class DummyPlayer(Player):
    def play_turn_strategy(self, possible_actions, drawed_tile):
        return PlayAction(discard_tile=drawed_tile)

    def call_strategy(self, possible_actions, played_tile):
        return {"action": None}


class HumanPlayer(Player):
    def play_turn_strategy(self, possible_actions, drawed_tile):
        print(f"hand: {self.hand.tiles}")
        print(f"possible actions: {possible_actions}")
        resp = input("Enter 'resolve' or 'discard: ")
        assert resp in ["resolve", "discard"]
        if resp == "resolve":
            resp = input("Enter 'input_tile discard_tile': ")
            return {
                "resolve": True,
                "input_tile": resp.split()[0],
                "discard_tile": resp.split()[1],
                "tile_sequence": False,
            }
        return resp


class Mahjong:
    """
    TODO
    - 东南西北圈/一局16盘
    - backend numpy/torch or human readable
    - simple visualization with print example below,

      current round sequence 9,
      idx house? hand          discarded
      2   True   ""
      3   False  "1万 2万 3万" "4万"
      0   False  "1万 2万 3万" "4万 5万 6万"
      1   False  "1万 2万 3万" "4万 5万 6万 7万"
      note, discarded tiles are segregated by player
    """

    def __init__(self, players: Dict[int, Player]):
        self.players: Dict[int, Player] = players
        self.tile_sequence = TilesSequence()
        self.current_player_idx = 0
        self.round_player_sequence = []
        self.current_round_sequence = 0
        self.winner = None

    def start(self):
        # throw dice twice
        val_player_sequence = random.randint(1, 13)
        # 东 0 南 1 西 2 北 3
        self.current_player_idx = (val_player_sequence - 1) % 4
        self.players[self.current_player_idx].house = True
        self.round_player_sequence = [x for x in range(self.current_player_idx, 4)] + [
            x for x in range(0, self.current_player_idx)
        ]

        val_start_sequence = random.randint(1, 13) + val_player_sequence
        self.tile_sequence.shuffle(val_start_sequence)
        self.deal()
        self.play()
        self.round_summary()

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

    def resolve_call(self, responses):
        """
        hu > peng/gang > shang
        multiple players can hu, player who sits right (1st) to the player that
        played tile wins
        """
        if "hu" in responses:
            if len(responses["hu"]) > 1:
                hu_order = [x for x in range(self.current_player_idx, 4)] + [
                    x for x in range(0, self.current_player_idx)
                ]
                for player_idx in hu_order:
                    if player_idx in responses["hu"]:
                        return player_idx
            else:
                return responses["hu"][0]
        elif "peng" in responses:
            return responses["peng"]
        elif "ming_gang" in responses:
            return responses["ming_gang"]
        elif "jia_gang" in responses:
            return responses["jia_gang"]
        elif "an_gang" in responses:
            return responses["an_gang"]
        elif "shang" in responses:
            return responses["shang"]
        else:
            raise ValueError("no valid response")

    def play_one_round(self):
        current_player = self.players[
            self.round_player_sequence[self.current_player_idx]
        ]
        played_tile = current_player.play_turn(self.tile_sequence)

        check_responses = {}
        for _, player in self.players.items():
            player: Player
            rv = player.call()
            if rv == "hu" and rv not in check_responses:
                check_responses[rv] = [player.player_idx]
            elif rv == "hu" and rv in check_responses:
                check_responses[rv].append(player.player_idx)
            else:
                check_responses[rv] = player.player_idx
        if len(check_responses) > 1:
            player_idx = self.resolve_call(check_responses)
            hu = self.players[player_idx].resolve()
            if hu:
                self.winner = player_idx
            # skip to the player that resolved the call
            self.current_round_sequence += player_idx  # TODO validate
            return
        self.current_round_sequence += 1
        return

    def play(self):
        while not self.winner:
            print(f"current round sequence {self.current_round_sequence}")
            print(f"current player idx {self.current_player_idx}")
            print(f"round player sequence {self.round_player_sequence}")
            self.current_player_idx = self.current_round_sequence % 4
            if self.tile_sequence.tiles == []:
                break
            self.play_one_round()
            if self.winner:
                break

    def round_summary(self):
        return
