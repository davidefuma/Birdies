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
        
    def draw(self, bird_index, screen):
        # Calculate rotation angle based on movement direction
        angle = math.degrees(math.atan2(self.dy, self.dx))
        size = self.get_size()
        color = self.get_color()
        
        if self.is_dead:
            # Draw dead bird with enhanced fade effect
            alpha = max(50, self.fade_alpha if hasattr(self, 'fade_alpha') else 255)  # Increased minimum alpha
            if hasattr(self, 'fade_alpha'):
                self.fade_alpha = max(50, self.fade_alpha - 0.3)  # Slower fade
            else:
                self.fade_alpha = 255
            
            # Create surface for dead bird with more detailed shape
            bird_surface = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
            pygame.draw.polygon(bird_surface, (*color[:3], alpha), [
                (size * 3, size * 1.5),  # Elongated tip
                (0, size),  # Top back
                (size, size * 1.5),  # Back indent
                (0, size * 2),  # Bottom back
            ])
            
            # Add subtle wing-like details
            wing_color = (*color[:3], alpha // 2)
            pygame.draw.polygon(bird_surface, wing_color, [
                (size * 2, size * 1.5),
                (size, size),
                (size * 1.5, size * 1.5),
            ])
        else:
            # Create surface for living bird
            bird_surface = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
            
            # Draw the main body with more dynamic shape
            pygame.draw.polygon(bird_surface, color, [
                (size * 3, size * 1.5),  # Elongated nose
                (0, size),  # Top back
                (size, size * 1.5),  # Back indent
                (0, size * 2),  # Bottom back
            ])
            
            # Add more detailed eye
            eye_pos = (size * 2.5, size * 1.5)
            pygame.draw.circle(bird_surface, (255, 255, 255), eye_pos, size/4)  # Larger white of eye
            pygame.draw.circle(bird_surface, (0, 0, 0), eye_pos, size/6)  # Larger pupil
            
            # Add wing details
            wing_color = tuple(max(0, c - 30) for c in color[:3])  # Slightly darker wing color
            pygame.draw.polygon(bird_surface, wing_color, [
                (size * 2, size * 1.5),
                (size, size),
                (size * 1.5, size * 1.5),
            ])
            
            # Add motion blur effect for fast-moving birds
            speed = math.hypot(self.dx, self.dy)
            if speed > 2:
                blur_surface = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
                blur_color = (*color[:3], 50)  # Very transparent
                pygame.draw.polygon(blur_surface, blur_color, [
                    (size * 3, size * 1.5),
                    (0, size),
                    (size, size * 1.5),
                    (0, size * 2),
                ])
                screen.blit(pygame.transform.rotate(blur_surface, -angle),
                          (variables.X[bird_index] - size + self.dx,
                           variables.Y[bird_index] - size + self.dy))
        
        # Rotate and draw the bird
        rotated_bird = pygame.transform.rotate(bird_surface, -angle)
        screen.blit(rotated_bird,
                   (variables.X[bird_index] - rotated_bird.get_width()/2,
                    variables.Y[bird_index] - rotated_bird.get_height()/2))
        
        # Draw interaction zones if enabled
        if variables.show_zones:
            self.draw_collision_zone(bird_index)
            self.draw_interaction_zone(bird_index)
        
    def get_size(self):
        """Override in subclasses to define specific sizes"""
        return 10  # Increased base size from 5 to 10
        
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
        
        # Dynamic speed adjustment based on distance
        speed_adjustment = max(0.1, min(1.0, 1.0 - distance / variables.interaction_zone_radius))
        self.dx = speed_adjustment * math.cos(angle_of_other_movement)
        self.dy = speed_adjustment * math.sin(angle_of_other_movement)

        # Shift towards the other bird
        dx_to_other = variables.X[other_bird_index] - variables.X[bird_index]
        dy_to_other = variables.Y[other_bird_index] - variables.Y[bird_index]

        if distance > 0:  # Avoid division by zero if birds are at the same position
            # Dynamic shift adjustment based on distance
            shift_strength = variables.shift_to_buddy * (1.0 - distance / variables.interaction_zone_radius)
            self.dx += shift_strength * dx_to_other / distance
            self.dy += shift_strength * dy_to_other / distance

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
            other_bird = all_birds[other_bird_index]
            # Skip aligning and shifting towards predators
            if other_bird.can_kill():
                continue
            self.align_direction(bird_index, other_bird_index, other_bird, distance)

    def update_position(self, bird_index):
        """Update bird position considering inertia, borders, and restricted areas"""
        # Calculate desired direction
        desired_dx = self.dx
        desired_dy = self.dy
        
        # Calculate current angle and desired angle
        current_angle = math.atan2(self.last_dy, self.last_dx)
        desired_angle = math.atan2(desired_dy, desired_dx)
        
        # Calculate angle difference
        angle_diff = desired_angle - current_angle
        
        # Normalize angle difference
        angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi
        
        # Limit turning angle
        max_turn_angle = math.radians(5)  # Maximum 5 degree turn per update
        if abs(angle_diff) > max_turn_angle:
            angle_diff = max_turn_angle if angle_diff > 0 else -max_turn_angle
        
        # Calculate new direction based on limited turn
        new_angle = current_angle + angle_diff
        
        # Update direction with limited turn
        self.dx = math.cos(new_angle) * math.hypot(desired_dx, desired_dy)
        self.dy = math.sin(new_angle) * math.hypot(desired_dx, desired_dy)
        
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
