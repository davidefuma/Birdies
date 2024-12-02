import pygame
import variables

class Checkbox:
    def __init__(self, x, y, size, initial_state, label):
        self.x = x
        self.y = y
        self.size = size
        self.state = initial_state
        self.label = label
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)

    def draw(self, screen):
        theme = variables.get_current_theme()
        pygame.draw.rect(screen, theme['border'], self.rect, 2)  # Border
        if self.state:
            pygame.draw.rect(screen, theme['text'], self.rect.inflate(-4, -4))  # Filled box if checked

        font = pygame.font.Font(None, 20)
        label_text = font.render(self.label, True, theme['text'])
        screen.blit(label_text, (self.x + self.size + 10, self.y + 2))

    def update(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
            self.state = not self.state
