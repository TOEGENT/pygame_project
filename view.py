import pygame

import config


def draw_team_blobs(screen, blue_blob, red_blob, fill_alpha=40, outline_alpha=140):
    for blob in (red_blob, blue_blob):
        if blob is None:
            continue
        radius = int(blob.radius)
        if radius < 1:
            continue
        color = config.COLOR_BLUE if blob.team == config.TEAM_BLUE else config.COLOR_RED
        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*color, fill_alpha), (radius, radius), radius)
        pygame.draw.circle(surf, (*color, outline_alpha), (radius, radius), radius, 2)
        screen.blit(surf, (blob.pos[0] - radius, blob.pos[1] - radius))
