# Birdies

A simple 2D fly simulation game built with Pygame.

## How to Play

1.  Make sure you have Pygame installed (`pip install pygame`).
2.  Run the `birdies_game.py` script.
3.  Use the sliders in the control panel to adjust the simulation parameters:
    *   **Inertia:** Controls how much the flies maintain their previous direction.
    *   **Speed Reduction:** Scales the overall speed of the flies.
    *   **Sensible Radius:** Radius of the sensible zone (used for collision avoidance).
    *   **Interaction Radius:** Radius of the interaction zone (used for aligning direction).
    *   **Shift to Buddy:**  How much flies move towards others in the interaction zone.

## Controls
No keyboard or mouse controls within the game board.  All interaction is through the control panel sliders.

## Launch

```
python birdies_game.py
```

## Requirements

*   Python 3
*   Pygame

## Installation of pygame library

```bash
pip install pygame
```

## Contributing


Feel free to fork the project and submit pull requests!