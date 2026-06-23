from collections import defaultdict

import config


class SpatialHash:
    def __init__(self, cell_size=None):
        self.cell_size = cell_size if cell_size is not None else config.CELL_SIZE
        self.balls_hash = defaultdict(list)
        self.food_hash = defaultdict(list)

    def clear(self):
        self.balls_hash.clear()
        self.food_hash.clear()

    def cell_pos(self, pos):
        return (int(pos[0] // self.cell_size), int(pos[1] // self.cell_size))

    def get_cells(self, pos, radius):
        x_start = int((pos[0] - radius) // self.cell_size)
        x_end = int((pos[0] + radius) // self.cell_size)
        y_start = int((pos[1] - radius) // self.cell_size)
        y_end = int((pos[1] + radius) // self.cell_size)
        cells = set()
        for x_cell in range(x_start, x_end + 1):
            for y_cell in range(y_start, y_end + 1):
                cells.add((x_cell, y_cell))
        return cells

    def register_ball(self, ball):
        for cell_pos in self.get_cells(ball.pos, ball.radius):
            if ball not in self.balls_hash[cell_pos]:
                self.balls_hash[cell_pos].append(ball)

    def unregister_ball(self, ball, pos=None, radius=None):
        pos = pos if pos is not None else ball.pos
        radius = radius if radius is not None else ball.radius
        for cell_pos in self.get_cells(pos, radius):
            bucket = self.balls_hash.get(cell_pos)
            if bucket and ball in bucket:
                bucket.remove(ball)
            if bucket is not None and not bucket:
                del self.balls_hash[cell_pos]

    def update_ball(self, ball, old_pos, old_radius):
        cell_pos_old = self.get_cells(old_pos, old_radius)
        cell_pos_current = self.get_cells(ball.pos, ball.radius)
        for cell_pos in cell_pos_current - cell_pos_old:
            if ball not in self.balls_hash[cell_pos]:
                self.balls_hash[cell_pos].append(ball)
        for cell_pos in cell_pos_old - cell_pos_current:
            bucket = self.balls_hash.get(cell_pos)
            if bucket and ball in bucket:
                bucket.remove(ball)
            if bucket is not None and not bucket:
                del self.balls_hash[cell_pos]
        return cell_pos_current

    def register_food(self, food):
        cell_pos = self.cell_pos(food.pos)
        self.food_hash[cell_pos].append(food)

    def unregister_food(self, food, cell_pos=None):
        if cell_pos is None:
            cell_pos = self.cell_pos(food.pos)
        if food in self.food_hash[cell_pos]:
            self.food_hash[cell_pos].remove(food)
        if not self.food_hash[cell_pos]:
            del self.food_hash[cell_pos]

    def neighbours(self, cell_poses):
        neighbours = set()
        for cell_pos in cell_poses:
            neighbours.update(self.balls_hash[cell_pos])
            neighbours.update(self.food_hash[cell_pos])
        return list(neighbours)

    def iter_food(self):
        for bucket in self.food_hash.values():
            for food_item in bucket:
                yield food_item
