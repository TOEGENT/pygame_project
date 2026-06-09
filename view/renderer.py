import pygame

import config


def draw_grid(surface, camera, screen_width, screen_height, cell_size, color):
    offset_x = camera.offset[0] * config.PIXELS_PER_METER * camera.zoom
    offset_y = camera.offset[1] * config.PIXELS_PER_METER * camera.zoom

    cell_px = cell_size * config.PIXELS_PER_METER * camera.zoom

    start_x = int(-offset_x % cell_px)
    start_y = int(-offset_y % cell_px)
    x = start_x
    while x < screen_width:
        pygame.draw.line(surface, color, (x, 0), (x, screen_height))
        x += cell_px
    y = start_y
    while y < screen_height:
        pygame.draw.line(surface, color, (0, y), (screen_width, y))
        y += cell_px


def draw_ball_with_alpha(surface, color, position, radius, alpha):
    temp_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    temp_color = (*color, int(alpha))
    pygame.draw.circle(temp_surface, temp_color, (radius, radius), radius)
    surface.blit(temp_surface, (position[0] - radius, position[1] - radius))
