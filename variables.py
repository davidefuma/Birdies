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
screen = pygame.display.set_mode((screen_width, screen_height))

X = []  # Vector to store x-coordinates of birds
Y = []  # Vector to store y-coordinates of birds