from dataclasses import dataclass, field
from typing import List

from save_state import State


__all__ = ["PlayAction", "PlayResult", "ReplacementResult"]


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
