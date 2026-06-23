import config
from utils.utils import calc_normal, team_mass_ratio, team_tactic


class SplitController:
    def __init__(self, food_density):
        self.food_density = food_density

    def split_player_team(self, ctx, command_target, do_split):
        if ctx.control_mode != config.CONTROL_MODE_PLAYER:
            return
        for ball in list(ctx.balls):
            if ball.team != ctx.player_team:
                continue
            if ball.mass < 2 * config.MINIMUM_MASS:
                continue
            dist, normal = calc_normal(ball.pos, command_target)
            direction = normal if dist > 0 else None
            do_split(ball, direction=direction)

    def try_ai_split(self, ball, neighbours, dt, ctx, do_split):
        if ctx.control_mode == config.CONTROL_MODE_PLAYER and ball.team == ctx.player_team:
            return
        if ball.team not in (config.TEAM_BLUE, config.TEAM_RED):
            return
        if ball.ai_split_cooldown > 0:
            ball.ai_split_cooldown = max(0, ball.ai_split_cooldown - dt)
            return
        own_blob = ctx.blue_blob if ball.team == config.TEAM_BLUE else ctx.red_blob
        enemy_blob = ctx.red_blob if ball.team == config.TEAM_BLUE else ctx.blue_blob
        if own_blob is None or enemy_blob is None:
            return

        mass_ratio = team_mass_ratio(own_blob, enemy_blob)
        tactic = team_tactic(mass_ratio)
        if tactic == "defense":
            return

        local_food, remote_density, food_direction = self.food_density.evaluate(
            ball, neighbours
        )

        if tactic == "neutral":
            if not self.food_density.split_allowed(local_food, remote_density):
                return
            self._split_to_max(ball, ctx, do_split)
        elif tactic == "attack":
            if food_direction is not None:
                split_direction = food_direction
            else:
                _, split_direction = calc_normal(ball.pos, enemy_blob.pos)
            self._split_to_max(ball, ctx, do_split, direction=split_direction)

        ball.ai_split_cooldown = config.AI_SPLIT_COOLDOWN

    def _split_to_max(self, ball, ctx, do_split, direction=None):
        while ball in ctx.balls and ball.mass >= 2 * config.MINIMUM_MASS:
            do_split(ball, direction=direction)
