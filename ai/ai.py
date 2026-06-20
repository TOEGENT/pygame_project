import config
import math

from entities import ball as Ball
from entities import food
def ai(ball:Ball.Ball,neighbours:list):
    total_x=ball.pos[0]
    total_y=ball.pos[1]
    for neighbour in neighbours:
        dx = neighbour.pos[0]-ball.pos[0]
        dy = neighbour.pos[1]-ball.pos[1]
        dist = math.hypot(dx,dy)
        if dist==0:
            continue
        nx = dx/dist
        ny = dy/dist

        if isinstance(neighbour,food.Food):
            total_x+=nx*neighbour.mass/dist
            total_y+=ny*neighbour.mass/dist
        elif isinstance(neighbour,Ball.Ball):
            if neighbour.radius==ball.radius:
                danger_factor=0
            else:
                danger_factor = -1/(neighbour.radius-ball.radius)
            total_x+=nx* danger_factor * neighbour.mass/dist
            total_y+=ny*danger_factor * neighbour.mass/dist
    return (total_x,total_y)
            

