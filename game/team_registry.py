import config
from game.team_blob import TeamBlob
from utils.utils import calc_mass_center


class TeamRegistry:
    def __init__(self):
        self.blue_blob = None
        self.red_blob = None

    def clear(self):
        self.blue_blob = None
        self.red_blob = None

    def update(self, balls):
        self.red_blob = self._make_blob(balls, config.TEAM_RED)
        self.blue_blob = self._make_blob(balls, config.TEAM_BLUE)

    def mass(self, balls, team):
        return sum(b.mass for b in balls if b.team == team)

    def winner(self, balls):
        blue_mass = self.mass(balls, config.TEAM_BLUE)
        red_mass = self.mass(balls, config.TEAM_RED)
        if blue_mass <= 0 and red_mass <= 0:
            return None
        if blue_mass <= 0:
            return config.TEAM_RED
        if red_mass <= 0:
            return config.TEAM_BLUE
        if blue_mass > red_mass:
            return config.TEAM_BLUE
        if red_mass > blue_mass:
            return config.TEAM_RED
        return None

    def _make_blob(self, balls, team):
        team_balls = [b for b in balls if b.team == team]
        if not team_balls:
            return None
        center = calc_mass_center(team_balls)
        if center is None:
            return None
        total_mass = sum(b.mass for b in team_balls)
        return TeamBlob(center, total_mass, team)
