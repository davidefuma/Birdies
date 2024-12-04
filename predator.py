import variables
from bird import Bird

class Predator(Bird):
    def __init__(self, dx, dy):
        # Apply speed reduction before passing to parent
        adjusted_dx = dx * variables.PREDATOR_SPEED_RATIO
        adjusted_dy = dy * variables.PREDATOR_SPEED_RATIO
        super().__init__(adjusted_dx, adjusted_dy)
        
    def get_size(self):
        """Predators are larger"""
        return super().get_size() * variables.PREDATOR_SIZE_RATIO
        
    def get_color(self):
        """Predators are red"""
        return variables.PREDATOR_COLOR
        
    def can_kill(self):
        """Predators can kill prey"""
        return True
        
    def can_be_killed(self):
        """Predators cannot be killed"""
        return False
