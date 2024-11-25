import math
import numpy as np
import pygame
import random

from Checkbox import Checkbox
from Slider import Slider

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Birds Simulation")

# Control Panel
panel_width = 200
panel_height = screen_height
panel_x = screen_width - panel_width
panel_rect = pygame.Rect(panel_x, 0, panel_width, panel_height)

# Parameters (initial values)
inertia = 0.75
speed_reduction_factor = 0.99
collision_zone_radius = 15
interaction_zone_radius = 30
shift_to_buddy = 0.7  # Adjust this value to control the shift strength
show_zones = True  # Initially show the zones

# Create checkbox
checkbox = Checkbox(panel_x + 20, 300, 20, show_zones, "Show Zones")

# Create sliders
sliders = [
    Slider(panel_x + 20, 50, panel_width - 40, 20, 0.1, 1.0, inertia, "Inertia"),
    Slider(panel_x + 20, 100, panel_width - 40, 20, 0.01, 1.0, speed_reduction_factor, "Speed Reduction"),
    Slider(panel_x + 20, 150, panel_width - 40, 20, 1, 100, collision_zone_radius, "Collision Radius"),
    Slider(panel_x + 20, 200, panel_width - 40, 20, 1, 100, interaction_zone_radius, "Interaction Radius"),
    Slider(panel_x + 20, 250, panel_width - 40, 20, 0.0, 2.0, shift_to_buddy, "Shift to Buddy"),
]


class Game:
    def __init__(self, num_birds=17):
        self.num_birds = num_birds
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.birds = []
        pygame.init()
        pygame.display.set_caption("Birds Simulation")
        self.X = []  # Vector to store x-coordinates of birds
        self.Y = []  # Vector to store y-coordinates of birds
        self.create_birds()

    def create_birds(self):
        for _ in range(self.num_birds):
            x = random.randint(0, self.screen_width -  panel_width)
            y = random.randint(0, self.screen_height)
            dx = random.uniform(-1, 1)
            dy = random.uniform(-1, 1)
            self.birds.append(Bird(dx, dy))  # No longer passing x, y to Bird
            self.X.append(x)  # Store x-coordinate in the vector
            self.Y.append(y)  # Store y-coordinate in the vector
        self.X = np.array(self.X)
        self.Y = np.array(self.Y)

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

            #update birds
            self.update()
            # draw board and birds
            self.draw()

            # Draw control panel
            pygame.draw.rect(screen, (200, 200, 200), panel_rect)  # Gray panel

            # Draw sliders
            for slider in sliders:
                slider.draw(screen)
            # Draw checkbox
            checkbox.draw(screen)

            # Update global parameters from sliders
            global inertia, speed_reduction_factor, collision_zone_radius, interaction_zone_radius, shift_to_buddy, show_zones
            inertia = sliders[0].val
            speed_reduction_factor = sliders[1].val
            collision_zone_radius = sliders[2].val
            interaction_zone_radius = sliders[3].val
            shift_to_buddy = sliders[4].val  # Update shift_to_buddy
            show_zones = checkbox.state

            pygame.display.flip()

        pygame.quit()

    def update(self):
        for bird_index, bird in enumerate(self.birds):  # Iterate using index
            bird.update(bird_index)  # Pass the bird's index

    def draw(self):
        screen.fill((0, 0, 0))
        for bird_index, bird in enumerate(self.birds):
            bird.draw(bird_index)
    # pygame.display.flip()


