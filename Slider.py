import pygame
import variables

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
        theme = variables.get_current_theme()
        pygame.draw.rect(screen, theme['border'], (self.x, self.y, self.width, self.height)) # Slider bar
        pygame.draw.rect(screen, variables.SLIDER_HANDLE_COLOR, self.slider_rect) # Slider handle in orange

        font = pygame.font.Font(None, 20)
        label_text = font.render(f"{self.label}: {self.val:.2f}", True, theme['text'])
        screen.blit(label_text, (self.x, self.y - 25)) # Label above the slider

    def update(self, mouse_pos):
        if self.slider_rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]: # Dragging
            self.slider_x = max(self.x, min(mouse_pos[0], self.x + self.width))
            self.slider_rect.x = self.slider_x - 5
            self.val = self.min_val + (self.slider_x - self.x) / self.width * (self.max_val - self.min_val)
