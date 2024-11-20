import math

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
inertia = 0.95
speed_reduction_factor = 1
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
    def __init__(self, num_birds=40):
        self.num_birds = num_birds
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.birds = []
        pygame.init()
        pygame.display.set_caption("Birds Simulation")
        self.create_birds()

    def create_birds(self):
        for _ in range(self.num_birds):
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            # Reduced initial speed
            dx = random.uniform(-1, 1)  # Reduced range
            dy = random.uniform(-1, 1)  # Reduced range
            self.birds.append(Bird(x, y, dx, dy))  # Pass dx and dy to bird constructor

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
            global inertia, speed_reduction_factor, collision_zone_radius, interaction_zone_radius,shift_to_buddy, show_zones
            inertia = sliders[0].val
            speed_reduction_factor = sliders[1].val
            collision_zone_radius = sliders[2].val
            interaction_zone_radius = sliders[3].val
            shift_to_buddy = sliders[4].val  # Update shift_to_buddy
            show_zones = checkbox.state

            pygame.display.flip()

        pygame.quit()

    def update(self):
        for bird in self.birds:
            bird.update()

    def draw(self):
        screen.fill((0, 0, 0))
        for bird in self.birds:
            bird.draw()
       # pygame.display.flip()


class Bird:

    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy

        # the directions at the previous step
        self.last_dx = dx
        self.last_dy = dy

    def draw(self):

        # Draw triangle
        angle = math.atan2(self.dy, self.dx)
        size = 5  # Size of the triangle
        points = [
            (self.x + size * math.cos(angle), self.y + size * math.sin(angle)),  # Tip
            (self.x + size * math.cos(angle + 2 * math.pi / 5), self.y + size * math.sin(angle + 2 * math.pi / 5)),
            (self.x + size * math.cos(angle - 2 * math.pi / 5), self.y + size * math.sin(angle - 2 * math.pi / 5)),
        ]
        pygame.draw.polygon(screen, (255, 145, 145), points)

        if show_zones:  # Only draw zones if checkbox is checked
            # Draw collision zone
            self.draw_collision_zone()
            # Draw interaction zone
            self.draw_interaction_zone()

    def draw_collision_zone(self):
        angle = math.atan2(self.dy, self.dx)  # Angle of movement
        points = []
        arc_angle = math.radians(100)  # 100 degrees in radians
        pp = 21  # Number of points

        for i in range(pp):
            current_angle = angle - arc_angle / 2 + i * arc_angle / (pp - 1)  # Distribute points over the arc
            x = self.x + collision_zone_radius * math.cos(current_angle)
            y = self.y + collision_zone_radius * math.sin(current_angle)
            points.append((x, y))

        pygame.draw.lines(screen, (145, 0, 0), False, points, 1)
    def draw_interaction_zone(self):
        angle = math.atan2(self.dy, self.dx)
        points = []
        arc_angle = math.radians(100)  # 100 degrees in radians
        pp = 21

        for i in range(pp):
            current_angle = angle - arc_angle / 2 + i * arc_angle / (pp - 1)
            x = self.x + interaction_zone_radius * math.cos(current_angle)
            y = self.y + interaction_zone_radius * math.sin(current_angle)
            points.append((x, y))

        pygame.draw.lines(screen, (0, 145, 0), False, points, 1)  # Green lines

    def is_colliding(self, other_bird):
        distance = math.hypot(self.x - other_bird.x, self.y - other_bird.y)
        if distance > collision_zone_radius:  # Outside collision zone radius
            return False

        angle_to_other = math.atan2(other_bird.y - self.y, other_bird.x - self.x)
        angle_of_movement = math.atan2(self.dy, self.dx)
        angle_diff = (angle_to_other - angle_of_movement) % (2 * math.pi)  # Ensure positive angle

        # Check if within 100-degree frontal cone (50 degrees on each side)
        return angle_diff < math.radians(100) / 2 or angle_diff > 2 * math.pi - math.radians(100) / 2

    def is_in_interaction_zone(self, other_bird):
        distance = math.hypot(self.x - other_bird.x, self.y - other_bird.y)
        if distance > interaction_zone_radius:  # Outside interaction zone radius
            return False

        angle_to_other = math.atan2(other_bird.y - self.y, other_bird.x - self.x)
        angle_of_movement = math.atan2(self.dy, self.dx)
        angle_diff = (angle_to_other - angle_of_movement) % (2 * math.pi)  # Ensure positive angle

        # Check if within 100-degree frontal cone (50 degrees on each side)
        return angle_diff < math.radians(100) / 2 or angle_diff > 2 * math.pi - math.radians(100) / 2


    def avoid_collision(self, other_bird):
        angle_to_other = math.atan2(other_bird.y - self.y, other_bird.x - self.x)

        # Steer away more directly
        self.dx -= 0.2 * math.cos(angle_to_other)
        self.dy -= 0.2 * math.sin(angle_to_other)

    def align_direction(self, other_bird):


        # Align direction with the other bird
        angle_of_other_movement = math.atan2(other_bird.dy, other_bird.dx)
        speed_adjustment = 0.5
        self.dx = speed_adjustment * math.cos(angle_of_other_movement)  # Adjust speed to match
        self.dy = speed_adjustment * math.sin(angle_of_other_movement)

        # Shift towards the other bird
        dx_to_other = other_bird.x - self.x
        dy_to_other = other_bird.y - self.y
        distance_to_other = math.hypot(dx_to_other, dy_to_other)

        if distance_to_other > 0:  # Avoid division by zero if birds are at the same position
            self.dx += shift_to_buddy * dx_to_other / distance_to_other
            self.dy += shift_to_buddy * dy_to_other / distance_to_other

    def update(self):
        # Adjust speed with fixed values
        speed_adjustment = random.gauss(0, 0.35)  # 0.35 ìs standard deviation
        self.dx += speed_adjustment
        self.dy += speed_adjustment
        # Further random adjustment
        self.dx += random.uniform(-0.1, 0.1)
        self.dy += random.uniform(-0.1, 0.1)


        # Collision detection with other birds and avoidance
        for other_bird in game.birds:
            if other_bird != self:
                if self.is_colliding(other_bird):  # collision zone
                    self.avoid_collision(other_bird)
                elif self.is_in_interaction_zone(other_bird):  # Interaction zone
                    self.align_direction(other_bird)

        # Inertia
        self.dx = inertia * self.last_dx + (1 - inertia) * self.dx
        self.dy = inertia * self.last_dy + (1 - inertia) * self.dy


        # Border collision avoidance (like with other birds)
        border = 16  # Border width
        # consider also panel width. this works only if panel is on the right of the board
        if self.x < border:
            self.dx += 0.2  # Steer away from left border
        if self.x > game.screen_width - border - panel_width:
            self.dx -= 0.2  # Steer away from right border
        if self.y < border:
            self.dy += 0.2  # Steer away from top border
        if self.y > game.screen_height - border:
            self.dy -= 0.2  # Steer away from bottom border

        # Reduce speed by a const factor to optimize the view
        self.dx *= speed_reduction_factor
        self.dy *= speed_reduction_factor


        #update the directions
        self.last_dx = self.dx
        self.last_dy = self.dy
        self.x += self.dx
        self.y += self.dy




if __name__ == "__main__":
    game = Game()
    game.run()
