import math

import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Fly Simulation")

# Control Panel
panel_width = 200
panel_height = screen_height
panel_x = screen_width - panel_width
panel_rect = pygame.Rect(panel_x, 0, panel_width, panel_height)

# Parameters (initial values)
inertia = 0.95
speed_reduction_factor = 1
sensible_zone_radius = 15
interaction_zone_radius = 30
shift_to_buddy = 0.7  # Adjust this value to control the shift strength


# Slider class
class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, label):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.label = label

        self.slider_x = self.x + int((self.val - self.min_val) / (self.max_val - self.min_val) * self.width)
        self.slider_rect = pygame.Rect(self.slider_x - 5, self.y, 10, self.height) # Small slider rectangle

    def draw(self, screen):
        pygame.draw.rect(screen, (150, 150, 150), (self.x, self.y, self.width, self.height)) # Slider bar
        pygame.draw.rect(screen, (0, 0, 0), self.slider_rect) # Slider handle

        font = pygame.font.Font(None, 20)
        label_text = font.render(f"{self.label}: {self.val:.2f}", True, (0, 0, 0))
        screen.blit(label_text, (self.x, self.y - 25)) # Label above the slider


    def update(self, mouse_pos):
        if self.slider_rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]: # Dragging
            self.slider_x = max(self.x, min(mouse_pos[0], self.x + self.width))
            self.slider_rect.x = self.slider_x - 5
            self.val = self.min_val + (self.slider_x - self.x) / self.width * (self.max_val - self.min_val)


# Create sliders
sliders = [
    Slider(panel_x + 20, 50, panel_width - 40, 20, 0.1, 1.0, inertia, "Inertia"),
    Slider(panel_x + 20, 100, panel_width - 40, 20, 0.01, 1.0, speed_reduction_factor, "Speed Reduction"),
    Slider(panel_x + 20, 150, panel_width - 40, 20, 1, 30, sensible_zone_radius, "Sensible Radius"),
    Slider(panel_x + 20, 200, panel_width - 40, 20, 1, 100, interaction_zone_radius, "Interaction Radius"),
    Slider(panel_x + 20, 250, panel_width - 40, 20, 0.0, 2.0, shift_to_buddy, "Shift to Buddy"),
]


class Game:
    def __init__(self, num_flies=40):
        self.num_flies = num_flies
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.flies = []
        pygame.init()
        pygame.display.set_caption("Fly Simulation")
        self.create_flies()

    def create_flies(self):
        for _ in range(self.num_flies):
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            # Reduced initial speed
            dx = random.uniform(-1, 1)  # Reduced range
            dy = random.uniform(-1, 1)  # Reduced range
            self.flies.append(Fly(x, y, dx, dy))  # Pass dx and dy to Fly constructor

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
                        for slider in sliders:
                            slider.update(mouse_pos)

            #update flies
            self.update()
            # draw board and flies
            self.draw()

            # Draw control panel
            pygame.draw.rect(screen, (200, 200, 200), panel_rect)  # Gray panel


            # Draw sliders
            for slider in sliders:
                slider.draw(screen)

            # Update global parameters from sliders
            global inertia, speed_reduction_factor, sensible_zone_radius, interaction_zone_radius,shift_to_buddy
            inertia = sliders[0].val
            speed_reduction_factor = sliders[1].val
            sensible_zone_radius = sliders[2].val
            interaction_zone_radius = sliders[3].val
            shift_to_buddy = sliders[4].val  # Update shift_to_buddy

            pygame.display.flip()

        pygame.quit()

    def update(self):
        for fly in self.flies:
            fly.update()

    def draw(self):
        screen.fill((0, 0, 0))
        for fly in self.flies:
            fly.draw()
       # pygame.display.flip()


class Fly:

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

        # Draw sensible zone
        self.draw_sensible_zone()
        # Draw interaction zone
        self.draw_interaction_zone()

    def draw_sensible_zone(self):
        angle = math.atan2(self.dy, self.dx)  # Angle of movement
        points = []
        arc_angle = math.radians(100)  # 100 degrees in radians
        pp = 21  # Number of points

        for i in range(pp):
            current_angle = angle - arc_angle / 2 + i * arc_angle / (pp - 1)  # Distribute points over the arc
            x = self.x + sensible_zone_radius * math.cos(current_angle)
            y = self.y + sensible_zone_radius * math.sin(current_angle)
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

    def is_colliding(self, other_fly):
        distance = math.hypot(self.x - other_fly.x, self.y - other_fly.y)
        if distance > sensible_zone_radius:  # Outside sensible zone radius
            return False

        angle_to_other = math.atan2(other_fly.y - self.y, other_fly.x - self.x)
        angle_of_movement = math.atan2(self.dy, self.dx)
        angle_diff = (angle_to_other - angle_of_movement) % (2 * math.pi)  # Ensure positive angle

        # Check if within 100-degree frontal cone (50 degrees on each side)
        return angle_diff < math.radians(100) / 2 or angle_diff > 2 * math.pi - math.radians(100) / 2

    def is_in_interaction_zone(self, other_fly):
        distance = math.hypot(self.x - other_fly.x, self.y - other_fly.y)
        if distance > interaction_zone_radius:  # Outside interaction zone radius
            return False

        angle_to_other = math.atan2(other_fly.y - self.y, other_fly.x - self.x)
        angle_of_movement = math.atan2(self.dy, self.dx)
        angle_diff = (angle_to_other - angle_of_movement) % (2 * math.pi)  # Ensure positive angle

        # Check if within 100-degree frontal cone (50 degrees on each side)
        return angle_diff < math.radians(100) / 2 or angle_diff > 2 * math.pi - math.radians(100) / 2


    def avoid_collision(self, other_fly):
        angle_to_other = math.atan2(other_fly.y - self.y, other_fly.x - self.x)

        # Steer away more directly
        self.dx -= 0.2 * math.cos(angle_to_other)
        self.dy -= 0.2 * math.sin(angle_to_other)

    def align_direction(self, other_fly):


        # Align direction with the other fly
        angle_of_other_movement = math.atan2(other_fly.dy, other_fly.dx)
        speed_adjustment = 0.5
        self.dx = speed_adjustment * math.cos(angle_of_other_movement)  # Adjust speed to match
        self.dy = speed_adjustment * math.sin(angle_of_other_movement)

        # Shift towards the other fly
        dx_to_other = other_fly.x - self.x
        dy_to_other = other_fly.y - self.y
        distance_to_other = math.hypot(dx_to_other, dy_to_other)

        if distance_to_other > 0:  # Avoid division by zero if flies are at the same position
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


        # Collision detection with other flies and avoidance
        for other_fly in game.flies:
            if other_fly != self:
                if self.is_colliding(other_fly):  # Sensible zone
                    self.avoid_collision(other_fly)
                elif self.is_in_interaction_zone(other_fly):  # Interaction zone
                    self.align_direction(other_fly)

        # Inertia
        self.dx = inertia * self.last_dx + (1 - inertia) * self.dx
        self.dy = inertia * self.last_dy + (1 - inertia) * self.dy


        # Border collision avoidance (like with other flies)
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
