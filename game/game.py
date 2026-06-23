import config
import math
from entities import ball, food
from game.spatial_hash import SpatialHash
from game.ai_context import AIContext
from game.split_context import SplitContext
from game.team_registry import TeamRegistry
from game.food_density_map import FoodDensityMap
from game.match_state import MatchState
from game.split_controller import SplitController
from game.ball_physics import BallPhysics
from game.match_setup import MatchSetup

Ball = ball.Ball
Food = food.Food


class Game:
    def __init__(self, time, control_mode=None):
        self.time = time
        self.control_mode = control_mode or config.CONTROL_MODE
        self.start_mass = config.START_MASS
        self.player_ball = None
        self.balls = set()
        self.foods = set()

        self.spatial = SpatialHash()
        self.teams = TeamRegistry()
        self.food_density = FoodDensityMap()
        self.match = MatchState()
        self.split = SplitController(self.food_density)
        self.physics = BallPhysics(self.spatial)

    @property
    def is_over(self):
        return self.match.is_over

    @property
    def match_time_remaining(self):
        return self.match.remaining

    @property
    def blue_blob(self):
        return self.teams.blue_blob

    @property
    def red_blob(self):
        return self.teams.red_blob

    def reset_for_match(self, opponent_count, food_count, map_size, player_mass=None):
        MatchSetup.reset(self, opponent_count, food_count, map_size, player_mass)

    def start(self):
        MatchSetup.start_legacy(self)

    def ai_context(self):
        return AIContext(
            control_mode=self.control_mode,
            player_team=config.PLAYER_TEAM,
            blue_blob=self.blue_blob,
            red_blob=self.red_blob,
            balls=self.balls,
        )

    def split_context(self):
        return SplitContext(
            control_mode=self.control_mode,
            player_team=config.PLAYER_TEAM,
            blue_blob=self.blue_blob,
            red_blob=self.red_blob,
            balls=self.balls,
        )

    def winner_team(self):
        return self.teams.winner(self.balls)

    def team_mass(self, team):
        return self.teams.mass(self.balls, team)

    def _add_ball(self, ball_obj):
        self.balls.add(ball_obj)
        if (
            self.control_mode == config.CONTROL_MODE_PLAYER
            and self.player_ball is None
            and ball_obj.team == config.PLAYER_TEAM
        ):
            self.player_ball = ball_obj
            self.player_ball.color = config.COLOR_BLUE
        self.spatial.register_ball(ball_obj)

    def _remove_ball(self, ball_obj):
        self.spatial.unregister_ball(ball_obj)
        self.balls.discard(ball_obj)
        for _ in range(config.DEATH_MASS):
            self.create_food(ball_obj.pos)

    def _remove_food(self, food_item, cell_pos=None):
        self.spatial.unregister_food(food_item, cell_pos)
        self.foods.discard(food_item)

    def create_food(self, pos):
        pos_x = max(
            config.WINDOW_WIDTH * config.FOOD_DISTANCE_FACTOR,
            min(config.WINDOW_WIDTH * (1 - config.FOOD_DISTANCE_FACTOR), pos[0]),
        )
        pos_y = max(
            config.WINDOW_HEIGHT * config.FOOD_DISTANCE_FACTOR,
            min(config.WINDOW_HEIGHT * (1 - config.FOOD_DISTANCE_FACTOR), pos[1]),
        )
        new_food = Food((pos_x, pos_y))
        new_food.color = config.COLOR_GREEN
        self.foods.add(new_food)
        self.spatial.register_food(new_food)

    def split_ball(self, ball_obj, direction=None):
        if ball_obj not in self.balls or ball_obj.mass < 2 * config.MINIMUM_MASS:
            return
        old_radius = ball_obj.radius
        half_mass = ball_obj.mass / 2
        self.spatial.unregister_ball(ball_obj, ball_obj.pos, old_radius)
        ball_obj.mass = half_mass
        ball_obj.old_mass = half_mass
        self.spatial.register_ball(ball_obj)
        if direction is not None:
            dx, dy = direction
        else:
            dx, dy = ball_obj.normal
        if math.hypot(dx, dy) < 1e-9:
            dx = math.cos(ball_obj.wander_angle)
            dy = math.sin(ball_obj.wander_angle)
        new_x = ball_obj.pos[0] + dx * old_radius
        new_y = ball_obj.pos[1] + dy * old_radius
        r = math.sqrt(half_mass)
        new_x = max(r, min(config.WINDOW_WIDTH - r, new_x))
        new_y = max(r, min(config.WINDOW_HEIGHT - r, new_y))
        new_ball = Ball((new_x, new_y), ball_obj.color, half_mass, ball_obj.team)
        self._add_ball(new_ball)

    def split_player_team(self, command_target):
        self.split.split_player_team(
            self.split_context(), command_target, self.split_ball
        )

    def update(self, dt):
        self.match.tick(dt)
        self.teams.update(self.balls)
        self.food_density.rebuild(self.spatial.iter_food())

        split_ctx = self.split_context()
        ai_ctx = self.ai_context()

        for ball_obj in list(self.balls):
            cells = self.spatial.update_ball(ball_obj, ball_obj.old_pos, ball_obj.old_radius)
            neighbours = self.spatial.neighbours(cells)
            self.physics.step(
                ball_obj,
                neighbours,
                dt,
                ai_ctx,
                on_remove_ball=self._remove_ball,
                on_create_food=self.create_food,
                on_try_split=lambda b, n, d: self.split.try_ai_split(
                    b, n, d, split_ctx, self.split_ball
                ),
            )

        for food_item in list(self.foods):
            if food_item.is_eaten_by:
                self._remove_food(food_item)

        self.match.check_elimination(
            self.team_mass(config.TEAM_BLUE),
            self.team_mass(config.TEAM_RED),
        )
