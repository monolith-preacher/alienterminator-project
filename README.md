# Alien Terminator

A classic arcade-style space shooter written in Python with [Pygame](https://www.pygame.org/). You control a ship at the bottom of the screen and fire at waves of aliens descending from the top, while dodging meteorites and fighting a recurring boss, the Predator. The game is endless: the goal is to reach the highest score possible before being defeated.

## Table of contents

- [Branches](#branches)
- [Gameplay](#gameplay)
- [Controls](#controls)
- [Requirements](#requirements)
- [Getting the code](#getting-the-code)
- [Installation and running](#installation-and-running)
  - [Linux (Ubuntu)](#linux-ubuntu)
  - [Ubuntu on WSL (Windows Subsystem for Linux)](#ubuntu-on-wsl-windows-subsystem-for-linux)
  - [macOS](#macos)
  - [Windows](#windows)
- [Running the tests](#running-the-tests)
- [Troubleshooting](#troubleshooting)
- [Project structure](#project-structure)
- [Technical notes](#technical-notes)
- [Music and sound](#music-and-sound)

## Branches

The repository currently has two branches:

| Branch         | Contents |
|----------------|----------|
| `main`         | The original version of the game, implemented in a single file (`alienterminator.py`). |
| `optimization` | The refactored version: the same gameplay, reorganized into the `alien_terminator` package, with performance improvements, frame-rate independent timing, error handling for missing audio devices and assets, and an automated test suite. |

**This README documents the `optimization` branch.** The `alien_terminator/` package, the `tests/` directory, the `python -m alien_terminator` command and the audio fallback described below exist only on this branch until it is merged into `main`. The gameplay and controls are the same in both branches.

## Gameplay

- **Aliens** descend in waves of ten. Each alien destroyed is worth **10 points**.
- **Meteorites** are indestructible and keep falling — dodge them.
- **Special shot:** every **15 aliens** destroyed charges **3 uses** of a spread shot (press **B**). It fires in five directions, and each projectile can pierce up to four aliens. There is a short cooldown (0.5 s) between special shots.
- **Predator (boss):** appears for the first time at **100 points** and then every **200 points** (100, 300, 500, …). It moves across the top of the screen firing lasers and must be hit **5 times** with regular shots to be defeated (the special shot does not damage it). No new alien waves arrive while it is alive.
- Touching an alien, a meteorite, a laser or the Predator means **game over**. The final screen shows the score, total alien kills and Predator kills.

## Controls

| Key           | Action                                              |
|---------------|-----------------------------------------------------|
| ← / →         | Move left / right                                   |
| Space         | Shoot                                               |
| B             | Special shot (when charged)                         |
| ESC           | In game: return to the main menu. In the menu: quit |
| ↑ / ↓         | Navigate the main menu                              |
| Enter         | Select a menu option                                |
| I             | Highlight "Instructions" in the main menu           |

## Requirements

- **Python 3.8 to 3.13.** The game was developed and tested with Python 3.12.
  At the time of writing, the latest Pygame release (2.6.1) provides prebuilt packages only up to Python 3.13. On Python 3.14 or newer, `pip` tries to compile Pygame from source, which usually fails — see [Troubleshooting](#pip-fails-to-install-pygame-on-a-new-python-version).
- **Pygame 2.5 or newer** — installed automatically from `requirements.txt`.
- **Git**, to clone the repository (alternatively, download a ZIP from GitHub: select the branch, then **Code → Download ZIP**).

## Getting the code

Cloning the repository without options gives you the default branch, `main` (the original version):

```bash
git clone https://github.com/monolith-preacher/alienterminator-project.git
```

To get the refactored version described in this README, clone the `optimization` branch directly:

```bash
git clone -b optimization https://github.com/monolith-preacher/alienterminator-project.git
```

If you have already cloned the repository, you can switch branches from inside the project directory:

```bash
git switch optimization   # refactored version
git switch main           # original version
```

Both commands create a directory named `alienterminator-project`. All the commands in the next sections must be run from inside it.

## Installation and running

The steps are the same on every system: check the Python version, create a virtual environment, activate it, install the dependencies and start the game. A virtual environment keeps the project's packages isolated from the system Python and is the recommended way to run the game.

Once the virtual environment is active, the prompt usually shows `(.venv)` and the `python` command refers to the environment's interpreter on every operating system. To leave it, run `deactivate`. The next time you want to play, you only need to enter the project directory, activate the environment and run the game.

### Linux (Ubuntu)

On many Linux distributions, including Ubuntu, the `python` command does not exist outside a virtual environment — use `python3` until the environment is active.

```bash
# 1. Install Python, venv support and Git
sudo apt update
sudo apt install python3 python3-venv python3-pip git

# 2. Clone the repository and enter the directory
git clone -b optimization https://github.com/monolith-preacher/alienterminator-project.git
cd alienterminator-project

# 3. Check the Python version (3.8 to 3.13)
python3 --version

# 4. Create and activate the virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 5. Install the dependencies
pip install -r requirements.txt

# 6. Start the game
python alienterminator.py
```

The game can also be started with `python -m alien_terminator`. Assets are located relative to the source code, so the game can be launched from any working directory, for example `python /path/to/alienterminator-project/alienterminator.py`.

### Ubuntu on WSL (Windows Subsystem for Linux)

The game was developed and tested on Ubuntu 24.04 running on WSL 2. Graphics and sound are provided by **WSLg**, which is included in current WSL versions on Windows 11 and in recent WSL releases on Windows 10. With WSLg, the game window opens on the Windows desktop like a native application.

1. In a Windows terminal, make sure WSL is up to date:

   ```powershell
   wsl --update
   wsl --version
   ```

   `wsl --version` should list a WSLg version. If you updated WSL, restart it with `wsl --shutdown` and open Ubuntu again.

2. Inside Ubuntu, follow exactly the same steps as in the [Linux (Ubuntu)](#linux-ubuntu) section. It is recommended to clone the project inside the Linux file system (for example, in your home directory, `~`) rather than under `/mnt/c/`, for better file-access performance.

3. Optionally, confirm that WSLg is available:

   ```bash
   echo $DISPLAY $WAYLAND_DISPLAY   # should print values such as ":0 wayland-0"
   echo $PULSE_SERVER               # usually unix:/mnt/wslg/PulseServer
   ```

In most installations the game runs with sound without any extra configuration. If audio fails to start with an ALSA error, see [No sound or ALSA error on WSL](#no-sound-or-alsa-error-on-wsl).

### macOS

```bash
# 1. Clone the repository and enter the directory
git clone -b optimization https://github.com/monolith-preacher/alienterminator-project.git
cd alienterminator-project

# 2. Check the Python version (3.8 to 3.13)
python3 --version

# 3. Create and activate the virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 4. Install the dependencies
pip install -r requirements.txt

# 5. Start the game
python alienterminator.py
```

If `python3` is not installed, or its version is newer than 3.13, install a compatible version from [python.org](https://www.python.org/downloads/macos/) or with Homebrew (`brew install python@3.13`) and create the environment with that interpreter, for example `python3.13 -m venv .venv`. If `git` is missing, macOS offers to install the Command Line Developer Tools the first time you run it.

### Windows

These commands assume Python was installed from [python.org](https://www.python.org/downloads/windows/), which includes the `py` launcher, and that [Git for Windows](https://git-scm.com/download/win) is installed.

```powershell
# 1. Clone the repository and enter the directory
git clone -b optimization https://github.com/monolith-preacher/alienterminator-project.git
cd alienterminator-project

# 2. Check the Python version (3.8 to 3.13)
py --version

# 3. Create the virtual environment
py -m venv .venv
```

Activate the virtual environment with the command for your terminal:

| Terminal          | Activation command          |
|-------------------|-----------------------------|
| PowerShell        | `.venv\Scripts\Activate.ps1` |
| Command Prompt (CMD) | `.venv\Scripts\activate.bat` |

If PowerShell refuses to run the activation script, see [PowerShell blocks the activation script](#powershell-blocks-the-activation-script).

Then install the dependencies and start the game (same commands in PowerShell and CMD):

```powershell
pip install -r requirements.txt
python alienterminator.py
```

If several Python versions are installed, you can choose one when creating the environment, for example `py -3.12 -m venv .venv`. If the `py` launcher is not available (for example, with the Microsoft Store version of Python), use `python` instead of `py` in the commands above.

## Running the tests

The `optimization` branch includes an automated test suite written with the standard library's `unittest` module, so no extra packages are needed. With the virtual environment active, run from the project root:

```bash
python -m unittest discover -s tests -v
```

The tests run without opening a window or using the sound card. They check the game rules that can be verified independently of the graphical interface — movement, shooting, the special shot, the Predator, collisions, scoring and game over — as well as the fixed-step timer, the integrity of the asset files, the audio fallbacks and the rendering of each screen without errors. They help catch regressions, but they do not replace playing the game and do not guarantee the absence of bugs.

## Troubleshooting

### `error: externally-managed-environment`

Recent versions of Ubuntu, Debian and other distributions prevent `pip` from installing packages into the system Python ([PEP 668](https://peps.python.org/pep-0668/)). This error means `pip install` was run **outside** a virtual environment. Do not work around it by modifying system packages (for example with `--break-system-packages`); instead, create and activate the virtual environment and install the dependencies inside it:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### `The virtual environment was not created successfully because ensurepip is not available`

The `venv` module is installed separately on Debian and Ubuntu. Install it, remove the incomplete environment and create it again:

```bash
sudo apt install python3-venv
rm -rf .venv
python3 -m venv .venv
```

### `python: command not found`

Outside a virtual environment, some Linux distributions only provide the `python3` command. Use `python3` to create the environment; after activating it, `python` is available. On Windows, use the `py` launcher.

### pip fails to install Pygame on a new Python version

If `pip install -r requirements.txt` tries to build Pygame from source and fails with compilation errors, your Python version is probably newer than the versions supported by the available Pygame release (currently up to 3.13). Install Python 3.13 or earlier, delete the `.venv` directory and create the environment again with that version.

### PowerShell blocks the activation script

If PowerShell reports that running scripts is disabled on this system, allow local scripts for your user and try again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
.venv\Scripts\Activate.ps1
```

Alternatively, use the Command Prompt (CMD) and `.venv\Scripts\activate.bat`.

### No sound or ALSA error on WSL

**These steps are only needed if your environment shows audio problems; they are not required for a normal installation.**

On WSL, the game may fail to open the audio device with the message:

```
ALSA: Couldn't open audio device: No such file or directory
```

This happens when SDL (the library used by Pygame) cannot use the PulseAudio server provided by WSLg and falls back to ALSA, for which WSL has no sound card. How the game reacts depends on the branch:

- On `optimization`, the game prints a warning and keeps running **without sound**.
- On `main`, the error stops the game at startup.

To restore the sound:

1. Check that the WSLg PulseAudio server is available:

   ```bash
   echo $PULSE_SERVER          # expected: unix:/mnt/wslg/PulseServer
   ls -l /mnt/wslg/PulseServer
   ```

   If the variable is empty or the file does not exist, WSLg is not active — update WSL as described in [Ubuntu on WSL](#ubuntu-on-wsl-windows-subsystem-for-linux).

2. Install the PulseAudio client library, which SDL needs to talk to the server:

   ```bash
   sudo apt install libpulse0
   ```

   On Ubuntu 24.04 the package is named `libpulse0`. Some distribution releases rename libraries with a `t64` suffix (for example `libpulse0t64`); if `apt` reports that `libpulse0` has no installation candidate, look up the name used by your release and install it:

   ```bash
   apt-cache search --names-only '^libpulse0'
   ```

3. Start the game forcing the PulseAudio driver:

   ```bash
   SDL_AUDIODRIVER=pulseaudio python alienterminator.py
   ```

   After the library is installed, SDL normally selects PulseAudio automatically, and plain `python alienterminator.py` also works. To always force the driver in your shell, you can add `export SDL_AUDIODRIVER=pulseaudio` to `~/.bashrc`.

If you just want to play without sound, disable audio output completely — this works on any system and on both branches:

```bash
SDL_AUDIODRIVER=dummy python alienterminator.py
```

### The game window does not open

On WSL, this usually means WSLg is not available: check `echo $DISPLAY $WAYLAND_DISPLAY` and update WSL with `wsl --update`. On the `optimization` branch, the game exits with an error message describing the problem instead of a traceback.

Messages printed by the game to the terminal (warnings and errors) are currently in Portuguese.

## Project structure

```
alienterminator-project/
├── alienterminator.py        # Entry point: python alienterminator.py
├── alien_terminator/         # Game package
│   ├── __init__.py
│   ├── __main__.py           # Entry point: python -m alien_terminator
│   ├── app.py                # Initialization, main loop and screen navigation
│   ├── assets.py             # Image loading (once, converted to the display format)
│   ├── audio.py              # Sound effects and music, tolerant to audio failures
│   ├── config.py             # Constants: screen, gameplay, audio and asset paths
│   ├── entities.py           # Sprites: player, bullets, aliens, meteorites, Predator, lasers
│   ├── game.py               # Game session: rules, collisions, scoring and drawing
│   ├── timing.py             # Fixed-step timer (frame-rate independent gameplay)
│   └── ui.py                 # Main menu, instructions, HUD and game over screens
├── tests/                    # Automated tests (unittest)
│   ├── helpers.py
│   ├── test_game.py
│   ├── test_resources.py
│   └── test_timing.py
├── tools/
│   └── generate_music.py     # Generates the background music
├── assets/                   # Images (.png), sound effects and music (.wav)
├── requirements.txt
└── README.md
```

## Technical notes

- **Frame-rate independent timing:** the game logic advances in fixed steps of 1/60 s. On a machine that keeps up with 60 FPS, this is exactly one update per frame, as in the original version; on slower machines, several steps are run per frame so the game speed stays the same instead of slowing down.
- **Resource caching:** images are loaded once and converted to the display format; fonts are created once and texts are only re-rendered when their content changes.
- **Sprites:** game entities use `pygame.sprite.Sprite` and `pygame.sprite.Group` for updating, drawing and collision detection.
- **Error handling:** if no audio device is available, the game runs without sound; missing or unreadable sound files are skipped with a warning; missing images or an unavailable display stop the game with a clear message and exit code 1.

## Music and sound

The background music is an original chiptune track synthesized by [`tools/generate_music.py`](tools/generate_music.py) using only the Python standard library. To regenerate `assets/background_music.wav`:

```bash
python tools/generate_music.py
```

Sound effects: thanks to the sound creators on YouTube.
