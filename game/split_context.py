from dataclasses import dataclass


@dataclass
class SplitContext:
    control_mode: str
    player_team: int
    balls: set
    blue_blob: object
    red_blob: object
