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
    if ball.team != config.TEAM_BLUE:
        more_follow = 0
        more_unfollow = 0
    danger_factor = 0
    ally_factor = 0
    delta = neighbour.radius - ball.radius
    merge_factor = config.INTENT_MERGE_CLAMP * math.tanh(delta / config.INTENT_MERGE_EPSILON)
    if neighbour.team != ball.team:
        danger_factor -= 1 + more_follow - more_unfollow
    else:
        if abs(neighbour.radius - ball.radius) < config.MINIMUM_MASS:
            ally_factor += 1/10 + more_follow - more_unfollow
    ball_factor = (danger_factor + ally_factor) * merge_factor
    return ball_factor

def calc_importance_factor(dist, scale, reverse=False):
    if dist <= 0 or scale <= 0:
        return 0
    if reverse:
        return dist ** 3 / (scale - dist)
    return min(1.0, scale / (scale + dist))

def calc_wall_importance(wall_dist, wall_scale):
    if wall_dist >= wall_scale or wall_scale <= 0:
        return 0
    t = 1.0 - wall_dist / wall_scale
    return t * t * config.WALL_INTENT_PEAK


def team_mass_ratio(own_blob, enemy_blob):
    if own_blob is None or enemy_blob is None or enemy_blob.mass <= 0:
        return 1.0
    return own_blob.mass / enemy_blob.mass

def team_tactic(mass_ratio):
    if mass_ratio >= config.DEFENSE_MASS_RATIO:
        return "defense"
    if mass_ratio <= config.ATTACK_MASS_RATIO:
        return "attack"
    return "neutral"

def team_largest_ball(balls, team):
    team_balls = [b for b in balls if b.team == team]
    if not team_balls:
        return None
    return max(team_balls, key=lambda b: b.mass)

def orbit_target(ball_pos, blob_pos, blob_radius, orbit_factor=None):
    dx = ball_pos[0] - blob_pos[0]
    dy = ball_pos[1] - blob_pos[1]
    dist = math.hypot(dx, dy)
    orbit_r = blob_radius * (orbit_factor if orbit_factor is not None else config.ORBIT_RADIUS_FACTOR)
    if dist < 1e-9:
        angle = 0.0
    else:
        angle = math.atan2(dy, dx)
    return (
        blob_pos[0] + math.cos(angle) * orbit_r,
        blob_pos[1] + math.sin(angle) * orbit_r,
    )

def calc_mass_center(balls):
    total_mass = sum(b.mass for b in balls)
    if total_mass == 0:
        return None
    cx = sum(b.pos[0] * b.mass for b in balls) / total_mass
    cy = sum(b.pos[1] * b.mass for b in balls) / total_mass
    return (cx, cy)
