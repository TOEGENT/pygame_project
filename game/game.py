import config
import math
from collections import defaultdict
import pygame
import random
from entities import ball,food
from ai import ai
Ball = ball.Ball
Food = food.Food
class Game:
    def __init__(self,time):
        self.time = time
        self.start_time=0
        self.start_mass=config.START_MASS
        self.blue_score=0
        self.red_score=0
        self.is_over=False
        self.player_ball = None

        self.balls = set()
        self.balls_hash = defaultdict(list)

        self.foods = set()
        self.food_hash = defaultdict(list)

    def start(self):
        for food in range(self.start_mass):
            blue_pos = (random.uniform(0,(config.WINDOW_WIDTH//2)*0.95),random.uniform(0,config.WINDOW_HEIGHT))
            self.create_food(blue_pos)
            red_pos = (random.uniform((config.WINDOW_WIDTH//2)*1.05,config.WINDOW_WIDTH),random.uniform(0,config.WINDOW_HEIGHT))
            self.create_food(red_pos)
        self.start_time = pygame.time.get_ticks()

    def _cell_pos(self, pos):
        return (int(pos[0] // config.MINIMUM_MASS), int(pos[1] // config.MINIMUM_MASS))

    def _register_ball_in_hash(self, ball):
        for cell_pos in self.get_ball_cells(ball.pos, ball.radius):
            if ball not in self.balls_hash[cell_pos]:
                self.balls_hash[cell_pos].append(ball)

    def _add_ball(self, ball):
        self.balls.add(ball)
        if self.player_ball is None:
            self.player_ball = ball
            self.player_ball.color = config.COLOR_ORANGE
            #pass
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
        if food.team==config.TEAM_BLUE:
            self.blue_score-=1
        elif food.team == config.TEAM_RED:
            self.red_score-=1
        else:
            raise TypeError

    def make_balls(self,cell_pos):

        green_food = [food for food in self.food_hash[cell_pos] if food.team==config.TEAM_BLUE]
        orange_food = [food for food in self.food_hash[cell_pos] if food.team==config.TEAM_RED]
        blue_balls_num = len(green_food)//config.MINIMUM_MASS
        balls_pos = (cell_pos[0]*config.MINIMUM_MASS,cell_pos[1]*config.MINIMUM_MASS)
        for i in range(blue_balls_num):
            new_ball=Ball(balls_pos,config.COLOR_BLUE,team=config.TEAM_BLUE)
            self._add_ball(new_ball)
        for i in range(blue_balls_num*config.MINIMUM_MASS):
            self._remove_food(green_food[i], cell_pos)
        red_balls_num = len(orange_food)//config.MINIMUM_MASS
        for i in range(red_balls_num):
            new_ball = Ball(balls_pos,config.COLOR_RED,team=config.TEAM_RED)
            self._add_ball(new_ball)

        for i in range(red_balls_num*config.MINIMUM_MASS):
            self._remove_food(orange_food[i], cell_pos)

    def create_food(self,pos):
        new_food = Food(pos)
        self.foods.add(new_food)
        cell_pos = self._cell_pos(new_food.pos)
        self.food_hash[cell_pos].append(new_food)
       
        half = config.WINDOW_WIDTH/2
        if new_food.pos[0]<half:
            new_food.team=config.TEAM_BLUE
            new_food.color = config.COLOR_GREEN
            self.blue_score+=new_food.mass
        elif new_food.pos[0]>half:
            new_food.team=config.TEAM_RED
            new_food.color = config.COLOR_ORANGE
            self.red_score+=new_food.mass
        else:
            raise TypeError
        if len(self.food_hash[cell_pos])>=config.MINIMUM_MASS:
            self.make_balls(cell_pos)
        
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
        x_start = int((pos[0]-radius)//config.MINIMUM_MASS)
        x_end = int((pos[0]+radius)//config.MINIMUM_MASS)
        y_start = int((pos[1]-radius)//config.MINIMUM_MASS)
        y_end = int((pos[1]+radius)//config.MINIMUM_MASS)
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
        if ball.old_mass>ball.mass:
            ball.lost_mass_to_spawn+=ball.old_mass-ball.mass
        while round(ball.lost_mass_to_spawn,2)>=config.FOOD_MASS:
            random_R = random.uniform(ball.radius+ball.radius*0.1,ball.radius+ball.radius*0.2)
            random_angle = random.uniform(0,2*math.pi)
            pos_x = max(0,min(config.WINDOW_WIDTH,ball.pos[0]+random_R*math.cos(random_angle)))
            pos_y = max(0,min(config.WINDOW_HEIGHT,ball.pos[1]+random_R*math.sin(random_angle)))
            food_pos = (pos_x,pos_y)
            self.create_food(food_pos)
            ball.lost_mass_to_spawn -= config.FOOD_MASS
    
    def update_ball_mass(self,ball,dt):
        ball.old_mass=ball.mass
        for food in ball.eats:
            ball.mass+=food.mass
        if ball.is_eaten_by:
            factor = 1
            for predator in ball.is_eaten_by:
                if predator.radius>ball.radius: # пофиксить (радиусы должны быть были разные к этому моменту)
                    factor+=1/(predator.radius-ball.radius)

            new_mass = config.DEATH_MASS+(ball.mass-config.DEATH_MASS)*0.99**(factor)

        else:
            new_mass = config.DEATH_MASS+(ball.mass-config.DEATH_MASS)*0.99**(dt)
        ball.mass = new_mass

        ball.eats.clear()

    def update_ball_pos(self,ball):
        cell_poses = self.get_ball_cells(ball.pos,ball.radius*config.BALL_VIEW_FACTOR)
        neighbours = self.get_neighbours(cell_poses)
        ball.old_pos = (ball.pos[0],ball.pos[1])
        if ball is self.player_ball:
                ball.view_point = pygame.mouse.get_pos()
        else:
            ball.view_point = ai.ai(ball,neighbours)
        normal = ball.normal
        speed = ball.speed
        new_x = max(ball.radius,min(config.WINDOW_WIDTH-ball.radius,ball.pos[0]+ normal[0]*speed))
        new_y = max(ball.radius,min(config.WINDOW_HEIGHT-ball.radius,ball.pos[1] + normal[1]*speed))
        ball.pos = (new_x,new_y)


    def update_ball_status(self,ball,neighbours,dt):
        self.update_interseptions(ball,neighbours)
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
        for ball in list(self.balls):
            current_ball_grid_cells = self.update_hash(ball,ball.old_pos,ball.old_radius)
            neighbours = self.get_neighbours(current_ball_grid_cells)

            self.update_ball_status(ball,neighbours,dt)
        for food in list(self.foods):
            self.update_food_status(food)
        
