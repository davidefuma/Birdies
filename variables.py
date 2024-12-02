# Parameters (initial values)
import pygame

inertia = 0.9

collision_zone_radius = 15
interaction_zone_radius = 30
shift_to_buddy = 0.7  # Adjust this value to control the shift strength
show_zones = True  # Initially show the zones

# Screen dimensions
panel_width = 200
screen_width = 1400
screen_height = 800
BORDER_THICKNESS = 5  # Define border thickness
screen = pygame.display.set_mode((screen_width, screen_height))

X = []  # Vector to store x-coordinates of birds
Y = []  # Vector to store y-coordinates of birds


# Define multiple restricted areas as tuples of (x, y, width, height)
restricted_areas = [
    (100, 100, 200, 100),  # Area 1
    (400, 150, 150, 200),  # Area 2
    (600, 50, 100, 300),  # Area 3
]

# Predator-Prey constants
PREDATOR_SIZE_RATIO = 2.0  # Predators are twice as big as prey
PREDATOR_SPEED_RATIO = 0.6  # Predators move at 60% of prey speed

# Colors
PREDATOR_COLOR = (255, 0, 0)  # Red
PREY_COLOR = (0, 255, 0)  # Green
DEAD_PREY_COLOR = (0, 0, 0)  # Black

# Dark/Light mode colors
is_dark_mode = True  # Default to dark mode

# Color schemes
DARK_MODE = {
    'background': (0, 0, 0),        # Black
    'border': (255, 255, 255),      # White
    'panel': (50, 50, 50),          # Dark Gray
    'text': (255, 255, 255),        # White
    'dead_prey': (128, 128, 128),   # Gray
    'restricted': (40, 40, 40)  ,    # Darker Gray
    'prey': (0, 255, 0),   # Green
    'predator': (255, 0, 0),   # Red
}

LIGHT_MODE = {
    'background': (255, 255, 255),  # White
    'border': (0, 0, 0),           # Black
    'panel': (220, 220, 220),      # Light Gray
    'text': (0, 0, 0),            # Black
    'dead_prey': (128, 128, 128),  # Gray
    'restricted': (200, 200, 200),  # Light Gray
    'prey': (0, 255, 0),   # Green
    'predator': (255, 0, 0),   # Red
}

def get_current_theme():
    return DARK_MODE if is_dark_mode else LIGHT_MODE
