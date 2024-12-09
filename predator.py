import math
import variables
import pygame
from bird import Bird

class Predator(Bird):
    def __init__(self, dx, dy):
        # Apply speed reduction before passing to parent
        adjusted_dx = dx * variables.PREDATOR_SPEED_RATIO
        adjusted_dy = dy * variables.PREDATOR_SPEED_RATIO
        super().__init__(adjusted_dx, adjusted_dy)
        
        # Energy system
        self.energy = variables.PREDATOR_INITIAL_ENERGY
        self.cycle_counter = 0
        
    def update_energy(self):
        """Update predator's energy level based on time and speed"""
        if self.is_dead:
            return
            
        # Time-based energy loss
        self.cycle_counter += 1
        if self.cycle_counter >= variables.PREDATOR_ENERGY_LOSS_INTERVAL:
            self.cycle_counter = 0
            self.energy -= variables.PREDATOR_ENERGY_LOSS_AMOUNT
            
            # Speed-based energy loss
            current_speed = math.sqrt(self.dx**2 + self.dy**2)
            if current_speed > variables.PREDATOR_BASE_SPEED:
                speed_cost = (current_speed - variables.PREDATOR_BASE_SPEED) * variables.PREDATOR_SPEED_ENERGY_COST
                self.energy -= speed_cost
            
            # Check if predator dies from starvation
            if self.energy <= 0:
                self.energy = 0
                self.is_dead = True
                
    def feed(self):
        """Restore energy after killing prey"""
        self.energy = variables.PREDATOR_INITIAL_ENERGY
        
    def draw(self, bird_index,screen):
        # Draw the bird triangle
        super().draw(bird_index,screen)
        
        # Draw energy bar if alive
        if not self.is_dead:
            self.draw_energy_bar(bird_index)
            
    def draw_energy_bar(self, bird_index):
        """Draw energy bar above the predator"""
        # Calculate energy bar position
        bar_x = variables.X[bird_index] - variables.ENERGY_BAR_WIDTH // 2
        bar_y = variables.Y[bird_index] - variables.ENERGY_BAR_OFFSET
        
        # Draw background (black)
        pygame.draw.rect(variables.screen, (0, 0, 0),
                        (bar_x, bar_y, variables.ENERGY_BAR_WIDTH, variables.ENERGY_BAR_HEIGHT))
        
        # Calculate energy bar width based on current energy
        energy_width = int((self.energy / variables.PREDATOR_INITIAL_ENERGY) * variables.ENERGY_BAR_WIDTH)
        
        # Choose color based on energy level
        if self.energy > variables.PREDATOR_INITIAL_ENERGY * 0.7:
            color = variables.ENERGY_BAR_HIGH
        elif self.energy > variables.PREDATOR_INITIAL_ENERGY * 0.3:
            color = variables.ENERGY_BAR_MEDIUM
        else:
            color = variables.ENERGY_BAR_LOW
            
        # Draw energy bar
        if energy_width > 0:
            pygame.draw.rect(variables.screen, color,
                           (bar_x, bar_y, energy_width, variables.ENERGY_BAR_HEIGHT))
        
    def get_size(self):
        """Predators are larger"""
        return super().get_size() * variables.PREDATOR_SIZE_RATIO
        
    def get_color(self):
        """Predators are red when alive, black when dead"""
        if self.is_dead:
            return variables.get_current_theme()['dead_prey']  # Use same color as dead prey
        return variables.PREDATOR_COLOR
        
    def can_kill(self):
        """Predators can kill prey if they're alive"""
        return not self.is_dead
        
    def can_be_killed(self):
        """Predators cannot be killed by other birds"""
        return False
