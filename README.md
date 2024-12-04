# Flyes - Predator-Prey Simulation

A dynamic 2D predator-prey simulation game built with Pygame, featuring complex flocking behaviors and ecosystem dynamics.

## Features

### Core Mechanics
- Two distinct species: Predators and Prey
- Realistic flocking behavior with collision avoidance
- Energy system for predators
- Population tracking and visualization
- Interactive control panel with real-time parameter adjustment

### Advanced Behaviors
- Predators actively hunt and consume prey
- Dead birds remain stationary and don't influence living birds
- Speed-based energy consumption for predators
- Dynamic interaction zones for movement and alignment
- Intelligent border and restricted area avoidance

## Controls

### Control Panel
- **Inertia:** Controls how much birds maintain their previous direction
- **Speed Reduction:** Scales the overall speed of birds
- **Sensible Radius:** Radius of the collision avoidance zone
- **Interaction Radius:** Radius of the flocking alignment zone
- **Shift to Buddy:** Strength of movement towards other birds
- **Show Zones:** Toggle visibility of interaction zones
- **Theme Toggle:** Switch between light and dark modes

### Population Tracking
- Real-time population counter
- Semi-transparent population history chart
- Color-coded tracking for predators and prey

## Installation

1. Ensure you have Python 3.x installed
2. Install required dependencies:
```bash
pip install pygame numpy
```

## Running the Simulation

```bash
python birdies_game.py
```

## Technical Details

### Bird Behaviors
- Birds follow complex flocking rules based on nearby neighbors
- Dead birds are completely ignored in all calculations:
  - No collision detection with dead birds
  - No flocking influence from dead birds
  - Dead birds remain stationary
- Predators consume energy while moving and hunting
- Prey turn black and stop moving when killed

### Performance Optimizations
- Efficient collision detection algorithms
- Optimized movement calculations
- Smart rendering of interaction zones

## Contributing

Feel free to fork the project and submit pull requests! Areas for potential improvement:
- Additional species types
- More complex hunting behaviors
- Environmental factors
- Genetic evolution
- Performance optimizations