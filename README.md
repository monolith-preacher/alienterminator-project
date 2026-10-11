# Alien Terminator

A classic space shooter made with Python and Pygame. You control a hero at the bottom of the screen and fire at waves of aliens descending from the top. The game is endless: the goal is to get the highest score possible before being defeated.

## Gameplay

- **Aliens** descend in waves. Each alien destroyed is worth **10 points**.
- **Special shot:** every **15 aliens** eliminated grants **3 uses** of a spread shot (press **B**).
- **Meteorites** are indestructible and fall periodically — dodge them.
- **Predator (boss):** appears for the first time at **100 points** and then every **200 points** (100, 300, 500, …). It fires lasers and takes **5 hits** to defeat.
- Touching an alien, a meteorite, or a laser means **game over**.

## Controls

| Key          | Action                            |
|--------------|-----------------------------------|
| ← / →        | Move                              |
| Space        | Shoot                             |
| B            | Special shot (when available)     |
| ESC          | Return to the main menu           |
| ↑ / ↓, Enter | Navigate and select in the menu   |

## How to run

Requires **Python 3.8+**.

```bash
git clone <repository-url>
cd alienterminator-project
pip install -r requirements.txt
python alienterminator.py
```

On some systems the command is `python3` instead of `python`. The game finds its assets relative to the script, so it can be launched from any directory.

## Project structure

```
alienterminator-project/
├── alienterminator.py      # Game source code
├── requirements.txt
├── tools/
│   └── generate_music.py   # Generates the background music
└── assets/
    ├── alien.png
    ├── background.png
    ├── heart.png
    ├── meteorite.png
    ├── player.png
    ├── predator.png
    ├── predator_laser.png
    ├── predator_laser2.png
    ├── background_music.wav
    ├── damage.wav
    ├── shoot.wav
    └── special_shot.wav
```

## Music and sound

The background music is an original chiptune track synthesized by [`tools/generate_music.py`](tools/generate_music.py) using only the Python standard library. To regenerate it:

```bash
python tools/generate_music.py
```

Sound effects: thanks to the sound creators on YouTube.
