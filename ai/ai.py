from re import S
import config
import math
import statistics

from entities import food, intent, ball as Ball

import pygame

from utils.smooth_normal import smooth_add_pos
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
    merge_factor = (1/(1+ neighbour.radius-ball.radius))
    if neighbour.team!=ball.team:
        danger_factor -= 1 + more_follow - more_unfollow
    else:
        if abs(neighbour.radius-ball.radius)<config.MINIMUM_MASS:
            ally_factor += 1/10 + more_follow - more_unfollow
    ball_factor = (danger_factor+ally_factor)*merge_factor
    return ball_factor

def calc_importance_factor(dist):
    if dist==0:
        return 0
    return config.FOOD_MASS/(0.1*dist)+config.IMPORTANCE_KOEF
def ai(ball:Ball.Ball,neighbours:list):
    mouse_keys = pygame.mouse.get_pressed()
    mouse_pos = pygame.mouse.get_pos()
    keyboard_keys = pygame.key.get_pressed()
    space = keyboard_keys[pygame.K_SPACE]
    more_follow = mouse_keys[0]
    more_unfollow = 2*mouse_keys[2]
    more_ignore = mouse_keys[1]
    ball.sharing_food_factor = space

    #reflex_intent (begin)
    total_reflex_intent = intent.Intent([0,0],config.COLOR_BLACK)
    for neighbour in neighbours:
        dist,normal = calc_normal(ball.pos,neighbour.pos)
        future_dist = 0
        if dist==0:
            continue

        ball_factor=0
        if isinstance(neighbour,Ball.Ball):
            
            ball_factor+=calc_intent(ball,neighbour,more_follow=more_follow,more_unfollow = more_unfollow)

            neighbour_future_pos = (neighbour.pos[0]+neighbour.normal[0]*neighbour.speed,
                                        neighbour.pos[1]+neighbour.normal[1]*neighbour.speed)
            future_dist,future_normal = calc_normal(ball.pos,neighbour_future_pos)

        reflex_factor = (1+ball_factor)*(calc_importance_factor(dist)+0.3*calc_importance_factor(future_dist))
        reflex_intent = (normal[0]*reflex_factor,
                        normal[1]*reflex_factor)
        total_reflex_intent.pos[0]+=reflex_intent[0]
        total_reflex_intent.pos[1]+=reflex_intent[1]
    #reflex_intent(end)

    #wall_intent (begin)
    wall_intent = intent.Intent([0,0],config.COLOR_BLACK)
    wall_dist_left = ball.pos[0]
    wall_dist_right = config.WINDOW_WIDTH-ball.pos[0]
    wall_dist_down = ball.pos[1]
    wall_dist_top = config.WINDOW_HEIGHT-ball.pos[1]

    if wall_dist_left<ball.radius*3:
        wall_intent.pos[0]+=1/(1+wall_dist_left)**2
    if wall_dist_down<ball.radius*3:
        wall_intent.pos[1]+=1/(1+wall_dist_down)**2
    if wall_dist_right<ball.radius*3:
        wall_intent.pos[0]-=1/(1+wall_dist_right)**2
    if wall_dist_top<ball.radius:
        wall_intent.pos[1]-=1/(1+wall_dist_top)**2
    #wall_intent (end)



    intents = [total_reflex_intent,wall_intent]



    #command_intent (begin)

    max_intent = max(intents, key=lambda b: math.hypot(b.pos[0], b.pos[1]))    
    max_intent_length = math.hypot(max_intent.pos[0],max_intent.pos[1])
    command_factor = (1 + more_follow - more_unfollow - more_ignore)*(max_intent_length+1)
    command_intent = intent.Intent([0,0],config.COLOR_ORANGE)
    if ball.team==config.TEAM_BLUE:
        command_dist,command_normal = calc_normal(ball.pos,mouse_pos)
        command_intent.pos[0] += command_normal[0] * command_factor *calc_importance_factor(command_dist)
        command_intent.pos[1] += command_normal[1]*command_factor*calc_importance_factor(command_dist)
    #command_intent (end)
    intents.append(command_intent)
    ball.intents=intents
    total_intent= intent.Intent([0,0],config.COLOR_GREEN)
    if not ball.smooth_intents:
        ball.smooth_intents=ball.intents
    for intent_id in range(len(ball.intents)):

        ball.smooth_intents[intent_id].pos = smooth_add_pos(ball.smooth_intents[intent_id].pos,
                                        ball.intents[intent_id].pos)
        total_intent.pos[0]+=ball.smooth_intents[intent_id].pos[0]
        total_intent.pos[1]+=ball.smooth_intents[intent_id].pos[1]
    ball.total_intent = total_intent
    ball.smooth_total_intent = intent.Intent(smooth_add_pos(ball.smooth_total_intent.pos,
                                            ball.total_intent.pos),config.COLOR_RED)
    return (ball.pos[0]+ball.smooth_total_intent.pos[0],ball.pos[1]+ball.smooth_total_intent.pos[1])
            

