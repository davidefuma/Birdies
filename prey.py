import variables
from bird import Bird

class Prey(Bird):
    def __init__(self, dx, dy):
        super().__init__(dx, dy)
        
    def get_size(self):
        """Prey use base size"""
        return super().get_size()
        
    def get_color(self):
        """Prey are green when alive, black when dead"""
        if self.is_dead:
            return variables.get_current_theme()['dead_prey']
        return variables.PREY_COLOR
        
    def can_kill(self):
        """Prey cannot kill"""
        return False
        
    def can_be_killed(self):
        """Prey can be killed"""
        return True
