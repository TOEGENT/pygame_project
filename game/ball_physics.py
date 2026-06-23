import math
import random

import config
from ai import ai
from entities import food

Food = food.Food


class BallPhysics:
    def __init__(self, spatial):
        self.spatial = spatial

    def step(self, ball, neighbours, dt, ai_ctx, on_remove_ball, on_create_food, on_try_split):
        self.resolve_collisions(ball, neighbours)
        self.apply_eating(ball)
        self.apply_decay(ball, dt)
        self.spawn_decay_food(ball, on_create_food)

        if round(ball.mass, 2) <= config.DEATH_MASS:
            on_remove_ball(ball)
            return

        on_try_split(ball, neighbours, dt)
        self.move(ball, ai_ctx)

    def resolve_collisions(self, ball, neighbours):
        seen = set()
        for neighbour in neighbours:
            if neighbour is ball or neighbour in seen:
                continue
            seen.add(neighbour)

            dx = neighbour.pos[0] - ball.pos[0]
            dy = neighbour.pos[1] - ball.pos[1]
            if ball.radius > neighbour.radius:
                predator = ball
                victum = neighbour
            elif ball.radius < neighbour.radius:
                predator = neighbour
                victum = ball
            else:
                ball.eats.discard(neighbour)
                neighbour.eats.discard(ball)
                ball.is_eaten_by.discard(neighbour)
                neighbour.is_eaten_by.discard(ball)
                continue

            if predator.radius * predator.radius > dx * dx + dy * dy:
                if isinstance(victum, Food) and victum.is_eaten_by:
                    continue
                victum.is_eaten_by.add(predator)
                if isinstance(victum, Food):
                    predator.eats.add(victum)
            else:
                victum.is_eaten_by.discard(predator)
                if isinstance(victum, Food):
                    predator.eats.discard(victum)

    def spawn_decay_food(self, ball, on_create_food):
        if ball.mass_before_decay > ball.mass:
            ball.lost_mass_to_spawn += ball.mass_before_decay - ball.mass
        while round(ball.lost_mass_to_spawn, 2) >= config.FOOD_MASS:
            random_r = random.uniform(
                ball.radius + ball.radius * 0.1,
                ball.radius + ball.radius * 0.2,
            )
            random_angle = random.uniform(0, 2 * math.pi)
            pos_x = ball.pos[0] + random_r * math.cos(random_angle)
            pos_y = ball.pos[1] + random_r * math.sin(random_angle)
            on_create_food((pos_x, pos_y))
            ball.lost_mass_to_spawn -= config.FOOD_MASS

    def apply_eating(self, ball):
        ball.old_mass = ball.mass
        for food_item in ball.eats:
            ball.mass += food_item.mass
        ball.eats.clear()

    def apply_decay(self, ball, dt):
        ball.mass_before_decay = ball.mass
        factor = 0
        if ball.is_eaten_by:
            for predator in ball.is_eaten_by:
                if predator.radius > ball.radius:
                    factor += 1 + 1 / (0.001 + predator.radius - ball.radius)
            new_mass = (
                config.DEATH_MASS - 0.1
                + (ball.mass - config.DEATH_MASS - 0.1) * config.DECAY_FACTOR ** (dt + factor)
            )
        else:
            new_mass = (
                config.DEATH_MASS
                + (ball.mass - config.DEATH_MASS) * config.DECAY_FACTOR ** (dt + factor)
            )
        ball.mass = new_mass

    def move(self, ball, ai_ctx):
        cell_poses = self.spatial.get_cells(
            ball.pos, ball.radius * config.BALL_VIEW_FACTOR
        )
        neighbours = self.spatial.neighbours(cell_poses)
        ball.old_pos = (ball.pos[0], ball.pos[1])
        ball.view_point = ai.ai(ball, neighbours, ai_ctx)
        ball.update_smooth_view()
        normal = ball.normal
        speed = ball.speed

        new_x = max(
            ball.radius,
            min(config.WINDOW_WIDTH - ball.radius, ball.pos[0] + normal[0] * speed),
        )
        new_y = max(
            ball.radius,
            min(config.WINDOW_HEIGHT - ball.radius, ball.pos[1] + normal[1] * speed),
        )
        ball.pos = (new_x, new_y)
