import config
from input.input_handler import handle_player_input
from systems import ai_system, physics


class GameState:
    def __init__(self, entities):
        self.entities = entities

    def update(self, dt, screen_width, screen_height):
        for e in self.entities:
            e.force = [0, 0]

        handle_player_input(self.entities[0], screen_width, screen_height)
        ai_system.update_ai(self.entities, dt)
        physics.apply_forces(self.entities, dt)
        physics.apply_absorption(self.entities, dt)
        physics.apply_dynamics(self.entities, dt)
        self.entities = physics.filter_dead_entities(self.entities)

        physics.apply_movement(self.entities, dt)
        physics.apply_boundaries(self.entities, dt)
