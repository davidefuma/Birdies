import pygame
import variables

class PopulationChart:
    def __init__(self, x, y):
        self.width = 200
        self.height = 200
        self.x = x
        self.y = y
        self.predator_history = []
        self.prey_history = []
        self.max_population = 0
        self.font = pygame.font.Font(None, variables.POPULATION_FONT_SIZE)
        
        # Create transparent surface
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
    def update(self, num_predators, num_prey):
        # Add new data points
        self.predator_history.append(num_predators)
        self.prey_history.append(num_prey)
        
        # Keep only the last N points
        if len(self.predator_history) > variables.CHART_HISTORY_LENGTH:
            self.predator_history.pop(0)
            self.prey_history.pop(0)
            
        # Update max population for scaling
        self.max_population = max(max(self.predator_history + self.prey_history), 1)
        
    def draw(self, screen):
        # Clear the transparent surface
        self.surface.fill((0, 0, 0, 0))
        
        # Draw semi-transparent background
        pygame.draw.rect(self.surface, (*variables.get_current_theme()['background'], 204), 
                        (0, 0, self.width, self.height))  # 204 is 80% of 255
        
        # Draw title
        title = self.font.render("Population Over Time", True, (*variables.get_current_theme()['text'], 255))
        title_x = (self.width - title.get_width()) // 2
        self.surface.blit(title, (title_x, 5))
        
        # Draw population counts
        pred_text = f"Predators: {self.predator_history[-1]}" if self.predator_history else "Predators: 0"
        prey_text = f"Prey: {self.prey_history[-1]}" if self.prey_history else "Prey: 0"
        
        pred_surface = self.font.render(pred_text, True, (*variables.PREDATOR_COLOR, 255))
        prey_surface = self.font.render(prey_text, True, (*variables.PREY_COLOR, 255))
        
        # Center the population counts
        pred_x = 10
        prey_x = self.width - prey_surface.get_width() - 10
        self.surface.blit(pred_surface, (pred_x, 25))
        self.surface.blit(prey_surface, (prey_x, 25))
        
        # Draw chart border
        pygame.draw.rect(self.surface, (*variables.get_current_theme()['border'], 255),
                        (0, 0, self.width, self.height), 1)
        
        # Draw grid lines
        for i in range(4):
            y_pos = 50 + (i * (self.height - 70) // 3)
            pygame.draw.line(self.surface, (*variables.CHART_GRID_COLOR, 204),
                           (0, y_pos),
                           (self.width, y_pos), 1)
            
            # Draw population value for this grid line
            value = int(self.max_population * (3 - i) / 3)
            value_text = str(value)
            value_surface = self.font.render(value_text, True, (*variables.get_current_theme()['text'], 255))
            self.surface.blit(value_surface, (5, y_pos - 8))
            
        # Draw population lines
        if len(self.predator_history) > 1:
            # Draw predator line
            pred_points = [(int(i * self.width / (len(self.predator_history) - 1)),
                           50 + int((self.height - 70) * (1 - p / self.max_population)))
                          for i, p in enumerate(self.predator_history)]
            if len(pred_points) > 1:
                pygame.draw.lines(self.surface, (*variables.PREDATOR_COLOR, 255), False, pred_points, 2)
            
            # Draw prey line
            prey_points = [(int(i * self.width / (len(self.prey_history) - 1)),
                           50 + int((self.height - 70) * (1 - p / self.max_population)))
                          for i, p in enumerate(self.prey_history)]
            if len(prey_points) > 1:
                pygame.draw.lines(self.surface, (*variables.PREY_COLOR, 255), False, prey_points, 2)
                
        # Blit the transparent surface onto the main screen
        screen.blit(self.surface, (self.x, self.y))
