import sys
import yaml
import time
import datetime as dt

sys.path.append(".")

from game import Player, PlayAction, Mahjong


class ReplayPlayer(Player):
    pass


class ReplayMahjong(Mahjong):
    pass


def main():
    pass


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--state-dir")
    main()
