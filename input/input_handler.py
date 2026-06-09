import math

import pygame

import config
from utils.math_utils import mobility


def handle_player_input(player, screen_width, screen_height):
    screen_center = [screen_width / 2, screen_height / 2]

    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_pos = [mouse_x, mouse_y]
    dx = mouse_pos[0] - screen_center[0]
    dy = mouse_pos[1] - screen_center[1]

    spring = 1
    damping = 0.5

    distance = math.sqrt(dx**2 + dy**2)

    nx = dx / (distance + 1e-6)
    ny = dy / (distance + 1e-6)
    if distance > 0:
        force_x = min(config.MAX_ACCELERATION, abs(nx * spring))
        force_y = min(config.MAX_ACCELERATION, abs(ny * spring))
        if dx < 0:
            force_x = -force_x
        if dy < 0:
            force_y = -force_y

        player.force[0] += force_x * mobility(player)
        player.force[1] += force_y * mobility(player)

        player.force[0] *= damping
        player.force[1] *= damping
