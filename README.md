# Jetpack Adventure

A 2D endless runner game with retro pixelated graphics inspired by Jetpack Joyride, created with Python and Pygame.

## Game Features

- Retro-style 2D pixelated graphics
- Procedurally generated chiptune background music
- Authentic 8-bit sound effects
- Parallax scrolling background with pixelated cityscape
- Jetpack flight mechanics with realistic physics
- Various obstacles including missiles and laser beams
- Collectible coins in different patterns
- Score system and coin counter
- Animated player character with jetpack effects
- Particle effects for jetpack smoke and dust
- Pixelated explosion animations
- High score tracking

## Installation

1. Install the required dependencies:
   ```
   pip install -r requirements_jetpack.txt
   ```
   
   Or directly:
   ```
   pip install pygame==2.5.2 numpy==1.24.3
   ```

2. Run the game:
   ```
   python jetpack_adventure.py
   ```

## Controls

- **Space Bar**: Hold to activate jetpack and rise
- **Mouse Button**: Hold to activate jetpack (alternative control)
- **M Key**: Toggle background music on/off
- **S Key**: Toggle sound effects on/off
- **Escape**: Quit the game

## Gameplay

- Hold space or mouse button to activate your jetpack and rise
- Release to fall with improved physics and momentum
- Avoid missiles and laser beams
- Collect coins to increase your score
- Your score also increases the longer you survive
- The game ends when you hit an obstacle

## Game Elements

- **Player**: Pixelated blue character with a jetpack
- **Missiles**: Pixelated red projectiles that move faster than the screen scrolling
- **Lasers**: Pixelated red beams that span vertically
- **Coins**: Pixelated yellow spinning coins that can be collected
- **Background**: Multi-layered pixelated city skyline with parallax effect
- **Particles**: Jetpack smoke and ground dust effects
- **UI**: Retro-style score display and coin counter

## Audio Features

- **Background Music**: Procedurally generated 8-bit style chiptune
- **Sound Effects**:
  - Jetpack thrust
  - Coin collection
  - Explosion
  - Laser/missile sounds
  - Menu selection
  - Game over

## Technical Notes

The game creates all graphics and audio programmatically:
- All graphics are generated using Pygame's drawing functions for an authentic pixel art style
- All sound effects and music are procedurally generated using NumPy
- No external image or audio files are required

This makes the game completely self-contained and easy to run on any system without worrying about missing assets.
