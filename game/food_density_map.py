import math
from collections import defaultdict

import config
from entities import food
from utils.utils import calc_normal

Food = food.Food


class FoodDensityMap:
    def __init__(self):
        self._density = {}

    def clear(self):
        self._density = {}

    def rebuild(self, food_iter):
        density = defaultdict(int)
        for food_item in food_iter:
            density[self._cell(food_item.pos)] += 1
        self._density = density

    def evaluate(self, ball, neighbours):
        local_food = sum(1 for n in neighbours if isinstance(n, Food))
        view_r = ball.radius * config.BALL_VIEW_FACTOR
        cx, cy = ball.pos
        search_r = config.AI_FOOD_DENSITY_SEARCH_RADIUS
        bx_min = int((cx - search_r) // config.AI_FOOD_DENSITY_CELL)
        bx_max = int((cx + search_r) // config.AI_FOOD_DENSITY_CELL)
        by_min = int((cy - search_r) // config.AI_FOOD_DENSITY_CELL)
        by_max = int((cy + search_r) // config.AI_FOOD_DENSITY_CELL)

        best_count = 0
        best_pos = None
        for bx in range(bx_min, bx_max + 1):
            for by in range(by_min, by_max + 1):
                count = self._density.get((bx, by), 0)
                if count == 0:
                    continue
                cell_cx = (bx + 0.5) * config.AI_FOOD_DENSITY_CELL
                cell_cy = (by + 0.5) * config.AI_FOOD_DENSITY_CELL
                dist = math.hypot(cell_cx - cx, cell_cy - cy)
                if dist <= view_r or dist > search_r:
                    continue
                if count > best_count:
                    best_count = count
                    best_pos = (cell_cx, cell_cy)

        direction = None
        if best_pos is not None:
            _, direction = calc_normal(ball.pos, best_pos)
        return local_food, best_count, direction

    def split_allowed(self, local_food, remote_density):
        if remote_density < config.AI_SPLIT_FOOD_DENSITY_MIN:
            return False
        if local_food > 0 and remote_density < local_food * config.AI_SPLIT_FOOD_SPREAD_RATIO:
            return False
        return True

    def _cell(self, pos):
        return (
            int(pos[0] // config.AI_FOOD_DENSITY_CELL),
            int(pos[1] // config.AI_FOOD_DENSITY_CELL),
        )