class Bird:

    def __init__(self, dx, dy):
        self.dx = dx
        self.dy = dy

        # the directions at the previous step
        self.last_dx = dx
        self.last_dy = dy

    def draw(self, bird_index):

        # Draw triangle
        angle = math.atan2(self.dy, self.dx)
        size = 5  # Size of the triangle
        points = [
            (game.X[bird_index] + size * math.cos(angle), game.Y[bird_index] + size * math.sin(angle)),  # Tip
            (
                game.X[bird_index] + size * math.cos(angle + 2 * math.pi / 5), game.Y[bird_index] + size * math.sin(angle + 2 * math.pi / 5)),
            (
                game.X[bird_index] + size * math.cos(angle - 2 * math.pi / 5), game.Y[bird_index] + size * math.sin(angle - 2 * math.pi / 5)),
        ]
        pygame.draw.polygon(screen, (255, 145, 145), points)

        if show_zones:  # Only draw zones if checkbox is checked
            # Draw collision zone
            self.draw_collision_zone(bird_index)
            # Draw interaction zone
            self.draw_interaction_zone(bird_index)

    def draw_collision_zone(self, bird_index):
        angle = math.atan2(self.dy, self.dx)  # Angle of movement
        points = []
        arc_angle = math.radians(100)  # 100 degrees in radians
        pp = 21  # Number of points

        for ii in range(pp):
            current_angle = angle - arc_angle / 2 + ii * arc_angle / (pp - 1)  # Distribute points over the arc
            x = game.X[bird_index] + collision_zone_radius * math.cos(current_angle)
            y = game.Y[bird_index] + collision_zone_radius * math.sin(current_angle)
            points.append((x, y))

        pygame.draw.lines(screen, (145, 0, 0), False, points, 1)

    def draw_interaction_zone(self, bird_index):
        angle = math.atan2(self.dy, self.dx)
        points = []
        arc_angle = math.radians(100)  # 100 degrees in radians
        pp = 21

        for ii in range(pp):
            current_angle = angle - arc_angle / 2 + ii * arc_angle / (pp - 1)
            x = game.X[bird_index] + interaction_zone_radius * math.cos(current_angle)
            y = game.Y[bird_index] + interaction_zone_radius * math.sin(current_angle)
            points.append((x, y))

        pygame.draw.lines(screen, (0, 145, 0), False, points, 1)  # Green lines

    def is_colliding(self, bird_index, other_bird_index, distance):

        if distance > collision_zone_radius:  # Outside collision zone radius
            return False

        angle_to_other = math.atan2(game.Y[other_bird_index] - game.Y[bird_index], game.X[other_bird_index] - game.X[bird_index])
        angle_of_movement = math.atan2(self.dy, self.dx)
        angle_diff = (angle_to_other - angle_of_movement) % (2 * math.pi)  # Ensure positive angle

        # Check if within 100-degree frontal cone (50 degrees on each side)
        return angle_diff < math.radians(100) / 2 or angle_diff > 2 * math.pi - math.radians(100) / 2

    def is_in_interaction_zone(self, bird_index, other_bird_index, distance):
        if distance > interaction_zone_radius:  # Outside interaction zone radius
            return False

        angle_to_other = math.atan2(game.Y[other_bird_index] - game.Y[bird_index], game.X[other_bird_index] - game.X[bird_index])
        angle_of_movement = math.atan2(self.dy, self.dx)
        angle_diff = (angle_to_other - angle_of_movement) % (2 * math.pi)  # Ensure positive angle

        # Check if within 100-degree frontal cone (50 degrees on each side)
        return angle_diff < math.radians(100) / 2 or angle_diff > 2 * math.pi - math.radians(100) / 2

    def avoid_collision(self, bird_index, other_bird_index):
        angle_to_other = math.atan2(game.Y[other_bird_index] - game.Y[bird_index], game.X[other_bird_index] - game.X[bird_index])

        # Steer away more directly
        self.dx -= 0.2 * math.cos(angle_to_other)
        self.dy -= 0.2 * math.sin(angle_to_other)

    def align_direction(self, bird_index, other_bird_index, other_bird, distance):

        # Align direction with the other bird
        angle_of_other_movement = math.atan2(other_bird.dy, other_bird.dx)
        speed_adjustment = 0.5
        self.dx = speed_adjustment * math.cos(angle_of_other_movement)  # Adjust speed to match
        self.dy = speed_adjustment * math.sin(angle_of_other_movement)

        # Shift towards the other bird
        dx_to_other = game.X[other_bird_index] - game.X[bird_index]
        dy_to_other = game.Y[other_bird_index] - game.Y[bird_index]

        if distance > 0:  # Avoid division by zero if birds are at the same position
            self.dx += shift_to_buddy * dx_to_other / distance
            self.dy += shift_to_buddy * dy_to_other / distance

    def update(self, bird_index):
        # Adjust speed with fixed values
        speed_adjustment = random.gauss(0, 0.35)  # 0.35 ìs standard deviation
        self.dx += speed_adjustment
        self.dy += speed_adjustment
        # Further random adjustment
        self.dx += random.uniform(-0.1, 0.1)
        self.dy += random.uniform(-0.1, 0.1)

        #calculate distances between all the couples of birds
        disx = game.X[:, np.newaxis] - game.X  # Calculate x-differences for all pairs
        disy = game.Y[:, np.newaxis] - game.Y  # Calculate y-differences for all pairs
        distances = np.hypot(disx, disy)  # Calculate distances for all pairs

        # Collision detection with other birds and avoidance
        j = 0
        for other_bird in game.birds:
            if other_bird != self:
                distance = distances[bird_index, j]
                #distance = math.hypot(game.X[bird_index] - game.X[j], game.Y[bird_index] - game.Y[j])
                if self.is_colliding(bird_index, j, distance):  # collision zone
                    self.avoid_collision(bird_index, j)
                elif self.is_in_interaction_zone(bird_index, j, distance):  # Interaction zone
                    self.align_direction(bird_index, j, other_bird, distance)
            j += 1

        # Inertia
        self.dx = inertia * self.last_dx + (1 - inertia) * self.dx
        self.dy = inertia * self.last_dy + (1 - inertia) * self.dy

        # Border collision avoidance (like with other birds)
        border = 16  # Border width
        # consider also panel width. this works only if panel is on the right of the board
        if game.X[bird_index] < border:
            self.dx += 0.2  # Steer away from left border
        if game.X[bird_index] > game.screen_width - border - panel_width:
            self.dx -= 0.2  # Steer away from right border
        if game.Y[bird_index] < border:
            self.dy += 0.2  # Steer away from top border
        if game.Y[bird_index] > game.screen_height - border:
            self.dy -= 0.2  # Steer away from bottom border

        # Reduce speed by a const factor to optimize the view
        self.dx *= speed_reduction_factor
        self.dy *= speed_reduction_factor

        #update the directions
        self.last_dx = self.dx
        self.last_dy = self.dy
        # Update position using X and Y vectors. X and Y are vectors of integers. dx and dy are float, so we must
        # round them
        game.X[bird_index] += np.round(self.dx)
        game.Y[bird_index] += np.round(self.dy)


if __name__ == "__main__":
    game = Game()
    game.run()
