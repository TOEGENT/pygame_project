from dataclasses import dataclass


@dataclass
class AIContext:
    control_mode: str
    player_team: int
    blue_blob: object
    red_blob: object
    balls: set
