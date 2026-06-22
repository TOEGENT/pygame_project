import math,config,entities.ball
Ball = entities.ball

def calc_normal(pos1,pos2):
    dx = pos2[0]-pos1[0]
    dy = pos2[1]-pos1[1]
    dist = math.hypot(dx,dy)
    if dist==0:
        return (0,(0,0))
    else:
        return dist, (dx/dist,dy/dist)
def calc_intent(ball:Ball,neighbour:Ball,more_follow,more_unfollow):
    if ball.team!=config.TEAM_BLUE:
        more_follow=0
        more_unfollow=0
    if neighbour.radius==ball.radius:
        return 0
    danger_factor = 0
    ally_factor = 0
    merge_factor = (1/(1+ neighbour.radius-ball.radius)+1)
    if neighbour.team!=ball.team:
        danger_factor -= 5 + more_follow - more_unfollow
    else:
        if abs(neighbour.radius-ball.radius)<config.MINIMUM_MASS:
            ally_factor += 5/10 + more_follow - more_unfollow
    ball_factor = (danger_factor+ally_factor)*merge_factor
    return ball_factor

def calc_importance_factor(dist):
    if dist==0:
        return 0
    return min(1,config.FOOD_MASS/(0.1+dist)+config.IMPORTANCE_KOEF)
def calc_mass_center(balls):
    total_mass = sum(b.mass for b in balls)
    if total_mass == 0:
        return None
    cx = sum(b.pos[0] * b.mass for b in balls) / total_mass
    cy = sum(b.pos[1] * b.mass for b in balls) / total_mass
    return (cx, cy)
