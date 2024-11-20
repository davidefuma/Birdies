import pygame


class Checkbox:
    def __init__(self, x, y, size, initial_state, label):
        self.x = x
        self.y = y
        self.size = size
        self.state = initial_state
        self.label = label
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)  # White border
        if self.state:
            pygame.draw.rect(screen, (0, 0, 0), self.rect.inflate(-4, -4))  # Filled black box if checked

        font = pygame.font.Font(None, 20)
        label_text = font.render(self.label, True, (0, 0, 0))
        screen.blit(label_text, (self.x + self.size + 10, self.y + 2))

    def update(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
            self.state = not self.state
