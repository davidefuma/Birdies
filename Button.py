import pygame
import variables

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_clicked = False
        self.click_time = 0
        
    def draw(self, screen):
        theme = variables.get_current_theme()
        # Draw button background
        pygame.draw.rect(screen, theme['border'], self.rect, 2)  # Border
        
        # Draw text
        font = pygame.font.Font(None, 20)
        text_surface = font.render(self.text, True, theme['text'])
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def update(self, mouse_pos):
        current_time = pygame.time.get_ticks()
        if (self.rect.collidepoint(mouse_pos) and 
            pygame.mouse.get_pressed()[0] and 
            current_time - self.click_time > 200):  # 200ms debounce
            self.is_clicked = True
            self.click_time = current_time
            # Toggle dark mode
            variables.is_dark_mode = not variables.is_dark_mode
            return True
        return False
