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

        self.balls = []
        self.balls_hash = defaultdict(list)

        self.foods = []
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

    def make_balls(self,cell_pos):
        orange_food = [food for food in self.food_hash[cell_pos] if food.team==config.TEAM_RED]
        green_food = [food for food in self.food_hash[cell_pos] if food.team==config.TEAM_BLUE]
        blue_balls_num = len(green_food)//config.MINIMUM_MASS
        balls_pos = (cell_pos[0]*config.MINIMUM_MASS,cell_pos[1]*config.MINIMUM_MASS)
        for i in range(blue_balls_num):
            new_ball=Ball(balls_pos,config.COLOR_BLUE,team=config.TEAM_BLUE)
            self.balls.append(new_ball)
            self._register_ball_in_hash(new_ball)
        for i in range(blue_balls_num*config.MINIMUM_MASS):
            green_food[i].is_alive=False
        self.blue_score-=blue_balls_num*config.MINIMUM_MASS

        red_balls_num = len(orange_food)//config.MINIMUM_MASS
        for i in range(red_balls_num):
            new_ball = Ball(balls_pos,config.COLOR_RED,team=config.COLOR_RED)
            self.balls.append(new_ball)
            self._register_ball_in_hash(new_ball)

        for i in range(red_balls_num*config.MINIMUM_MASS):
            orange_food[i].is_alive=False
        self.red_score-=red_balls_num*config.MINIMUM_MASS

        self.food_hash[cell_pos]=orange_food+green_food

    def create_food(self,pos):
        new_food = Food(pos)
        self.foods.append(new_food)
        cell_pos = self._cell_pos(new_food.pos)
        self.food_hash[cell_pos].append(new_food)
        orientation = new_food.pos[0]//(config.WINDOW_WIDTH//2)
        if orientation==config.TEAM_BLUE:
            new_food.team=config.TEAM_BLUE
            new_food.color = config.COLOR_GREEN
            self.blue_score+=new_food.mass
        elif orientation==config.TEAM_RED:
            new_food.team=config.TEAM_RED
            new_food.color = config.COLOR_ORANGE
            self.red_score+=new_food.mass
        else:
            raise TypeError
        if len(self.food_hash[cell_pos])>=5:
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
        ball.lost_mass_to_spawn+=ball.old_mass-ball.mass               
        while ball.lost_mass_to_spawn>=config.MINIMUM_MASS:
            random_R = random.uniform(ball.radius+ball.radius*0.1,ball.radius+ball.radius*0.2)
            random_angle = random.uniform(0,2*math.pi)
            pos_x = max(0,min(config.WINDOW_WIDTH,ball.pos[0]+random_R*math.cos(random_angle)))
            pos_y = max(0,min(config.WINDOW_HEIGHT,ball.pos[1]+random_R*math.sin(random_angle)))
            food_pos = (pos_x,pos_y)
            self.create_food(food_pos)
            ball.lost_mass_to_spawn -= config.FOOD_MASS
    
    def update_ball_mass(self,ball,dt):
        ball.old_mass=ball.mass

        factor = 1
        for predator in ball.is_eaten_by:
            factor+=1/(predator.radius-ball.radius)
        for food in ball.eats:
            ball.mass+=food.mass
        if factor>100:
            print(factor)
        new_mass = config.MINIMUM_MASS+(ball.mass-config.MINIMUM_MASS)*0.99**(dt+factor)
        ball.mass = new_mass
        ball.eats.clear()

    def update_ball_pos(self,ball):
        ball.old_pos = (ball.pos[0],ball.pos[1])
        if ball == self.balls[0]:
                ball.view_point = pygame.mouse.get_pos()
        else:
            ball.view_point = ai.ai(ball)
        normal = ball.normal
        speed = ball.speed
        new_x = max(ball.radius,min(config.WINDOW_WIDTH-ball.radius,ball.pos[0]+ normal[0]*speed))
        new_y = max(ball.radius,min(config.WINDOW_HEIGHT-ball.radius,ball.pos[1] + normal[1]*speed))
        ball.pos = (new_x,new_y)

    def update_ball_status(self,ball,neighbours,dt):
        self.update_interseptions(ball,neighbours)
        self.update_ball_mass(ball,dt)
        self.update_delta_mass_to_food(ball)
        if ball.mass<=config.MINIMUM_MASS:
            for i in range(config.MINIMUM_MASS):
                self.create_food(ball.pos)
            ball.is_alive=False
        else:
            self.update_ball_pos(ball)
        
    def update_food_status(self,food):
        if food.is_eaten_by:
            consumer = next(iter(food.is_eaten_by))
            consumer.eats.add(food)
            food.is_alive=False

    def get_neighbours(self,cell_poses):
        neighbours = set()
        for cell_pos in cell_poses:
            neighbours.update(self.balls_hash[cell_pos])
            neighbours.update(self.food_hash[cell_pos])
        return list(neighbours)
    def existion_update(self, balls,foods):
        for ball in balls:
            if not(ball.is_alive):
                ball_cells = self.get_ball_cells(ball.pos,ball.radius)
                for cell_pos in ball_cells:
                    self.balls_hash[cell_pos].remove(ball)
                self.balls.remove(ball)
        for food in foods:
            if not(food.is_alive):
                cell_pos = self._cell_pos(food.pos)
                self.food_hash[cell_pos].remove(food)
                self.foods.remove(food)


    def update(self,dt):
        for ball in self.balls:
            current_ball_grid_cells = self.update_hash(ball,ball.old_pos,ball.old_radius)

            neighbours = self.get_neighbours(current_ball_grid_cells)
            self.update_ball_status(ball,neighbours,dt)
        for food in self.foods:
            self.update_food_status(food)
        
        self.existion_update(self.balls,self.foods)

