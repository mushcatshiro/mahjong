import random
import pickle
import copy
from typing import Dict, List

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

SPECIAL_WINNING_HAND = {
    "清一色": ["1索", "2索", "3索", "4索", "5索", "6索", "7索", "8索", "9索"],
}


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

    def save(self, pick=True):
        if not pick:
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
        replace with last time. used when there is a "gang" or getting a non
        playable tile
        """
        rv = []
        for _ in range(total):
            rv.append(self.tiles.pop(-1))
        return rv


class Hand(State):
    def __init__(self, player: int, replacement_tiles=DEFAULT_REPLACEMENT_TILES):
        self.tiles = []
        self.player = player
        self.tiles_history = {}
        self.replacement_tiles = [] if not replacement_tiles else replacement_tiles
        self.non_playable_tiles = []
        self.non_playable_tiles_ptr = 0
        self.distinct_tile_count = {}
        self.shang_candidates = []
        self.peng_history = []

    def update_shang_candidates(self):
        suite = ["万", "筒", "索"]
        self.shang_candidates = []
        for s in suite:
            candidates = sorted([x.replace(s, "") for x in self.tiles if x.endswith(s)])
            bptr = 0
            fptr = 2
            while fptr <= len(candidates):
                combination = "".join(candidates[bptr:fptr])
                if combination in SHANG_LUT:
                    self.shang_candidates += [f"{x}{s}" for x in SHANG_LUT[combination]]
                bptr += 1
                fptr += 1

    def add_tiles(self, tiles: List, incr_ptr=0, is_peng=False):
        if type(tiles) == str:  # TODO to be removed
            tiles = [tiles]
        self.tiles_history[f"{len(self.tiles_history)}add"] = tiles
        for tile in tiles:
            if tile in self.replacement_tiles:
                self.non_playable_tiles.append(tile)
            else:
                self.tiles.append(tile)
                if tile not in self.distinct_tile_count:
                    self.distinct_tile_count[tile] = 1
                else:
                    self.distinct_tile_count[tile] += 1
        if incr_ptr:
            self.non_playable_tiles_ptr += incr_ptr
        if is_peng:
            assert len(tiles) == 1
            self.peng_history.append(tiles[0])
        self.update_shang_candidates()

    def remove_tile(self, tile):
        self.tiles.remove(tile)
        self.distinct_tile_count[tile] -= 1
        assert self.distinct_tile_count[tile] >= 0
        self.tiles_history[f"{len(self.tiles_history)}remove"] = tile


class Player(State):
    def __init__(self, player, house):
        self.player = player
        self.previous_player = (player - 1) % 4  # TODO validate
        self.hand = Hand(player)
        self.action_history = []
        self.house = house
        self.pending_resolve = None

    def initial_draw(self, tile_sequence: TilesSequence, total, jump):
        tiles = tile_sequence.draw(total, jump)
        self.hand.add_tiles(tiles)

    def replace_tiles(self, tile_sequence: TilesSequence):
        """
        TODO
        - test
          hand "春 夏"
          got replacement "秋 冬"
          then get two more replacement "1 2"
          instead of getting 4 in a go
        - check for non dealing stage replacement is always 1?
        """
        total = len(self.hand.non_playable_tiles[self.hand.non_playable_tiles_ptr :])
        replaced_tiles = tile_sequence.replace(total)
        self.hand.add_tiles(replaced_tiles, total)
        return replaced_tiles

    def resolve_tile_replacement(self, tile_sequence: TilesSequence, drawed_tile=None):
        while True:
            if len(self.hand.non_playable_tiles) > self.hand.non_playable_tiles_ptr:
                drawed_tile = self.replace_tiles(tile_sequence)
            else:
                break
        return drawed_tile

    def play_turn(self, turn, tile_sequence: TilesSequence):
        self.pending_resolve = None  # reset

        drawed_tile = tile_sequence.draw()
        self.hand.add_tiles(drawed_tile)

        drawed_tile = self.resolve_tile_replacement(tile_sequence, drawed_tile)

        initial_possible_actions = self.draw_check(drawed_tile)

        action = self.play_turn_strategy(initial_possible_actions, drawed_tile)
        if action["resolve"]:
            self.resolve(
                action["input_tile"],
                action["discard_tile"],
                tile_sequence if action["tile_sequence"] else None,
            )
            return None
        else:
            self.hand.remove_tile(action["discard_tile"])
            return

    def call(self, played_tile, player):
        self.pending_resolve = None

        possible_actions = self.call_check(played_tile, player)
        response = self.call_strategy(possible_actions, played_tile)
        self.pending_resolve = (
            getattr(self, f"resolve_{response['action']}")
            if response["action"]
            else None
        )
        return response

    def play_turn_strategy(self, possible_actions, input_tile):
        raise NotImplementedError

    def call_strategy(self, possible_actions, played_tile):
        raise NotImplementedError

    def draw_check(self, drawed_tile):
        if type(drawed_tile) == list:
            assert len(drawed_tile) == 1
            drawed_tile = drawed_tile[0]
        rv = {
            "an_gang": self.an_gang(drawed_tile),
            "hu": self.hu(drawed_tile),
            "jia_gang": self.jia_gang(drawed_tile),
        }
        return rv

    def call_check(self, played_tile, player):
        # TODO not ready
        rv = {
            "peng": self.peng(played_tile),
            "ming_gang": self.ming_gang(played_tile),
            "shang": self.shang(played_tile, player),
            "hu": self.hu(played_tile),
        }
        return rv

    def peng(self, played_tile):
        if (
            played_tile in self.hand.distinct_tile_count.keys()
            and self.hand.distinct_tile_count[played_tile] == 2
        ):
            return True
        return False

    def resolve_peng(self, played_tile, discard_tile):
        # TODO add to hand then remove one tile
        self.hand.add_tiles(played_tile, is_peng=True)
        self.hand.remove_tile(discard_tile)

    def ming_gang(self, played_tile):
        if (
            played_tile in self.hand.distinct_tile_count.keys()
            and self.hand.distinct_tile_count[played_tile] == 3
            and played_tile not in self.hand.peng_history
        ):
            return True
        return False

    def resolve_ming_gang(self, played_tile, discard_tile, tile_sequence):
        self.hand.add_tiles(played_tile)
        drawed_tile = tile_sequence.replace(1)
        self.hand.add_tiles(drawed_tile)
        self.resolve_tile_replacement(tile_sequence, drawed_tile)

    def jia_gang(self, drawed_tile):
        if (
            drawed_tile in self.hand.distinct_tile_count.keys()
            and self.hand.distinct_tile_count[drawed_tile] == 3
            and drawed_tile in self.hand.peng_history
        ):
            return True
        return False

    def resolve_jia_gang(self, drawed_tile, discard_tile, tile_sequence):
        self.hand.add_tiles(drawed_tile)
        drawed_tile = tile_sequence.replace(1)
        self.hand.add_tiles(drawed_tile)
        self.resolve_tile_replacement(tile_sequence, drawed_tile)

    def an_gang(self, drawed_tile):
        if (
            drawed_tile in self.hand.distinct_tile_count.keys()
            and self.hand.distinct_tile_count[drawed_tile] == 4
        ):
            return True
        return False

    def resolve_an_gang(self, drawed_tile, discard_tile, tile_sequence):
        # TODO add to hidden hand
        drawed_tile = tile_sequence.replace(1)
        self.hand.add_tiles(drawed_tile)
        self.resolve_tile_replacement(tile_sequence, drawed_tile)

    def shang(self, played_tile, player):
        if player != self.previous_player:
            return False
        """
        boundary 1 9 only 1, 2, 3 and 7, 8, 9
        boundary 2 8 only 1, 2, 3 and 7, 8, 9
        3 - 7 can have n - 2, n - 1, n, n + 1, n + 2
        """
        if played_tile in self.hand.shang_candidates:
            return True
        return False

    def resolve_shang(self, played_tile, discard_tile):
        # TODO add to hand then remove one tile
        self.hand.add_tiles(played_tile)
        self.hand.remove_tile(discard_tile)

    def hu(self, played_tile):
        if self.winning_condition(self.hand.tiles + [played_tile]):
            return True
        return False

    def winning_condition(self, hand):
        # basic winning condition 3 sets of 3 (peng/gang or shang) + 1 pair
        # gang will be considered as 3

        # 清一色
        # 混一色
        # 大四喜
        # 大三元
        # 綠一色
        # 九蓮寶燈
        # 四槓子
        # 連七對
        # 十三幺
        # 七對子
        # 全不靠
        # 對對和
        return False

    def resolve_hu(self):
        return True

    def resolve(self, input_tile, discard_tile, tile_sequence=None):
        # append function name
        self.action_history.append(self.pending_resolve.__name__)
        if tile_sequence is not None:
            return self.pending_resolve(input_tile, discard_tile, tile_sequence)
        return self.pending_resolve(input_tile, discard_tile)


class DummyPlay(Player):
    def play_turn_strategy(self, possible_actions):
        return possible_actions[0]


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

    def __init__(self, players):
        self.players: Dict[int, Player] = {}
        self.tile_sequence = TilesSequence()
        self.current_player = 0
        self.current_round_player_sequence = []
        self.current_round_sequence = 0
        self.winner = None

    def start(self):
        # throw dice twice
        val_player_sequence = random.randint(0, 5)
        # 东 0 南 1 西 2 北 3
        self.current_player = val_player_sequence % 4
        self.current_round_player_sequence = [
            x for x in range(self.current_player, 4)
        ] + [x for x in range(0, self.current_player)]

        val_start_sequence = random.randint(1, 6) + val_player_sequence + 1
        self.tile_sequence.shuffle(val_start_sequence)
        self.deal()
        self.play()
        self.round_summary()

    def deal(self):
        # (4, 4, 4) * 3, 2 跳, 1, 1, 1
        for i in range(3):
            for player_idx in self.current_round_player_sequence:
                player: Player = self.players[player_idx]
                player.initial_draw(self.tile_sequence.draw(total=4))
        for idx, player_idx in enumerate(self.current_round_player_sequence):
            player: Player = self.players[player_idx]
            if idx == 0:
                player.initial_draw(self.tile_sequence.draw(total=2, jump=True))
            player.initial_draw(self.tile_sequence.draw(total=1, jump=False))
        for player_idx in self.current_round_player_sequence:
            player: Player = self.players[player_idx]
            player.replace_tiles()

    def resolve_call(self, actions):
        """
        hu > peng/gang > shang
        multiple players can hu, player who sits right (1st) to the player that
        played tile wins
        """

    def play_one_round(self):
        current_player = self.players[
            self.current_round_sequence[self.current_player_idx]
        ]
        current_player.play_turn()

        check_responses = {}
        for _, player in self.players.items():
            rv = player.check()
            check_responses[player.player] = rv
        if sum(check_responses.values()) > 1:
            player_idx = self.resolve_call(check_responses)
            hu = self.players[player_idx].resolve()
            if hu:
                self.winner = player_idx
            # skip to the player that resolved the call
            self.current_round_sequence += player_idx

    def play(self):
        while not self.winner:
            self.current_player_idx = self.current_round_sequence % 4
            if self.tile_sequence.tiles == []:
                break
            self.play_one_round()
            if self.winner:
                break
            self.current_round_sequence += 1

    def round_summary(self):
        return
