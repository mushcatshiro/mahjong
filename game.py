import random
from typing import Dict

from tiles import FENGS

from player import Player, PlayAction, PlayResult
from tiles import TilesSequence


__all__ = ["Mahjong"]


class Mahjong:
    def __init__(self, players: Dict[int, Player]):
        self.players: Dict[int, Player] = players  # TODO dynamic load players
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
            player.reset()

    def prepare(self):
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
        self.prepare()
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
        """
        TODO `calculate_fan` focuses on `Hand` level. `round_summary`
        should be dealing with moving points from players to winner.
        """
        if self.winner is not None:
            self.players[self.winner].round_summary()
