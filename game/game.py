from re import escape
import config
import math
from collections import defaultdict
import pygame
import random
from entities import ball,food
from ai import ai
from utils.utils import calc_mass_center
Ball = ball.Ball
Food = food.Food

class TeamBlob:
    def __init__(self, pos, mass, team):
        self.pos = pos
        self.mass = mass
        self.team = team

    @property
    def radius(self):
        return math.sqrt(self.mass)

class Game:
    def __init__(self, time, control_mode=None):
        self.time = time
        self.control_mode = control_mode or config.CONTROL_MODE
        self.start_time=0
        self.start_mass=config.START_MASS
        self.is_over=False
        self.player_ball = None
        self.balls = set()
        self.balls_hash = defaultdict(list)

        self.foods = set()
        self.food_hash = defaultdict(list)

        self.red_blob = None
        self.blue_blob = None

    def _make_team_blob(self, team):
        team_balls = [b for b in self.balls if b.team == team]
        if not team_balls:
            return None
        center = calc_mass_center(team_balls)
        if center is None:
            return None
        total_mass = sum(b.mass for b in team_balls)
        return TeamBlob(center, total_mass, team)

    def update_team_blobs(self):
        self.red_blob = self._make_team_blob(config.TEAM_RED)
        self.blue_blob = self._make_team_blob(config.TEAM_BLUE)

    def draw_team_blobs(self, screen, fill_alpha=40, outline_alpha=140):
        for blob in (self.red_blob, self.blue_blob):
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

    def team_mass(self, team):
        return sum(b.mass for b in self.balls if b.team == team)

    def start(self):
        margin = config.FOOD_DISTANCE_FACTOR
        for _ in range(self.start_mass):
            pos = (
                random.uniform(config.WINDOW_WIDTH * margin, config.WINDOW_WIDTH * (1 - margin)),
                random.uniform(config.WINDOW_HEIGHT * margin, config.WINDOW_HEIGHT * (1 - margin)),
            )
            self.create_food(pos)
        self.start_time = pygame.time.get_ticks()

    def _cell_pos(self, pos):
        return (int(pos[0] // config.CELL_SIZE), int(pos[1] // config.CELL_SIZE))

    def _register_ball_in_hash(self, ball):
        for cell_pos in self.get_ball_cells(ball.pos, ball.radius):
            if ball not in self.balls_hash[cell_pos]:
                self.balls_hash[cell_pos].append(ball)

    def _add_ball(self, ball):
        self.balls.add(ball)
        if (
            self.control_mode == config.CONTROL_MODE_PLAYER
            and self.player_ball is None
            and ball.team == config.PLAYER_TEAM
        ):
            self.player_ball = ball
            self.player_ball.color = config.COLOR_ORANGE
        self._register_ball_in_hash(ball)

 

    def _remove_ball(self, ball):
        for cell_pos in self.get_ball_cells(ball.pos, ball.radius):
            if ball in self.balls_hash[cell_pos]:
                self.balls_hash[cell_pos].remove(ball)
            if not self.balls_hash[cell_pos]:
                del self.balls_hash[cell_pos]
        self.balls.discard(ball)
        for i in range(config.DEATH_MASS):
             self.create_food(ball.pos)



    def _remove_food(self, food, cell_pos=None):
        if cell_pos is None:
            cell_pos = self._cell_pos(food.pos)
        if food in self.food_hash[cell_pos]:
            self.food_hash[cell_pos].remove(food)
        if not self.food_hash[cell_pos]:
            del self.food_hash[cell_pos]
        self.foods.discard(food)

    def create_food(self, pos):
        pos_x = max(config.WINDOW_WIDTH*config.FOOD_DISTANCE_FACTOR,min(config.WINDOW_WIDTH*(1-config.FOOD_DISTANCE_FACTOR),pos[0]))
        pos_y = max(config.WINDOW_HEIGHT*config.FOOD_DISTANCE_FACTOR,min(config.WINDOW_HEIGHT*(1-config.FOOD_DISTANCE_FACTOR),pos[1]))
        new_food = Food((pos_x, pos_y))
        new_food.color = config.COLOR_GREEN
        self.foods.add(new_food)
        cell_pos = self._cell_pos(new_food.pos)
        self.food_hash[cell_pos].append(new_food)

    def split_ball(self, ball):
        if ball not in self.balls or ball.mass < 2 * config.MINIMUM_MASS:
            return
        old_radius = ball.radius
        half_mass = ball.mass / 2
        ball.mass = half_mass
        ball.old_mass = half_mass
        dx, dy = ball.normal
        if math.hypot(dx, dy) < 1e-9:
            dx = math.cos(ball.wander_angle)
            dy = math.sin(ball.wander_angle)
        new_x = ball.pos[0] + dx * old_radius
        new_y = ball.pos[1] + dy * old_radius
        r = math.sqrt(half_mass)
        new_x = max(r, min(config.WINDOW_WIDTH - r, new_x))
        new_y = max(r, min(config.WINDOW_HEIGHT - r, new_y))
        new_ball = Ball((new_x, new_y), ball.color, half_mass, ball.team)
        self._add_ball(new_ball)

    def update_interseptions(self,ball,neighbours):
        seen = set()
        for neighbour in neighbours:
            if neighbour is ball or neighbour in seen:
                continue
            seen.add(neighbour)

            dx = neighbour.pos[0]-ball.pos[0]
            dy = neighbour.pos[1]-ball.pos[1]
            if ball.radius>neighbour.radius:
                predator = ball
                victum = neighbour
            elif ball.radius<neighbour.radius:
                predator=neighbour
                victum=ball
            else:
                ball.eats.discard(neighbour)
                neighbour.eats.discard(ball)
                ball.is_eaten_by.discard(neighbour)
                neighbour.is_eaten_by.discard(ball)
                continue
            
            if predator.radius*predator.radius>dx*dx+dy*dy:
                if isinstance(victum, Food) and victum.is_eaten_by:
                    continue
                victum.is_eaten_by.add(predator)
                if isinstance(victum,Food):
                    predator.eats.add(victum)
            else:
                victum.is_eaten_by.discard(predator)
                if isinstance(victum,Food):
                    predator.eats.discard(victum)

  

    def get_ball_cells(self,pos,radius):
        x_start = int((pos[0]-radius)//config.CELL_SIZE)
        x_end = int((pos[0]+radius)//config.CELL_SIZE)
        y_start = int((pos[1]-radius)//config.CELL_SIZE)
        y_end = int((pos[1]+radius)//config.CELL_SIZE)
        cell_pos_current = set()
        for x_cell in range(x_start,x_end+1):
            for y_cell in range(y_start,y_end+1):
                cell_pos_current.add((x_cell,y_cell))
        return cell_pos_current
    
    def update_hash(self,ball,old_pos,old_radius):

        cell_pos_old = self.get_ball_cells(old_pos,old_radius)

        cell_pos_current = self.get_ball_cells(ball.pos,ball.radius)

        cell_pos_fantom = cell_pos_old-cell_pos_current
        cell_pos_new = cell_pos_current-cell_pos_old

        for cell_pos in cell_pos_new:
            self.balls_hash[cell_pos].append(ball)
        for cell_pos in cell_pos_fantom:
            self.balls_hash[cell_pos].remove(ball)
    
            if not self.balls_hash[cell_pos]: del self.balls_hash[cell_pos]

        return cell_pos_current
                    
    def update_delta_mass_to_food(self,ball):
        if ball.mass_before_decay>ball.mass:
            ball.lost_mass_to_spawn+=ball.mass_before_decay-ball.mass
        while round(ball.lost_mass_to_spawn,2)>=config.FOOD_MASS:
            random_R = random.uniform(ball.radius+ball.radius*0.1,ball.radius+ball.radius*0.2)
            random_angle = random.uniform(0,2*math.pi)
            pos_x = ball.pos[0]+random_R*math.cos(random_angle)
            pos_y = ball.pos[1]+random_R*math.sin(random_angle)

            food_pos = (pos_x,pos_y)
            self.create_food(food_pos)
            ball.lost_mass_to_spawn -= config.FOOD_MASS
    
    def update_ball_eats(self,ball):
        ball.old_mass = ball.mass
        for food in ball.eats:
            ball.mass+=food.mass
        ball.eats.clear()
    def update_ball_mass(self,ball,dt):
        ball.mass_before_decay=ball.mass
        factor = ball.sharing_food_factor
        if ball.is_eaten_by:
            for predator in ball.is_eaten_by:
                if predator.radius>ball.radius: # пофиксить (радиусы должны быть были разные к этому моменту)
                    factor+=1+1/(predator.radius-ball.radius)
            new_mass = config.DEATH_MASS-0.1+(ball.mass-config.DEATH_MASS-0.1)*0.99**(dt+factor)
        else:
            new_mass = config.DEATH_MASS+(ball.mass-config.DEATH_MASS)*0.99**(dt+factor)

        ball.mass = new_mass



    def update_ball_pos(self,ball):
        cell_poses = self.get_ball_cells(ball.pos,ball.radius*config.BALL_VIEW_FACTOR)
        neighbours = self.get_neighbours(cell_poses)
        ball.old_pos = (ball.pos[0],ball.pos[1])
        if self.control_mode == config.CONTROL_MODE_PLAYER and ball is self.player_ball:
            ball.view_point = pygame.mouse.get_pos()
        else:
            ball.view_point = ai.ai(ball, neighbours, self)
        normal = ball.normal
        speed = ball.speed
        
        new_x = max(ball.radius,min(config.WINDOW_WIDTH-ball.radius,ball.pos[0]+ normal[0]*speed))
        new_y = max(ball.radius,min(config.WINDOW_HEIGHT-ball.radius,ball.pos[1] + normal[1]*speed))
        ball.pos = (new_x,new_y)


    def update_ball_status(self,ball,neighbours,dt):
        self.update_interseptions(ball,neighbours)
        self.update_ball_eats(ball)
        self.update_ball_mass(ball,dt)
        self.update_delta_mass_to_food(ball)

        if round(ball.mass,2)<=config.DEATH_MASS:
            self._remove_ball(ball)
        else:
            self.update_ball_pos(ball)
        
    def update_food_status(self,food):
        if food.is_eaten_by:

            self._remove_food(food)

    def get_neighbours(self,cell_poses):
        neighbours = set()
        for cell_pos in cell_poses:
            neighbours.update(self.balls_hash[cell_pos])
            neighbours.update(self.food_hash[cell_pos])
        return list(neighbours)

    def update(self,dt):
        self.update_team_blobs()
        for ball in list(self.balls):
            current_ball_grid_cells = self.update_hash(ball,ball.old_pos,ball.old_radius)
            neighbours = self.get_neighbours(current_ball_grid_cells)

            self.update_ball_status(ball,neighbours,dt)
        for food in list(self.foods):
            self.update_food_status(food)

