import config
import math
from collections import defaultdict
import pygame
import random
from entities import ball,food
from ai import ai
Ball = ball.Ball
Food = food.Food
print(Ball)
class Game:
    def __init__(self,time,start_mass):
        self.time = time
        self.start_time=0
        self.start_mass=start_mass
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





    def make_balls(self,cell_pos):
        orange_food = [food for food in self.food_hash[cell_pos] if food.team==config.TEAM_RED]
        green_food = [food for food in self.food_hash[cell_pos] if food.team==config.TEAM_BLUE]
        blue_balls_num = len(green_food)//config.MINIMUM_MASS
        balls_pos = (cell_pos[0]*config.MINIMUM_MASS,cell_pos[1]*config.MINIMUM_MASS)
        for i in range(blue_balls_num):
            new_ball=Ball(balls_pos,config.COLOR_BLUE,team=config.TEAM_BLUE)
            self.balls.append(new_ball)
            self.balls_hash[cell_pos].append(new_ball)
            self.check_intersetptions([cell_pos],new_ball)
        for i in range(blue_balls_num*config.MINIMUM_MASS):
            green_food[i].is_alive=False
        self.blue_score-=blue_balls_num*config.MINIMUM_MASS

        red_balls_num = len(orange_food)//config.MINIMUM_MASS
        for i in range(red_balls_num):
            new_ball = Ball(balls_pos,config.COLOR_RED,team=config.COLOR_RED)
            self.balls.append(new_ball)
            self.balls_hash[cell_pos].append(new_ball)
            self.check_intersetptions([cell_pos],new_ball)

        for i in range(red_balls_num*config.MINIMUM_MASS):
            orange_food[i].is_alive=False
        self.red_score-=red_balls_num*config.MINIMUM_MASS

        self.food_hash[cell_pos]=orange_food+green_food


    def create_food(self,pos):
        new_food = Food(pos)
        self.foods.append(new_food)
        cell_pos = (new_food.pos[0]//config.MINIMUM_MASS,new_food.pos[1]//config.MINIMUM_MASS)
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
        self.check_intersetptions([cell_pos],new_food)
        if len(self.food_hash[cell_pos])>=5:
            self.make_balls(cell_pos)
        
    def interseption_update(self,cell_poses:list,ball):
        seen = set()
        for cell_pos in cell_poses:
            foods = self.food_hash.get(cell_pos,[])
            balls = self.balls_hash.get(cell_pos,[])
            
            for neighbour in balls:
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
                    continue

                if predator.radius*predator.radius>dx*dx+dy*dy:
                    victum.is_eaten_by.add(predator)
                else:
                    victum.is_eaten_by.discard(predator)
            
            for food in foods:
                dx = food.pos[0]-ball.pos[0]
                dy = food.pos[1]-ball.pos[1]

                if ball.radius*ball.radius>dx*dx+dy*dy:
                    food.is_eaten_by.add(ball)
                else:
                    food.is_eaten_by.discard(ball)

  



    def update_hash(self,ball,old_pos,old_radius):
        """
        отвечает за актуализацию отображения шарика на соответствующие клетки
        """

        # находим старые клетки (начало)
        x_start_old = int((old_pos[0]-old_radius)//config.MINIMUM_MASS)
        x_end_old = int((old_pos[0]+old_radius)//config.MINIMUM_MASS)
        y_start_old = int((old_pos[1]-old_radius)//config.MINIMUM_MASS)
        y_end_old = int((old_pos[1]+old_radius)//config.MINIMUM_MASS)
        cell_pos_old = set()
        
        for x_cell in range(x_start_old,x_end_old+1):
            for y_cell in range(y_start_old,y_end_old+1):
                cell_pos_old.add((x_cell,y_cell))
        # находим старые клетки (конец)

        #находим новые клетки (начало)
        x_start = int((ball.pos[0]-ball.radius)//config.MINIMUM_MASS)
        x_end = int((ball.pos[0]+ball.radius)//config.MINIMUM_MASS)
        y_start = int((ball.pos[1]-ball.radius)//config.MINIMUM_MASS)
        y_end = int((ball.pos[1]+ball.radius)//config.MINIMUM_MASS)
        cell_pos_current = set()

        for x_cell in range(x_start,x_end+1):
            for y_cell in range(y_start,y_end+1):
                cell_pos_current.add((x_cell,y_cell))
        #находим новые клетки (конец)

        #актуализируем отображение шарика на клетки (начало)
        cell_pos_fantom = cell_pos_old-cell_pos_current
        cell_pos_new = cell_pos_current-cell_pos_old

        for cell_pos in cell_pos_new:
            self.balls_hash[cell_pos].append(ball)

        for cell_pos in cell_pos_fantom:
            self.balls_hash[cell_pos].remove(ball)
        
            if not self.balls_hash[cell_pos]: del self.balls_hash[cell_pos]
        #актуализируем отображение шарика на клетки (конец)

                    
                    
    def consume(self,food:list,dt):
        """
        отвечает за применение разиличного влияния к еде что поедается в данный момент
        на вход принимает список еды к которой нужно применить влияние
        """
        # определяем влияние на еду что ещё имеет ценность (alive) (начало)
        for food_object in food:
            if food_object.is_alive:

                # определяем влияние на еду которая еда
                if isinstance(food_object,Food):
                    if food_object.is_eaten_by:
                        consumer = next(iter(food_object.is_eaten_by)) 
                        consumer.mass += food_object.mass 
                        food_object.is_alive=False 
                        food_object.is_eaten_by=set() 
                

                # определяем влияние на еду которая шарик
                else:
                    old_radius = food_object.radius 
                    total_factor = 0
                    for consumer in food_object.is_eaten_by:
                        total_factor += 1/(consumer.radius-food_object.radius)
                        if food_object.mass==config.MINIMUM_MASS: 
                            food_object.is_alive = False 
                        for i in range(config.MINIMUM_MASS): 
                            self.create_food(food_object.pos)
                    self.mass_food_convertation_step(food_object,dt*total_factor) 
                    self.update_hash(food_object,old_pos=food_object.pos,old_radius=old_radius)

        # определяем влияние на еду что ещё имеет ценность (alive) (конец)    

        #определяем влияние на еду что уже не имеет ценности (not alive) (начало)
        for food_object in food: 
            cell_pos = (food_object.pos[0]//config.MINIMUM_MASS,food_object.pos[1]//config.MINIMUM_MASS) 
            if not (food_object.is_alive): 
                if isinstance(food_object,Food): 
                    self.food_hash[cell_pos] = [food_object for food_object in self.food_hash[cell_pos] if food_object.is_alive]
                    self.foods = [food_object for food_object in self.foods if food_object.is_alive]
                if isinstance(food_object,Ball):
                    self.balls_hash[cell_pos] = [ball for ball in self.balls_hash[cell_pos] if ball.is_alive]
                    self.balls = [ball for ball in self.balls if ball.is_alive]
        #определяем влияние на еду что уже не имеет ценности (not alive) (конец)      

    def mass_food_convertation_step(self,ball,dt):

        new_mass = config.MINIMUM_MASS + (ball.mass-config.MINIMUM_MASS)*(0.99)**(dt)
        ball.lost_mass_to_spawn += ball.mass-new_mass
        while ball.lost_mass_to_spawn>=config.FOOD_MASS:
            random_R = random.uniform(ball.radius+ball.radius*0.1,ball.radius+ball.radius*0.2)
            random_angle = random.uniform(0,2*math.pi)
            pos_x = max(0,min(config.WINDOW_WIDTH,ball.pos[0]+random_R*math.cos(random_angle)))
            pos_y = max(0,min(config.WINDOW_HEIGHT,ball.pos[1]+random_R*math.sin(random_angle)))
            food_pos = (pos_x,pos_y)
            self.create_food(food_pos)
            ball.lost_mass_to_spawn -= config.FOOD_MASS
        ball.mass = new_mass

    def pos_update(self,ball):
        if ball == self.balls[0]:
                ball.view_point = pygame.mouse.get_pos()
        else:
            ball.view_point = ai.ai(ball)
        normal = ball.normal
        speed = ball.speed
        new_x = max(ball.radius,min(config.WINDOW_WIDTH-ball.radius,ball.pos[0]+ normal[0]*speed))
        new_y = max(ball.radius,min(config.WINDOW_HEIGHT-ball.radius,ball.pos[1] + normal[1]*speed))
        old_pos = (ball.pos[0],ball.pos[1])
        ball.pos = (new_x,new_y)

        self.update_hash(ball,old_pos=old_pos,old_radius=ball.radius) # оптимизация

    def update(self,dt):
        for ball in self.balls:
            self.pos_update(ball)
            self.intersetption_update(ball)
            self.mass_update(ball,dt)

        self.existion_update([object for object in self.balls+self.foods])

