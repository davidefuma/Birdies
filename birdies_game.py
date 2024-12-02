import numpy as np
import pygame
import random
import variables
from Checkbox import Checkbox
from Slider import Slider
from bird import Bird

# Initialize Pygame
pygame.init()

pygame.display.set_caption("Birds Simulation")

# Control Panel
panel_height = variables.screen_height
panel_x = variables.screen_width - variables.panel_width
panel_rect = pygame.Rect(panel_x, 0, variables.panel_width, panel_height)

# Create checkbox
checkbox = Checkbox(panel_x + 20, 300, 20, variables.show_zones, "Show Zones")

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
    def __init__(self, num_birds=10):
        self.num_birds = num_birds
        self.screen_width = variables.screen_width
        self.screen_height = variables.screen_height
        self.birds = []
        pygame.init()
        pygame.display.set_caption("Birds Simulation")

        self.create_birds()

    def create_birds(self):
        for _ in range(self.num_birds):
            while True:
                x = random.randint(variables.BORDER_THICKNESS, self.screen_width - variables.panel_width - variables.BORDER_THICKNESS)
                y = random.randint(variables.BORDER_THICKNESS, self.screen_height - variables.BORDER_THICKNESS)

                # Check if the bird is inside any restricted area
                if not self.is_inside_restricted_areas(x, y):
                    break

            dx = random.uniform(-1, 1)
            dy = random.uniform(-1, 1)
            self.birds.append(Bird(dx, dy))  # No longer passing x, y to Bird
            variables.X.append(x)  # Store x-coordinate in the vector
            variables.Y.append(y)  # Store y-coordinate in the vector
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
                        for slider in sliders:
                            slider.update(mouse_pos)

            # Update birds
            self.update()
            # Draw board and birds
            self.draw()

            # Draw control panel
            pygame.draw.rect(variables.screen, (200, 200, 200), panel_rect)  # Gray panel

            # Draw sliders
            for slider in sliders:
                slider.draw(variables.screen)
            # Draw checkbox
            checkbox.draw(variables.screen)

            # Update global parameters from sliders
            variables.inertia = sliders[0].val
            variables.collision_zone_radius = sliders[1].val
            variables.interaction_zone_radius = sliders[2].val
            variables.shift_to_buddy = sliders[3].val  # Update shift_to_buddy
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
        variables.screen.fill((0, 0, 0))
        # Draw solid borders
        pygame.draw.rect(variables.screen, (255, 255, 255), (variables.BORDER_THICKNESS, variables.BORDER_THICKNESS,
                                                             self.screen_width - variables.panel_width - 2 * variables.BORDER_THICKNESS,
                                                             self.screen_height - 2 * variables.BORDER_THICKNESS),
                         2)  # White border with thickness of 2

        # Draw all restricted areas
        for rect in variables.restricted_areas:
            rect_x, rect_y, rect_width, rect_height = rect
            pygame.draw.rect(variables.screen, (14, 12, 13),
                             (rect_x, rect_y, rect_width, rect_height))  # Red restricted area

        for bird_index, bird in enumerate(self.birds):
            bird.draw(bird_index)


if __name__ == "__main__":
    game = Game()
    game.run()
