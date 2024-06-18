from game import Mahjong, Player


class EnvPlayer(Player):
    """
    need to break down play_turn, call and call_resolve and convert to `Tensor`
    """

    def __init__(self, player_idx, debug=False, strategy="dummy"):
        super().__init__(player_idx, debug=debug, strategy=strategy)

    def model_to_tensor(self, possible_actions):
        pass

    def tensor_to_model(self, possible_action):
        pass

    def play_turn(self, tile_sequence):
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
        return

    def step(self):

        pass

    def play_turn_strategy(self, possible_action, **kwargs):
        return self.tensor_to_model(possible_action)

    def call_strategy(self, possible_action, played_tile, **kwargs):
        return self.tensor_to_model(possible_action)

    def gang_discard_strategy(self, possible_action, **kwargs):
        return self.tensor_to_model(possible_action)


class EnvMahjong(Mahjong):
    def __init__(self):
        super().__init__()

    def step(self):
        # need to break down play_one_round
        # term when game ends
        return state


class GameState:
    pass


class Env:
    """
    a few things to think about:
    - how to train multiple rl agents (self-play)
      - same agent observe different states (player hand) and update a unified mapping function? how?
    - intermediate rewards?
    assumes 1 player (idx 0) vs 3 bots
    """

    def __init__(self, env_name):
        self.env_name = "Mahjong"
        self.env = EnvMahjong()

    def reset(self) -> GameState:
        # reset should prepare the game and return game state
        self.env.reset()
        self.env.prepare()
        self.env.deal()
        # state include current hand, discarded pool and remaining player showable tiles
        return self.env.step()

    def calculate_step_reward(self, state):
        pass

    def step(self, action):
        """
        state: current hand, discarded pool, remaining player showable tiles
        reward: ?
        term: game ends
        """
        if self.env.tile_sequence.is_empty():
            return None, 0, True
        if self.env.winner is not None:
            if self.env.winner == 0:
                reward = self.env.players[0].round_summary()
                return None, reward, True
            return None, 0, True
        state = self.env.step(action)
        reward = self.calculate_step_reward(state)
        return state, reward, term
