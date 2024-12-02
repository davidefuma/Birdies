import math
import random

import numpy as np
import pygame

import variables


class Bird:

    def __init__(self, dx, dy, is_predator=False):
        self.is_predator = is_predator
        self.is_dead = False
        
        # Adjust speed based on species
        speed_multiplier = variables.PREDATOR_SPEED_RATIO if is_predator else 1.0
        self.dx = dx * speed_multiplier
        self.dy = dy * speed_multiplier

        # the directions at the previous step
        self.last_dx = self.dx
        self.last_dy = self.dy

    def draw(self, bird_index):

        # Get size based on species
        base_size = 5
        size = base_size * (variables.PREDATOR_SIZE_RATIO if self.is_predator else 1.0)
        
        # Get color based on species and state
        if self.is_dead:
            color = variables.get_current_theme()['dead_prey']
        else:
            color = variables.get_current_theme()['predator'] if self.is_predator else variables.get_current_theme()['prey']

        # Draw triangle
        angle = math.atan2(self.dy, self.dx)
        points = [
            (variables.X[bird_index] + size * math.cos(angle), 
             variables.Y[bird_index] + size * math.sin(angle)),  # Tip
            (variables.X[bird_index] + size * math.cos(angle + 2 * math.pi / 5),
             variables.Y[bird_index] + size * math.sin(angle + 2 * math.pi / 5)),
            (variables.X[bird_index] + size * math.cos(angle - 2 * math.pi / 5),
             variables.Y[bird_index] + size * math.sin(angle - 2 * math.pi / 5)),
        ]
        pygame.draw.polygon(variables.screen, color, points)

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

        pygame.draw.lines(variables.screen, variables.get_current_theme()['border'], False, points, 1)

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

        pygame.draw.lines(variables.screen, variables.get_current_theme()['border'], False, points, 1)  # Green lines

    def is_colliding(self, bird_index, other_bird_index, distance):
        if self.is_dead:  # Dead birds don't collide
            return False

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

    def update(self, bird_index, all_birds, distances, this_step_interactions):
        # If dead, don't move
        if self.is_dead:
            self.dx = 0
            self.dy = 0
            return

        # Adjust speed with fixed values
        speed_adjustment = random.gauss(0, 0.35)  # 0.35 ìs standard deviation
        self.dx += speed_adjustment
        self.dy += speed_adjustment

        # calculate distances between all the couples of birds
        disx = variables.X[:, np.newaxis] - variables.X  # Calculate x-differences for all pairs
        disy = variables.Y[:, np.newaxis] - variables.Y  # Calculate y-differences for all pairs
        distances = np.hypot(disx, disy)  # Calculate distances for all pairs

        # Collision detection with other birds and avoidance
        j = 0

        for other_bird in all_birds:
            if other_bird != self:
                distance = distances[bird_index, j]
                if self.is_colliding(bird_index, j, distance):  # collision zone
                    self.avoid_collision(bird_index, j)

                # if the bird_index has already had an interaction with bird j this step, avoid the reciprocal interaction
                else:
                    if j not in this_step_interactions or bird_index not in this_step_interactions[j]:
                        if self.is_in_interaction_zone(bird_index, j, distance):  # Interaction zone
                            self.align_direction(bird_index, j, other_bird, distance)
                            this_step_interactions[bird_index][j] = True
                    else:
                        # print('bird already had reciprocal interaction')
                        pass
            j += 1

        # Check for predator-prey collision
        j = 0
        for other_bird in all_birds:
            if other_bird != self:
                distance = distances[bird_index, j]
                self.check_predator_prey_collision(bird_index, j, other_bird, distance)
            j += 1

        # Inertia
        self.dx = variables.inertia * self.last_dx + (1 - variables.inertia) * self.dx
        self.dy = variables.inertia * self.last_dy + (1 - variables.inertia) * self.dy

        # Border collision avoidance with improved logic
        avoidance_radius = variables.collision_zone_radius * 2  # Same detection radius as restricted areas
        speed = np.hypot(self.dx, self.dy)
        speed_multiplier = max(1.0, speed)
        
        # Left border
        distance_to_left = variables.X[bird_index] - variables.BORDER_THICKNESS
        if distance_to_left < avoidance_radius:
            base_force = 1.0 if distance_to_left <= 0 else (1 - distance_to_left/avoidance_radius) * 0.5
            force = base_force * speed_multiplier
            self.dx += force  # Push right
            
        # Right border (accounting for panel)
        distance_to_right = (variables.screen_width - variables.panel_width - variables.BORDER_THICKNESS) - variables.X[bird_index]
        if distance_to_right < avoidance_radius:
            base_force = 1.0 if distance_to_right <= 0 else (1 - distance_to_right/avoidance_radius) * 0.5
            force = base_force * speed_multiplier
            self.dx -= force  # Push left
            
        # Top border
        distance_to_top = variables.Y[bird_index] - variables.BORDER_THICKNESS
        if distance_to_top < avoidance_radius:
            base_force = 1.0 if distance_to_top <= 0 else (1 - distance_to_top/avoidance_radius) * 0.5
            force = base_force * speed_multiplier
            self.dy += force  # Push down
            
        # Bottom border
        distance_to_bottom = variables.screen_height - variables.BORDER_THICKNESS - variables.Y[bird_index]
        if distance_to_bottom < avoidance_radius:
            base_force = 1.0 if distance_to_bottom <= 0 else (1 - distance_to_bottom/avoidance_radius) * 0.5
            force = base_force * speed_multiplier
            self.dy -= force  # Push up

        # Avoid restricted areas based on collision zone radius
        for rect in variables.restricted_areas:
            rect_x, rect_y, rect_width, rect_height = rect

            # Calculate if bird is inside the restricted area
            is_inside = (rect_x < variables.X[bird_index] < rect_x + rect_width and
                         rect_y < variables.Y[bird_index] < rect_y + rect_height)

            # Calculate the closest point on the rectangle to the bird
            closest_x = max(rect_x, min(variables.X[bird_index], rect_x + rect_width))
            closest_y = max(rect_y, min(variables.Y[bird_index], rect_y + rect_height))

            # Calculate the distance and direction from the bird to the closest point
            dx_to_rect = closest_x - variables.X[bird_index]
            dy_to_rect = closest_y - variables.Y[bird_index]
            distance_to_rect = np.hypot(dx_to_rect, dy_to_rect)

            # Calculate avoidance force based on distance
            avoidance_radius = variables.collision_zone_radius * 2  # Increase detection radius
            if distance_to_rect < avoidance_radius or is_inside:
                # Calculate base force (stronger when closer)
                base_force = 1.0 if is_inside else (1 - distance_to_rect / avoidance_radius) * 0.5

                # Calculate speed-based multiplier (faster birds need stronger avoidance)
                speed = np.hypot(self.dx, self.dy)
                speed_multiplier = max(1.0, speed)

                # Apply force in opposite direction of the restricted area
                if distance_to_rect > 0:  # Avoid division by zero
                    force = base_force * speed_multiplier
                    self.dx -= force * dx_to_rect / distance_to_rect
                    self.dy -= force * dy_to_rect / distance_to_rect
                else:
                    # If exactly on the border, apply random force
                    angle = random.uniform(0, 2 * math.pi)
                    force = base_force * speed_multiplier
                    self.dx += force * math.cos(angle)
                    self.dy += force * math.sin(angle)

        # update the directions
        self.last_dx = self.dx
        self.last_dy = self.dy
        # Update position using X and Y vectors. X and Y are vectors of integers. dx and dy are float, so we must
        # round them
        variables.X[bird_index] += np.round(self.dx)
        variables.Y[bird_index] += np.round(self.dy)

    def check_predator_prey_collision(self, bird_index, other_bird_index, other_bird, distance):
        if distance > variables.collision_zone_radius:
            return False
            
        # Only check collision if one is predator and other is prey (and prey is alive)
        if self.is_predator and not other_bird.is_predator and not other_bird.is_dead:
            angle_to_other = math.atan2(variables.Y[other_bird_index] - variables.Y[bird_index],
                                      variables.X[other_bird_index] - variables.X[bird_index])
            angle_of_movement = math.atan2(self.dy, self.dx)
            angle_diff = (angle_to_other - angle_of_movement) % (2 * math.pi)  # Ensure positive angle
            
            # Check if prey is within predator's frontal cone (same as collision detection)
            if angle_diff < math.radians(100) / 2 or angle_diff > 2 * math.pi - math.radians(100) / 2:
                other_bird.is_dead = True
                return True
        return False
