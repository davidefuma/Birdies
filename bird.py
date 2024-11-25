import math
import random

import numpy as np
import pygame

import variables


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
            (variables.X[bird_index] + size * math.cos(angle), variables.Y[bird_index] + size * math.sin(angle)),  # Tip
            (
                variables.X[bird_index] + size * math.cos(angle + 2 * math.pi / 5),
                variables.Y[bird_index] + size * math.sin(angle + 2 * math.pi / 5)),
            (
                variables.X[bird_index] + size * math.cos(angle - 2 * math.pi / 5),
                variables.Y[bird_index] + size * math.sin(angle - 2 * math.pi / 5)),
        ]
        pygame.draw.polygon(variables.screen, (255, 145, 145), points)

        if variables.show_zones:  # Only draw zones if checkbox is checked
            # Draw collision zone
            self.draw_collision_zone(bird_index)
            # Draw interaction zone
            self.draw_interaction_zone(bird_index)

    def draw_collision_zone(self, bird_index):
        angle = math.atan2(self.dy, self.dx)  # Angle of movement
        points = []
        arc_angle = math.radians(100)  # 100 degrees in radians
        pp = 13  # Number of points

        for ii in range(pp):
            current_angle = angle - arc_angle / 2 + ii * arc_angle / (pp - 1)  # Distribute points over the arc
            x = variables.X[bird_index] + variables.collision_zone_radius * math.cos(current_angle)
            y = variables.Y[bird_index] + variables.collision_zone_radius * math.sin(current_angle)
            points.append((x, y))

        pygame.draw.lines(variables.screen, (145, 0, 0), False, points, 1)

    def draw_interaction_zone(self, bird_index):
        angle = math.atan2(self.dy, self.dx)
        points = []
        arc_angle = math.radians(100)  # 100 degrees in radians
        pp = 13

        for ii in range(pp):
            current_angle = angle - arc_angle / 2 + ii * arc_angle / (pp - 1)
            x = variables.X[bird_index] + variables.interaction_zone_radius * math.cos(current_angle)
            y = variables.Y[bird_index] + variables.interaction_zone_radius * math.sin(current_angle)
            points.append((x, y))

        pygame.draw.lines(variables.screen, (0, 145, 0), False, points, 1)  # Green lines

    def is_colliding(self, bird_index, other_bird_index, distance):

        if distance > variables.collision_zone_radius:  # Outside collision zone radius
            return False

        angle_to_other = math.atan2(variables.Y[other_bird_index] - variables.Y[bird_index],
                                    variables.X[other_bird_index] - variables.X[bird_index])
        angle_of_movement = math.atan2(self.dy, self.dx)
        angle_diff = (angle_to_other - angle_of_movement) % (2 * math.pi)  # Ensure positive angle

        # Check if within 100-degree frontal cone (50 degrees on each side)
        return angle_diff < math.radians(100) / 2 or angle_diff > 2 * math.pi - math.radians(100) / 2

    def is_in_interaction_zone(self, bird_index, other_bird_index, distance):
        if distance > variables.interaction_zone_radius:  # Outside interaction zone radius
            return False

        angle_to_other = math.atan2(variables.Y[other_bird_index] - variables.Y[bird_index],
                                    variables.X[other_bird_index] - variables.X[bird_index])
        angle_of_movement = math.atan2(self.dy, self.dx)
        angle_diff = (angle_to_other - angle_of_movement) % (2 * math.pi)  # Ensure positive angle

        # Check if within 100-degree frontal cone (50 degrees on each side)
        return angle_diff < math.radians(100) / 2 or angle_diff > 2 * math.pi - math.radians(100) / 2

    def avoid_collision(self, bird_index, other_bird_index):
        angle_to_other = math.atan2(variables.Y[other_bird_index] - variables.Y[bird_index],
                                    variables.X[other_bird_index] - variables.X[bird_index])

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
        dx_to_other = variables.X[other_bird_index] - variables.X[bird_index]
        dy_to_other = variables.Y[other_bird_index] - variables.Y[bird_index]

        if distance > 0:  # Avoid division by zero if birds are at the same position
            self.dx += variables.shift_to_buddy * dx_to_other / distance
            self.dy += variables.shift_to_buddy * dy_to_other / distance

    def update(self, bird_index, all_birds):
        # Adjust speed with fixed values
        speed_adjustment = random.gauss(0, 0.35)  # 0.35 ìs standard deviation
        self.dx += speed_adjustment
        self.dy += speed_adjustment
        # Further random adjustment
        self.dx += random.uniform(-0.1, 0.1)
        self.dy += random.uniform(-0.1, 0.1)

        #calculate distances between all the couples of birds
        disx = variables.X[:, np.newaxis] - variables.X  # Calculate x-differences for all pairs
        disy = variables.Y[:, np.newaxis] - variables.Y  # Calculate y-differences for all pairs
        distances = np.hypot(disx, disy)  # Calculate distances for all pairs

        # Collision detection with other birds and avoidance
        j = 0
        for other_bird in all_birds:
            if other_bird != self:
                distance = distances[bird_index, j]
                #distance = math.hypot(variables.X[bird_index] - variables.X[j], variables.Y[bird_index] - variables.Y[j])
                if self.is_colliding(bird_index, j, distance):  # collision zone
                    self.avoid_collision(bird_index, j)
                elif self.is_in_interaction_zone(bird_index, j, distance):  # Interaction zone
                    self.align_direction(bird_index, j, other_bird, distance)
            j += 1

        # Inertia
        self.dx = variables.inertia * self.last_dx + (1 - variables.inertia) * self.dx
        self.dy = variables.inertia * self.last_dy + (1 - variables.inertia) * self.dy

        # Border collision avoidance (like with other birds)
        border = variables.collision_zone_radius  # Border width
        # consider also panel width. this works only if panel is on the right of the board
        if variables.X[bird_index] < border:
            self.dx += 0.2  # Steer away from left border
        if variables.X[bird_index] > variables.screen_width - border - variables.panel_width:
            self.dx -= 0.2  # Steer away from right border
        if variables.Y[bird_index] < border:
            self.dy += 0.2  # Steer away from top border
        if variables.Y[bird_index] > variables.screen_height - border:
            self.dy -= 0.2  # Steer away from bottom border

        # Reduce speed by a const factor to optimize the view
        self.dx *= variables.speed_reduction_factor
        self.dy *= variables.speed_reduction_factor

        #update the directions
        self.last_dx = self.dx
        self.last_dy = self.dy
        # Update position using X and Y vectors. X and Y are vectors of integers. dx and dy are float, so we must
        # round them
        variables.X[bird_index] += np.round(self.dx)
        variables.Y[bird_index] += np.round(self.dy)
