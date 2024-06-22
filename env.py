import socket
import os
import subprocess
from typing import Dict

from game import Mahjong, Player
from model import PlayResult
from player import PlayAction


def push_data(cmd, host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.send(cmd.encode())
    # check if data is received?
    s.close()


def pull_data(cmd, host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.send(cmd.encode())
    data = b""
    while True:
        part = s.recv(1024)
        if not part:
            break
        data += part
    s.close()
    return data


class TCPServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((host, port))
        self.s.listen(1)
        self.pact_queue = []  # no need to consider thread safety
        self.ract_queue = []
        self.game_queue = []

    def serve(self):
        while True:
            client_socket, addr = self.s.accept()
            print("Got connection from", addr)

            data = b""
            while True:
                part = client_socket.recv(1024)
                if not part:
                    break
                data += part
            header, queue_name, payload = data.decode().split(":")
            queue = getattr(self, queue_name)
            if not queue:
                raise ValueError(f"Queue {queue_name} not found")
            if header == "ADDQ":
                queue.append(payload)
            elif header == "GETQ":
                if len(queue) == 0:
                    client_socket.send(b"NONE")
                else:
                    client_socket.send(queue.pop(0))


def model_to_tensor(possible_actions):
    pass


def tensor_to_model(possible_action):
    pass


class EnvPlayer(Player):
    def __init__(self, player_idx, host, port, info, debug=False):
        super().__init__(player_idx, debug=debug)
        self.host = host
        self.port = port
        self.info = info

    def process_possible_actions(self, possible_actions):
        payload = model_to_tensor(possible_actions)
        cmd = "ADDQ:pact:" + payload
        push_data(cmd, self.host, self.port)

        while True:
            possible_action = pull_data("GETQ:ract:", self.host, self.port)
            if possible_action != b"NONE":
                break

        return self.tensor_to_model(possible_action)

    def play_turn_strategy(self, possible_actions, **kwargs):
        return self.process_possible_actions(possible_actions)

    def call_strategy(self, possible_actions, played_tile, **kwargs):
        return self.process_possible_actions(possible_actions)

    def gang_discard_strategy(self, possible_actions, **kwargs):
        return self.process_possible_actions(possible_actions)


class EnvMahjong(Mahjong):
    def __init__(self, players: Dict[int, Player], host, port):
        super().__init__(players)
        self.host = host
        self.port = port

    def player_play_turn(self) -> PlayResult:
        current_player = self.players[self.current_player_idx]
        if hasattr(current_player, "info"):
            pass
        else:
            play_result = current_player.play_turn(self.tile_sequence)
        return play_result

    def play(self):
        while True:
            game_playload = pull_data("GETQ:game:", self.host, self.port)
            term = True if game_playload.decode() == "term" else False
            if self.winner is not None or term:
                break
            if self.tile_sequence.is_empty():
                break
            self.play_one_round()

    def player_call(self, play_result: PlayResult, player_idx) -> PlayAction:
        return super().player_call(play_result, player_idx)

    def round_summary(self):
        return super().round_summary()


class Env:
    """
    a few things to think about:
    - how to train multiple rl agents (self-play)
      - same agent observe different states (player hand) and update a unified mapping function? how?
    - intermediate rewards?
    assumes 1 player (idx 0) vs 3 bots
    """

    def __init__(self, env_name, host, port):
        self.env_name = "Mahjong"
        self.host = host
        self.port = port

    def calculate_step_reward(self, state):
        pass

    def close(self):
        push_data(b"ADDQ:game:exit", self.host, self.port)

    def reset(self):
        # returns initial state
        push_data(b"ADDQ:game:reset", self.host, self.port)
        while True:
            state = pull_data("GETQ:pact:", self.host, self.port)
            if state:
                break
        return state

    def step(self, action):
        """
        state: current hand, discarded pool, remaining player showable tiles
        reward: ?
        term: game ends
        early term
        """
        push_data("ADDQ:ract:", self.host, self.port)
        while True:
            play_payload = pull_data("GETQ:pact:", self.host, self.port)
            if play_payload:
                break
        state = play_payload.decode()
        game_payload = pull_data("GETQ:game:", self.host, self.port)

        reward = self.calculate_step_reward(state)
        term = True if game_payload.decode() == "term" else False

        return state, reward, term


def main(host, port, cmd):
    if cmd == "start-game":
        while True:
            payload = pull_data("GETQ:game:", host, port)
            if payload[:4] == b"exit":
                break
            elif payload[:4] == b"reset":
                game = EnvMahjong()
                game.reset()
                game.prepare()
                game.deal()
                game.play()
                result = game.round_summary()
                result = result.encode()
                payload = b"ADDQ:game:term" + result
                push_data(payload, host, port)
                payload = b"ADDQ:"  # add round summary reward
    elif cmd == "start-server":
        server = TCPServer(host, port)
        server.serve()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="localhost")
    parser.add_argument("--port", type=int, default=12345)
    parser.add_argument("--cmd", type=str, choices=["start-game", "start-server"])
    args = parser.parse_args()
    main(args.host, args.port, args.cmd)
