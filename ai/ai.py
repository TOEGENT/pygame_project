import config
import math

from entities import ball as Ball
from entities import food
def ai(ball:Ball.Ball,neighbours:list):
    result = [0,0]
    def update_reflexes():
        total_x=ball.pos[0]
        total_y=ball.pos[1]
        wall_dist_left = ball.pos[0]
        wall_dist_right = config.WINDOW_WIDTH-ball.pos[0]
        wall_dist_down = ball.pos[1]
        wall_dist_top = config.WINDOW_HEIGHT-ball.pos[1]
        for neighbour in neighbours:
            dx = neighbour.pos[0]-ball.pos[0]
            dy = neighbour.pos[1]-ball.pos[1]
            dist = math.hypot(dx,dy)
            if dist==0:
                continue
            nx = dx/dist
            ny = dy/dist

            if isinstance(neighbour,food.Food) :
                total_x+=nx*neighbour.mass/dist
                total_y+=ny*neighbour.mass/dist
            elif isinstance(neighbour,Ball.Ball):
                if neighbour.radius==ball.radius:
                    danger_factor=0
                else:
                    if neighbour.team!=ball.team:
                        danger_factor = -1/(neighbour.radius-ball.radius)
                    else:
                        danger_factor = -1/10*abs(neighbour.radius-ball.radius)
                neighbour_future_x = neighbour.normal[0]*neighbour.speed
                neighbour_future_y = neighbour.normal[1]*neighbour.speed
                future_dx = ball.pos[0]-neighbour_future_x
                future_dy = ball.pos[1]-neighbour_future_y
                dist_future = math.hypot(future_dx,future_dy)
                n_future_x = future_dx/dist_future
                n_future_y = future_dy/dist_future
                total_x+=(nx + 0.3*n_future_x)*(danger_factor * neighbour.mass/dist)
                total_y+=(ny+0.3*n_future_y)*danger_factor * neighbour.mass/dist
        if wall_dist_left<ball.radius*3:
            total_x+=1/(1+wall_dist_left)**2
        if wall_dist_down<ball.radius*3:
            total_y+=1/(1+wall_dist_down)**2
        if wall_dist_right<ball.radius*3:
            total_x-=1/(1+wall_dist_right)**2
        if wall_dist_top<ball.radius:
            total_y-=1/(1+wall_dist_top)**2
        return (total_x,total_y)
    reflexes = update_reflexes()
    result[0]+=reflexes[0]
    result[1]+=reflexes[1]
    return tuple(result)
            

