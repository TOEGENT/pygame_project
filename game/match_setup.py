import math
import random

import config
from entities import ball

Ball = ball.Ball


class MatchSetup:
    @staticmethod
    def reset(game, opponent_count, food_count, map_size, player_mass=None):
        game.balls.clear()
        game.spatial.clear()
        game.foods.clear()
        game.player_ball = None
        game.match.clear()
        game.teams.clear()
        game.food_density.clear()
        game.start_mass = food_count

        config.WINDOW_WIDTH = map_size
        config.WINDOW_HEIGHT = map_size

        margin = config.FOOD_DISTANCE_FACTOR
        spawn_mass = player_mass if player_mass is not None else config.START_TEAM_BALL_MASS
        player_mass_val = max(config.MINIMUM_MASS * 2, spawn_mass)
        player_x = map_size * (margin + 0.12)
        player_y = map_size * 0.5
        game._add_ball(
            Ball((player_x, player_y), config.COLOR_BLUE, player_mass_val, config.TEAM_BLUE)
        )

        opp_mass = max(config.MINIMUM_MASS * 2, config.START_TEAM_BALL_MASS / opponent_count)
        for _ in range(opponent_count):
            ox = random.uniform(map_size * 0.55, map_size * (1 - margin))
            oy = random.uniform(map_size * margin, map_size * (1 - margin))
            r = math.sqrt(opp_mass)
            ox = max(r, min(map_size - r, ox))
            oy = max(r, min(map_size - r, oy))
            game._add_ball(Ball((ox, oy), config.COLOR_RED, opp_mass, config.TEAM_RED))

        for _ in range(food_count):
            pos = (
                random.uniform(map_size * margin, map_size * (1 - margin)),
                random.uniform(map_size * margin, map_size * (1 - margin)),
            )
            game.create_food(pos)



    @staticmethod
    def _clamp_ball_pos(pos, radius):
        margin = config.FOOD_DISTANCE_FACTOR
        x = max(radius, min(config.WINDOW_WIDTH * (1 - margin) - radius, pos[0]))
        y = max(radius, min(config.WINDOW_HEIGHT * (1 - margin) - radius, pos[1]))
        return (x, y)

    @staticmethod
    def _random_cluster_center(x_min, x_max):
        margin = config.FOOD_DISTANCE_FACTOR
        y_min = config.WINDOW_HEIGHT * margin
        y_max = config.WINDOW_HEIGHT * (1 - margin)
        return (
            random.uniform(x_min, x_max),
            random.uniform(y_min, y_max),
        )

    @staticmethod
    def _spawn_cluster_balls(game, team, color, center, mass_budget):
        spawned = 0.0
        while spawned + config.MINIMUM_MASS <= mass_budget + 1e-6:
            remaining = mass_budget - spawned
            mass = random.uniform(config.MINIMUM_MASS, remaining)
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(0, config.START_CLUSTER_RADIUS)
            radius = math.sqrt(mass)
            pos = MatchSetup._clamp_ball_pos(
                (center[0] + dist * math.cos(angle), center[1] + dist * math.sin(angle)),
                radius,
            )
            game._add_ball(Ball(pos, color, mass, team))
            spawned += mass
