import config


class MatchState:
    def __init__(self, duration=None):
        self.duration = duration if duration is not None else config.GAME_DURATION_SEC
        self.remaining = self.duration
        self.is_over = False

    def clear(self):
        self.remaining = self.duration
        self.is_over = False

    def tick(self, dt):
        if self.is_over:
            return
        self.remaining = max(0, self.remaining - dt)
        if self.remaining <= 0:
            self.is_over = True

    def check_elimination(self, blue_mass, red_mass):
        if self.is_over:
            return
        if blue_mass <= 0 or red_mass <= 0:
            self.is_over = True
