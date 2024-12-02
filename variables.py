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
