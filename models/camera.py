import config


class Camera:
    def __init__(self, width, height):
        self.offset = [0, 0]
        self.width = width
        self.height = height
        self.zoom = 1.0

    def update(self, target_pos, target_radius):
        alpha = 0.5
        target_zoom = 2.0 / (max(target_radius, 1) ** alpha)
        self.zoom += (target_zoom - self.zoom) * 0.2

        target_offset_x = target_pos[0] - (self.width / (2 * config.PIXELS_PER_METER * self.zoom))
        target_offset_y = target_pos[1] - (self.height / (2 * config.PIXELS_PER_METER * self.zoom))

        self.offset[0] += (target_offset_x - self.offset[0]) * 0.7
        self.offset[1] += (target_offset_y - self.offset[1]) * 0.7

    def apply(self, target_pos):
        return [
            (target_pos[0] - self.offset[0]) * config.PIXELS_PER_METER * self.zoom,
            (target_pos[1] - self.offset[1]) * config.PIXELS_PER_METER * self.zoom,
        ]
