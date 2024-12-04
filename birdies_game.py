import numpy as np
import pygame
import random
import variables
from Checkbox import Checkbox
from Slider import Slider
from Button import Button
from predator import Predator
from prey import Prey

# Initialize Pygame
pygame.init()

pygame.display.set_caption("Predator-Prey Simulation")

# Control Panel
panel_height = variables.screen_height
panel_x = variables.screen_width - variables.panel_width
panel_rect = pygame.Rect(panel_x, 0, variables.panel_width, panel_height)

# Create checkbox
checkbox = Checkbox(panel_x + 20, 300, 20, variables.show_zones, "Show Zones")

# Create theme toggle button
theme_button = Button(panel_x + 20, 350, 160, 30, "Toggle Dark/Light Mode")

# Create sliders
sliders = [
    Slider(panel_x + 20, 50, variables.panel_width - 40, 20, 0.0, 1.0, variables.inertia, "Inertia"),
    Slider(panel_x + 20, 100, variables.panel_width - 40, 20, 1, 100, variables.collision_zone_radius,
           "Collision Radius"),
    Slider(panel_x + 20, 150, variables.panel_width - 40, 20, 1, 100, variables.interaction_zone_radius,
           "Interaction Radius"),
    Slider(panel_x + 20, 200, variables.panel_width - 40, 20, 0.0, 2.0, variables.shift_to_buddy, "Shift to Buddy"),
]


class Game:
    def __init__(self, num_birds=10, predator_ratio=0.3):
        self.num_birds = num_birds
        self.predator_ratio = predator_ratio
        self.screen_width = variables.screen_width
        self.screen_height = variables.screen_height
        self.birds = []
        pygame.init()
        pygame.display.set_caption("Predator-Prey Simulation")

        self.create_birds()

    def create_birds(self):
        num_predators = int(self.num_birds * self.predator_ratio)
        num_prey = self.num_birds - num_predators
        
        # Create both predators and prey
        for is_predator in [True, False]:
            num_to_create = num_predators if is_predator else num_prey
            for _ in range(num_to_create):
                while True:
                    x = random.randint(variables.BORDER_THICKNESS, 
                                    self.screen_width - variables.panel_width - variables.BORDER_THICKNESS)
                    y = random.randint(variables.BORDER_THICKNESS, 
                                    self.screen_height - variables.BORDER_THICKNESS)

                    # Check if the bird is inside any restricted area
                    if not self.is_inside_restricted_areas(x, y):
                        break

                dx = random.uniform(-1, 1)
                dy = random.uniform(-1, 1)
                
                # Create appropriate bird type
                bird = Predator(dx, dy) if is_predator else Prey(dx, dy)
                self.birds.append(bird)
                variables.X.append(x)
                variables.Y.append(y)
        
        variables.X = np.array(variables.X)
        variables.Y = np.array(variables.Y)

    def is_inside_restricted_areas(self, x, y):
        for rect in variables.restricted_areas:
            rect_x, rect_y, rect_width, rect_height = rect
            if (rect_x < x < rect_x + rect_width) and (rect_y < y < rect_y + rect_height):
                return True
        return False

    def run(self):
        running = True
        while running:
            # Handle slider updates
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEMOTION:
                    if pygame.mouse.get_pressed()[0]:  # Left mouse button held down
                        mouse_pos = pygame.mouse.get_pos()
                        checkbox.update(mouse_pos)
                        theme_button.update(mouse_pos)
                        for slider in sliders:
                            slider.update(mouse_pos)

            # Update birds
            self.update()
            # Draw board and birds
            self.draw()

            # Draw control panel
            theme = variables.get_current_theme()
            pygame.draw.rect(variables.screen, theme['panel'], panel_rect)

            # Draw sliders
            for slider in sliders:
                slider.draw(variables.screen)
            # Draw checkbox
            checkbox.draw(variables.screen)
            # Draw theme button
            theme_button.draw(variables.screen)

            # Update global parameters from sliders
            variables.inertia = sliders[0].val
            variables.collision_zone_radius = sliders[1].val
            variables.interaction_zone_radius = sliders[2].val
            variables.shift_to_buddy = sliders[3].val
            variables.show_zones = checkbox.state

            pygame.display.flip()

        pygame.quit()

    def update(self):
        # Calculate distances between all the couples of birds
        disx = variables.X[:, np.newaxis] - variables.X  # Calculate x-differences for all pairs
        disy = variables.Y[:, np.newaxis] - variables.Y  # Calculate y-differences for all pairs
        distances = np.hypot(disx, disy)  # Calculate distances for all pairs

        this_step_interactions = {}

        for bird_index, bird in enumerate(self.birds):  # Iterate using index
            this_step_interactions[bird_index] = {}
            bird.update(bird_index, self.birds, distances, this_step_interactions)  # Pass the bird's index

    def draw(self):
        theme = variables.get_current_theme()
        variables.screen.fill(theme['background'])
        
        # Draw solid borders
        pygame.draw.rect(variables.screen, theme['border'], 
                        (variables.BORDER_THICKNESS, variables.BORDER_THICKNESS,
                         self.screen_width - variables.panel_width - 2 * variables.BORDER_THICKNESS,
                         self.screen_height - 2 * variables.BORDER_THICKNESS),
                        2)  # Border with thickness of 2

        # Draw all restricted areas
        for rect in variables.restricted_areas:
            rect_x, rect_y, rect_width, rect_height = rect
            pygame.draw.rect(variables.screen, theme['restricted'],
                           (rect_x, rect_y, rect_width, rect_height))

        for bird_index, bird in enumerate(self.birds):
            bird.draw(bird_index)


if __name__ == "__main__":
    game = Game()
    game.run()
