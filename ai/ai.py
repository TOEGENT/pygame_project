import random
import config
import math
from entities import food, intent, ball as Ball
from utils.utils import *
Intent = intent.Intent
import pygame

from utils.smooth_normal import smooth_add_pos


def _intent_len(v):
    return math.hypot(v[0], v[1])


INTENT_WEIGHTS = {
    "food": config.INTENT_WEIGHT_FOOD,
    "balls": config.INTENT_WEIGHT_BALLS,
    "wall": config.INTENT_WEIGHT_WALL,
    "wander": config.INTENT_WEIGHT_WANDER,
    "command": config.INTENT_WEIGHT_COMMAND,
}


def _apply_intent_budget(layer_specs):
    raw_lens = {name: _intent_len(layer.pos) for name, layer in layer_specs}
    budget_layers = ("food", "balls", "wall")
    L = max((raw_lens[n] for n in budget_layers), default=0)
    L = max(L, config.INTENT_MIN_BASELINE)

    urgencies = {}
    for name, _layer in layer_specs:
        length = raw_lens[name]
        if length < config.INTENT_DEAD_ZONE:
            continue
        urgencies[name] = INTENT_WEIGHTS[name] * length

    if urgencies:
        total_urgency = sum(urgencies.values())
        for name, layer in layer_specs:
            length = raw_lens[name]
            if length < config.INTENT_DEAD_ZONE:
                layer.pos[0] = 0
                layer.pos[1] = 0
                continue
            share = urgencies[name] / total_urgency
            layer.pos[0] = layer.pos[0] / length * L * share
            layer.pos[1] = layer.pos[1] / length * L * share

