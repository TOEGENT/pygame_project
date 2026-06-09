import random
import sys

import pygame

import config
from game.game_state import GameState
from models.ball import Ball
from models.camera import Camera
from models.constants import Colors
from view.renderer import draw_ball_with_alpha, draw_grid


class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("My Game")
        self.clock = pygame.time.Clock()

        self.game_state = GameState(self._create_entities())
        self.camera = Camera(self.screen.get_width(), self.screen.get_height())
        self.running = True

    def _create_entities(self):
        balls = [
            Ball(
                color=Colors.RED,
                pos=[400, 300],
                radius=5,
                mass=10,
            ),
        ]
        balls += [
            Ball(
                color=random.choice([Colors.RED, Colors.BLUE]),
                pos=[random.uniform(0, config.WIDTH), random.uniform(0, config.HEIGHT)],
                radius=random.randint(5, config.MAX_RADIUS),
                mass=random.randint(5, config.MAX_MASS),
            )
            for _ in range(200)
        ]
        return balls

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            config.ACCUMULATOR += dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            while config.ACCUMULATOR >= config.FIXED_DT:
                self.game_state.update(
                    config.FIXED_DT,
                    self.screen.get_width(),
                    self.screen.get_height(),
                )
                self.camera.update(
                    self.game_state.entities[0].pos,
                    self.game_state.entities[0].radius,
                )
                config.ACCUMULATOR -= config.FIXED_DT

            self._render()

        pygame.quit()
        sys.exit()

    def _render(self):
        self.screen.fill(Colors.WHITE)
        draw_grid(
            self.screen,
            self.camera,
            self.screen.get_width(),
            self.screen.get_height(),
            20,
            (200, 200, 200),
        )
        for ball in self.game_state.entities:
            screen_pos = self.camera.apply(ball.pos)
            mass_norm = max(0, min(1, ball.mass / config.MAX_MASS))
            alpha = int(config.MIN_ALPHA + mass_norm * (config.MAX_ALPHA - config.MIN_ALPHA))
            draw_ball_with_alpha(
                self.screen,
                ball.color,
                screen_pos,
                int(ball.radius * config.PIXELS_PER_METER * self.camera.zoom),
                alpha,
            )

        pygame.display.flip()
