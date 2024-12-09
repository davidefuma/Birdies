import numpy as np
import pygame
import random
import variables
from Checkbox import Checkbox
from Slider import Slider
from Button import Button
from predator import Predator
from prey import Prey
from PopulationChart import PopulationChart

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
    def __init__(self, num_birds=40, predator_ratio=0.3):
        self.num_birds = num_birds
        self.predator_ratio = predator_ratio
        self.screen_width = variables.screen_width
        self.screen_height = variables.screen_height
        self.birds = []
        pygame.init()
        pygame.display.set_caption("Predator-Prey Simulation")

        self.create_birds()
        self.create_ui_elements()
        chart_x = self.screen_width - variables.panel_width - 220  # 200 width + 20 margin
        chart_y = self.screen_height - 220  # 200 height + 20 margin
        self.population_chart = PopulationChart(chart_x, chart_y)

        # Initialize particle system
        self.particles = []

        # Load wall texture for restricted areas
        self.wall_texture = pygame.image.load('static/wall.jpg')

        # Initialize background surface for efficient updates
        self.background_surface = pygame.Surface((self.screen_width, self.screen_height))
        self.background_surface.fill(variables.get_current_theme()['background'])
        self.draw_static_elements()

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

    def create_ui_elements(self):
        self.show_zones_checkbox = Checkbox(panel_x + 20, 300, 20, variables.show_zones, "Show Zones")
        self.theme_button = Button(panel_x + 20, 350, 160, 30, "Toggle Dark/Light Mode")
        self.sliders = [
            Slider(panel_x + 20, 50, variables.panel_width - 40, 20, 0.0, 1.0, variables.inertia, "Inertia"),
            Slider(panel_x + 20, 100, variables.panel_width - 40, 20, 1, 100, variables.collision_zone_radius,
                   "Collision Radius"),
            Slider(panel_x + 20, 150, variables.panel_width - 40, 20, 1, 100, variables.interaction_zone_radius,
                   "Interaction Radius"),
            Slider(panel_x + 20, 200, variables.panel_width - 40, 20, 0.0, 2.0, variables.shift_to_buddy, "Shift to Buddy"),
        ]

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
                        self.show_zones_checkbox.update(mouse_pos)
                        if self.theme_button.update(mouse_pos):
                            # Update background surface when theme changes
                            self.background_surface.fill(variables.get_current_theme()['background'])
                            self.draw_static_elements()
                        for slider in self.sliders:
                            slider.update(mouse_pos)

            # Update birds
            self.update()
            # Draw board and birds
            self.draw()

            # Draw control panel
            theme = variables.get_current_theme()
            pygame.draw.rect(variables.screen, theme['panel'], panel_rect)

            # Draw sliders
            for slider in self.sliders:
                slider.draw(variables.screen)
            # Draw checkbox
            self.show_zones_checkbox.draw(variables.screen)
            # Draw theme button
            self.theme_button.draw(variables.screen)

            # Update global parameters from sliders
            variables.inertia = self.sliders[0].val
            variables.collision_zone_radius = self.sliders[1].val
            variables.interaction_zone_radius = self.sliders[2].val
            variables.shift_to_buddy = self.sliders[3].val
            variables.show_zones = self.show_zones_checkbox.state

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

        # Update population statistics
        num_predators = sum(1 for bird in self.birds if isinstance(bird, Predator) and not bird.is_dead)
        num_prey = sum(1 for bird in self.birds if isinstance(bird, Prey) and not bird.is_dead)
        self.population_chart.update(num_predators, num_prey)

        # Update particles
        self.update_particles()

    def draw(self):
        # Blit the background surface instead of filling the screen each frame
        variables.screen.blit(self.background_surface, (0, 0))
        
        for bird_index, bird in enumerate(self.birds):
            bird.draw(bird_index, variables.screen)

        # Draw UI panel background
        pygame.draw.rect(variables.screen, variables.get_current_theme()['panel'],
                        (self.screen_width - variables.panel_width, 0,
                         variables.panel_width, self.screen_height))

        # Draw UI elements
        for slider in self.sliders:
            slider.draw(variables.screen)
        self.show_zones_checkbox.draw(variables.screen)
        self.theme_button.draw(variables.screen)

        # Draw population chart
        self.population_chart.draw(variables.screen)

        # Draw particles
        self.draw_particles()

    def draw_static_elements(self):
        # Draw wall texture for areas outside the main border
        outside_border_rects = [
            # Left side outside border
            (0, 0, variables.BORDER_THICKNESS, self.screen_height),
            # Right side outside border (accounting for panel)
            (self.screen_width - variables.panel_width, 0, variables.BORDER_THICKNESS, self.screen_height),
            # Top outside border
            (0, 0, self.screen_width, variables.BORDER_THICKNESS),
            # Bottom outside border
            (0, self.screen_height - variables.BORDER_THICKNESS, self.screen_width, variables.BORDER_THICKNESS)
        ]

        for rect_x, rect_y, rect_width, rect_height in outside_border_rects:
            area_texture = pygame.transform.scale(self.wall_texture, (rect_width, rect_height))
            self.background_surface.blit(area_texture, (rect_x, rect_y))

        # Draw solid borders on the background surface
        pygame.draw.rect(self.background_surface, variables.get_current_theme()['border'],
                         (variables.BORDER_THICKNESS, variables.BORDER_THICKNESS,
                          self.screen_width - variables.panel_width - 2 * variables.BORDER_THICKNESS,
                          self.screen_height - 2 * variables.BORDER_THICKNESS),
                         2)  # Border with thickness of 2

        # Draw all restricted areas with texture
        for rect in variables.restricted_areas:
            rect_x, rect_y, rect_width, rect_height = rect
            area_texture = pygame.transform.scale(self.wall_texture, (rect_width, rect_height))
            self.background_surface.blit(area_texture, (rect_x, rect_y))

    def update_particles(self):
        # Efficiently update particles
        for particle in self.particles:
            particle.update()
            if particle.is_dead():
                self.particles.remove(particle)

    def draw_particles(self):
        # Efficiently draw particles
        for particle in self.particles:
            particle.draw(variables.screen)

    def add_particle(self, position, velocity):
        # Add a new particle to the system
        self.particles.append(Particle(position, velocity))


class Particle:
    def __init__(self, position, velocity):
        self.position = position
        self.velocity = velocity
        self.lifetime = 100  # Lifetime of the particle

    def update(self):
        # Update particle position and reduce lifetime
        self.position = (self.position[0] + self.velocity[0],
                         self.position[1] + self.velocity[1])
        self.lifetime -= 1

    def is_dead(self):
        # Check if the particle is dead
        return self.lifetime <= 0

    def draw(self, screen):
        # Draw the particle on the screen
        pygame.draw.circle(screen, (255, 255, 255),
                           (int(self.position[0]), int(self.position[1])), 3)


if __name__ == "__main__":
    game = Game()
    game.run()