def ai(ball: Ball.Ball, neighbours: list, game):
    player_control = (
        game.control_mode == config.CONTROL_MODE_PLAYER
        and ball.team == config.PLAYER_TEAM
    )

    if player_control:
        mouse_keys = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        keyboard_keys = pygame.key.get_pressed()
        space = keyboard_keys[pygame.K_SPACE]
        more_follow = mouse_keys[0]
        more_unfollow = 2 * mouse_keys[2]
        more_ignore = mouse_keys[1]
        ball.sharing_food_factor = space
    else:
        mouse_pos = (0, 0)
        more_follow = 0
        more_unfollow = 0
        more_ignore = 0
        ball.sharing_food_factor = 0

    view_scale = ball.radius * config.BALL_VIEW_FACTOR
    wall_scale_x = max(ball.radius * 2.5, config.WINDOW_WIDTH * config.WALL_DISTANCE_FACTOR)
    wall_scale_y = max(ball.radius * 2.5, config.WINDOW_HEIGHT * config.WALL_DISTANCE_FACTOR)
    command_scale = max(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

    #reflex_intent (begin)
    total_ball_intent = Intent([0, 0], config.COLOR_BLACK, "balls")
    total_food_intent = Intent([0, 0], config.COLOR_GREEN, "food")
    food_count = 0
    ball_vectors = []
    for neighbour in neighbours:
        dist,normal = calc_normal(ball.pos,neighbour.pos)
        future_dist = 0
        if dist==0:
            continue
        #ball_intent (begin)
        ball_factor=1
        future_ball_intent = Intent((0,0),config.COLOR_PURPLE)
        if isinstance(neighbour,Ball.Ball):
            ball_factor_without_dist=calc_intent(ball,neighbour,more_follow=more_follow,more_unfollow = more_unfollow)

            neighbour_future_pos = (neighbour.pos[0]+neighbour.normal[0]*neighbour.speed,
                                        neighbour.pos[1]+neighbour.normal[1]*neighbour.speed)
            future_dist,future_normal = calc_normal(ball.pos,neighbour_future_pos)
            ball_future_factor = (ball_factor_without_dist)*(calc_importance_factor(future_dist, view_scale))
            future_ball_intent.pos = (future_normal[0]*ball_future_factor,future_normal[1]*ball_future_factor)

            ball_factor = (ball_factor_without_dist)*(calc_importance_factor(dist, view_scale))
            ball_intent = Intent((normal[0]*ball_factor,
                            normal[1]*ball_factor),config.COLOR_WHITE)
            ix = ball_intent.pos[0] + 0.3 * future_ball_intent.pos[0]
            iy = ball_intent.pos[1] + 0.3 * future_ball_intent.pos[1]
            score = abs(ball_factor_without_dist) * calc_importance_factor(dist, view_scale)
            ball_vectors.append((score, ix, iy))
        
        #ball_intent (end)

        #food_intent
        elif isinstance(neighbour,food.Food):
            food_count += 1
            food_factor = calc_importance_factor(dist, view_scale)
            total_food_intent.pos[0] += normal[0] * food_factor
            total_food_intent.pos[1] += normal[1] * food_factor

    if not player_control and ball.team in (config.TEAM_BLUE, config.TEAM_RED):
        own_blob = game.blue_blob if ball.team == config.TEAM_BLUE else game.red_blob
        enemy_blob = game.red_blob if ball.team == config.TEAM_BLUE else game.blue_blob


    ball_vectors.sort(key=lambda item: item[0], reverse=True)
    for _, ix, iy in ball_vectors[: config.INTENT_TOP_BALLS]:
        total_ball_intent.pos[0] += ix
        total_ball_intent.pos[1] += iy
    #reflex_intent(end)


    #wall_intent (begin)

    wall_intent = Intent([0, 0], config.COLOR_WHITE, "wall")
    wall_dist_left = ball.pos[0]-ball.radius
    wall_dist_right = config.WINDOW_WIDTH-ball.pos[0]+ball.radius
    wall_dist_top = ball.pos[1] - ball.radius
    wall_dist_down = config.WINDOW_HEIGHT-ball.pos[1] + ball.radius


    if wall_dist_left<wall_scale_x:
        wall_intent.pos[0]+=calc_wall_importance(wall_dist_left, wall_scale_x)
    if wall_dist_top<wall_scale_y:
        wall_intent.pos[1]+=calc_wall_importance(wall_dist_top, wall_scale_y)
    if wall_dist_right<wall_scale_x:
        wall_intent.pos[0]-=calc_wall_importance(wall_dist_right, wall_scale_x)
    if wall_dist_down<wall_scale_y:
        wall_intent.pos[1]-=calc_wall_importance(wall_dist_down, wall_scale_y)
    #wall_intent (end)
    #wander_intent (begin)
    ball.wander_angle += random.uniform(-0.3,0.3)
    wander_intent = Intent([0, 0], config.COLOR_WHITE, "wander")
    wander_intent.pos[0] = math.cos(ball.wander_angle) * config.WANDER_FACTOR
    wander_intent.pos[1] = math.sin(ball.wander_angle) * config.WANDER_FACTOR
    #wander_intent (end)


    #command_intent (begin)


    command_intent = Intent([0, 0], config.COLOR_ORANGE, "command")

    if player_control:
        command_factor = (1 + more_follow - more_unfollow - more_ignore)
        command_dist, command_normal = calc_normal(ball.pos, mouse_pos)
        command_intent.pos[0] += command_normal[0] * command_factor * calc_importance_factor(command_dist, command_scale,reverse=True)
        command_intent.pos[1] += command_normal[1] * command_factor * calc_importance_factor(command_dist, command_scale,reverse=True)
    elif ball.team in (config.TEAM_BLUE, config.TEAM_RED):
        own_blob = game.blue_blob if ball.team == config.TEAM_BLUE else game.red_blob
        enemy_blob = game.red_blob if ball.team == config.TEAM_BLUE else game.blue_blob
        if own_blob is not None and enemy_blob is not None:
            gather, gather_factor = team_gather_command(own_blob, enemy_blob)
            if gather:
                target = own_blob.pos
                command_factor = gather_factor
                rally_scale = max(view_scale, own_blob.radius * 2)
                command_dist, command_normal = calc_normal(ball.pos, target)
                strength = command_factor * calc_importance_factor(command_dist, rally_scale)
            else:
                target = enemy_blob.pos
                command_factor = calc_intent(own_blob, enemy_blob, 0, 0)
                command_dist, command_normal = calc_normal(ball.pos, target)
                strength = command_factor * calc_importance_factor(command_dist, command_scale)
            command_intent.pos[0] += command_normal[0] * strength
            command_intent.pos[1] += command_normal[1] * strength
            if gather:
                command_intent.pos[0] *= config.COMMAND_GATHER_INTENT_MULT
                command_intent.pos[1] *= config.COMMAND_GATHER_INTENT_MULT
    #command_intent (end)

    layer_specs = [
        ("food", total_food_intent),
        ("balls", total_ball_intent),
        ("wall", wall_intent),
        ("wander", wander_intent),
        ("command", command_intent),
    ]
    _apply_intent_budget(layer_specs)
    intents = [layer for _, layer in layer_specs]

    ball.intents = intents
    total_intent = Intent([0, 0], config.COLOR_GREEN, "total")
    if not ball.smooth_intents:
        ball.smooth_intents = ball.intents
    for intent_id in range(len(ball.intents)):
        layer = ball.intents[intent_id]
        keep = 1 - config.FOOD_INTENT_SMOOTH_STEP if layer.name == "food" else (
            1 - config.BALL_INTENT_SMOOTH_STEP if layer.name == "balls" else 0.7
        )
        ball.smooth_intents[intent_id].pos = smooth_add_pos(
            ball.smooth_intents[intent_id].pos,
            layer.pos,
            keep=keep,
        )
        total_intent.pos[0] += ball.smooth_intents[intent_id].pos[0]
        total_intent.pos[1] += ball.smooth_intents[intent_id].pos[1]

    ball.total_intent = total_intent
    ball.smooth_total_intent = Intent(
        smooth_add_pos(ball.smooth_total_intent.pos, ball.total_intent.pos),
        config.COLOR_RED,
        "total_smooth",
    )
    offset = ball.smooth_total_intent.pos
    offset_len = math.hypot(offset[0], offset[1])
    if offset_len < 1e-9:
        return ball.pos
    scale = config.INTENT_LOOK_AHEAD / offset_len
    return (ball.pos[0] + offset[0] * scale, ball.pos[1] + offset[1] * scale)

            

