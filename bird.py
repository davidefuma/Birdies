import math
import random
import numpy as np
import pygame
import variables

class Bird:
    def __init__(self, dx, dy):
        self.is_dead = False
        self.dx = dx
        self.dy = dy
        self.last_dx = dx
        self.last_dy = dy
        
    def draw(self, bird_index):
        # Get size based on species
        size = self.get_size()
        color = self.get_color()

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
            self.draw_collision_zone(bird_index)
            self.draw_interaction_zone(bird_index)
            
    def get_size(self):
        """Override in subclasses to define specific sizes"""
        return 5  # Base size
        
    def get_color(self):
        """Override in subclasses to define specific colors"""
        if self.is_dead:
            return variables.get_current_theme()['dead_prey']
        return (255, 255, 255)  # Default white
        
    def can_be_killed(self):
        """Override in subclasses to define if this bird can be killed"""
        return False
        
    def can_kill(self):
        """Override in subclasses to define if this bird can kill others"""
        return False

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
        # Update energy if this bird has an energy system
        if hasattr(self, 'update_energy'):
            self.update_energy()
            
        if self.is_dead:
            self.dx = 0
            self.dy = 0
            return

        # Initialize lists for different zones
        collision_zone_birds = []
        interaction_zone_birds = []

        # Check all other birds
        for other_bird_index, (other_bird, distance) in enumerate(zip(all_birds, distances[bird_index])):
            if other_bird_index == bird_index:
                continue
                
            # Skip dead birds for both collision and interaction
            if other_bird.is_dead:
                continue

            # Check for predator-prey collision
            if self.check_predator_prey_collision(bird_index, other_bird_index, other_bird, distance):
                continue

            # Sort birds into zones (only for living birds)
            if distance < variables.collision_zone_radius:
                collision_zone_birds.append((other_bird_index, distance))
            elif distance < variables.interaction_zone_radius:
                interaction_zone_birds.append((other_bird_index, distance))

        # Apply collision avoidance (from living birds only)
        if collision_zone_birds:
            self.handle_collisions(bird_index, collision_zone_birds)

        # Apply interaction rules (with living birds only)
        if interaction_zone_birds:
            self.handle_interactions(bird_index, interaction_zone_birds, all_birds=all_birds)

        # Update position
        self.update_position(bird_index)

    def handle_collisions(self, bird_index, collision_zone_birds):
        for other_bird_index, distance in collision_zone_birds:
            self.avoid_collision(bird_index, other_bird_index)

    def handle_interactions(self, bird_index, interaction_zone_birds, all_birds):
        for other_bird_index, distance in interaction_zone_birds:
            self.align_direction(bird_index, other_bird_index, all_birds[other_bird_index], distance)

    def update_position(self, bird_index):
        """Update bird position considering inertia, borders, and restricted areas"""
        # Apply inertia
        self.dx = variables.inertia * self.last_dx + (1 - variables.inertia) * self.dx
        self.dy = variables.inertia * self.last_dy + (1 - variables.inertia) * self.dy
        
        # Adjust speed with random variation
        speed_adjustment = random.gauss(0, 0.35)  # 0.35 is standard deviation
        self.dx += speed_adjustment
        self.dy += speed_adjustment

        # Border collision avoidance
        self.handle_border_collision(bird_index)
        
        # Avoid restricted areas
        self.handle_restricted_areas(bird_index)
        
        # Update last direction
        self.last_dx = self.dx
        self.last_dy = self.dy
        
        # Update position
        variables.X[bird_index] += np.round(self.dx)
        variables.Y[bird_index] += np.round(self.dy)
        
    def handle_border_collision(self,bird_index):
        """Handle collision with screen borders"""
        avoidance_radius = variables.collision_zone_radius * 2
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
            
    def handle_restricted_areas(self,bird_index):
        """Handle collision with restricted areas"""
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
            avoidance_radius = variables.collision_zone_radius * 2
            if distance_to_rect < avoidance_radius or is_inside:
                # Calculate base force (stronger when closer)
                base_force = 1.0 if is_inside else (1 - distance_to_rect / avoidance_radius) * 0.5
                
                # Calculate speed-based multiplier
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

    def check_predator_prey_collision(self, bird_index, other_bird_index, other_bird, distance):
        if distance > variables.collision_zone_radius:
            return False
            
        # Only check collision if this bird can kill and other bird can be killed
        if self.can_kill() and other_bird.can_be_killed() and not other_bird.is_dead:
            angle_to_other = math.atan2(variables.Y[other_bird_index] - variables.Y[bird_index],
                                      variables.X[other_bird_index] - variables.X[bird_index])
            angle_of_movement = math.atan2(self.dy, self.dx)
            angle_diff = (angle_to_other - angle_of_movement) % (2 * math.pi)
            
            if angle_diff < math.radians(100) / 2 or angle_diff > 2 * math.pi - math.radians(100) / 2:
                other_bird.is_dead = True
                # If this is a predator, restore its energy
                if hasattr(self, 'feed'):
                    self.feed()
                return True
        return False
