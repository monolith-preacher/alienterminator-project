# Alien Terminator

A classic space shooter made with Python and Pygame. You control a hero at the bottom of the screen and fire at waves of aliens descending from the top. The game is endless: the goal is to get the highest score possible before being defeated.

## Gameplay

- **Aliens** descend in waves. Each alien destroyed is worth **10 points**.
- **Special shot:** every **15 aliens** eliminated grants **3 uses** of a spread shot (press **B**). Each of its five projectiles can pierce up to four aliens.
- **Meteorites** are indestructible and fall periodically — dodge them.
- **Predator (boss):** appears for the first time at **100 points** and then every **200 points** (100, 300, 500, …). It fires lasers and takes **5 hits** from regular shots to defeat. No new alien waves arrive while it is alive.
- Touching an alien, a meteorite, a laser or the Predator means **game over**.

## Controls

| Key          | Action                            |
|--------------|-----------------------------------|
| ← / →        | Move                              |
| Space        | Shoot                             |
| B            | Special shot (when available)     |
| ESC          | Return to the main menu           |
| ↑ / ↓, Enter | Navigate and select in the menu   |
| I            | Jump to "Instructions" in the menu |

## Requirements

- Python **3.8+**
- [Pygame](https://www.pygame.org/) 2.5 or newer (installed from `requirements.txt`)

## Installation and running (Ubuntu)

```bash
# 1. System packages (Python virtual environment support)
sudo apt update
sudo apt install python3 python3-venv python3-pip

# 2. Clone the repository
git clone <repository-url>
cd alienterminator-project

# 3. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 4. Install the dependencies
pip install -r requirements.txt

# 5. Run the game
python alienterminator.py
```

The game can also be started with `python -m alien_terminator`. Assets are located relative to the source code, so it can be launched from any directory. To leave the virtual environment, run `deactivate`.

On Windows and macOS the steps are the same, except that the environment is activated with `.venv\Scripts\activate` (Windows) and `python` may be used instead of `python3`.

### Running on WSL (Windows Subsystem for Linux)

On Windows 11 (or Windows 10 with a recent WSL), **WSLg** provides the graphical window and the audio (through PulseAudio) automatically — no extra configuration is needed. You can check it with:

```bash
echo $DISPLAY $WAYLAND_DISPLAY   # should not be empty
echo $PULSE_SERVER               # usually unix:/mnt/wslg/PulseServer
```

If WSLg is not available, update WSL from Windows with `wsl --update` and restart it with `wsl --shutdown`.

### Audio and error handling

- If no audio device is available, the game prints a warning and **keeps running without sound**.
- Missing or unreadable sound files are skipped individually, with a warning.
- Missing images or an unavailable display stop the game with a clear error message (exit code 1) instead of a traceback.

## Running the tests

The tests use only the standard library (`unittest`) and run without opening a window or using the sound card:

```bash
python -m unittest discover -s tests -v
```

They cover the game rules (movement, shooting, special shot, Predator, collisions and game over), the fixed-step timer, asset integrity, audio fallbacks and screen rendering.

## Project structure

```
alienterminator-project/
├── alienterminator.py        # Entry point
├── alien_terminator/         # Game package
│   ├── __main__.py           # Allows `python -m alien_terminator`
│   ├── app.py                # Initialization, main loop and screen navigation
│   ├── config.py             # Constants: screen, gameplay, audio, asset paths
│   ├── assets.py             # Image loading (once, converted to the display format)
│   ├── audio.py              # Sound effects and music, tolerant to audio failures
│   ├── entities.py           # Sprites: player, bullets, aliens, meteorites, Predator, lasers
│   ├── game.py               # Game session: rules, collisions, scoring, drawing
│   ├── timing.py             # Fixed-step timer (frame-rate independent gameplay)
│   └── ui.py                 # Menu, instructions, HUD and game over screens
├── tests/                    # Automated tests (unittest)
├── tools/
│   └── generate_music.py     # Generates the background music
├── assets/                   # Images, sound effects and music
└── requirements.txt
```

## Technical notes

- **Frame-rate independence:** the game logic advances in fixed steps of 1/60 s. On a normal machine this is exactly one update per frame (the original behavior); if the computer cannot keep up with 60 FPS, several steps are run per frame so the game speed stays the same instead of slowing down.
- **Resource caching:** images are loaded once and converted to the display format; fonts are created once and texts are only re-rendered when their content changes.
- **Sprites:** entities use `pygame.sprite.Sprite` and `Group` for updating, drawing and collision checks.

## Music and sound

The background music is an original chiptune track synthesized by [`tools/generate_music.py`](tools/generate_music.py) using only the Python standard library. To regenerate it:

```bash
python tools/generate_music.py
```

Sound effects: thanks to the sound creators on YouTube.
