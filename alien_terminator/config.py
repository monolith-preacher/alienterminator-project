# -*- coding: utf-8 -*-
"""Constantes do jogo: tela, tempo, jogabilidade, áudio e caminhos dos recursos.

Os valores de movimento estão em pixels por passo de simulação (1/60 s),
exatamente como no jogo original, que movia tudo uma vez por frame a 60 FPS.
"""
from pathlib import Path

TITLE = "Alien Terminator"

# Tela
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Tempo: a lógica avança em passos fixos de 1/60 s, independente do FPS real
FPS = 60
STEP_SECONDS = 1 / FPS
MAX_STEPS_PER_FRAME = 5  # acima disso o jogo desacelera em vez de "teleportar"

# Cores
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Jogador
PLAYER_SPEED = 7
PLAYER_START_MIDBOTTOM = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20)

# Tiro normal
BULLET_SIZE = (4, 10)
BULLET_SPEED = 10

# Tiro especial: 5 direções; cada projétil atravessa até 4 aliens
POWER_KILLS_REQUIRED = 15
SPECIAL_USES = 3
SPECIAL_COOLDOWN_STEPS = round(0.5 * FPS)  # 0.5 s entre tiros especiais
SPECIAL_ANGLES = (-30, -15, 0, 15, 30)
SPECIAL_SPEED = 10
SPECIAL_PIERCE = 4

# Aliens e meteoros
ALIEN_WAVE_SIZE = 10
ALIEN_SPEED = 5
ALIEN_SCORE = 10
METEORITE_COUNT = 5
METEORITE_SPEED = 5
ALIEN_SPAWN_MAX_X = SCREEN_WIDTH - 40
METEORITE_SPAWN_MAX_X = SCREEN_WIDTH - 60
SPAWN_Y_RANGE = (-1000, -40)  # nascem acima da tela, em alturas aleatórias

# Predator (chefe)
PREDATOR_HEALTH = 5
PREDATOR_SPEED = 5
PREDATOR_START_MIDTOP = (SCREEN_WIDTH, 50)
PREDATOR_FIRST_APPEARANCE = 100  # pontos
PREDATOR_APPEARANCE_INTERVAL = 200  # pontos entre aparições
PREDATOR_LASER_CHANCE = 0.02  # probabilidade por passo, para cada tipo de laser
PREDATOR_LASER_SPEED = 8
PREDATOR_LASER2_SPEED = 6
PREDATOR_LASER2_OFFSET_X = -20
HEART_SPACING = 30

# Áudio
SHOOT_VOLUME = 0.1
DAMAGE_VOLUME = 0.1
SPECIAL_SHOT_VOLUME = 0.3
MUSIC_VOLUME = 0.1

# Recursos
ASSETS_DIR = Path(__file__).resolve().parent.parent / 'assets'

IMAGE_FILES = {
    'player': 'player.png',
    'background': 'background.png',
    'alien': 'alien.png',
    'meteorite': 'meteorite.png',
    'predator': 'predator.png',
    'predator_laser': 'predator_laser.png',
    'predator_laser2': 'predator_laser2.png',
    'heart': 'heart.png',
}

SOUND_FILES = {
    'shoot': ('shoot.wav', SHOOT_VOLUME),
    'damage': ('damage.wav', DAMAGE_VOLUME),
    'special_shot': ('special_shot.wav', SPECIAL_SHOT_VOLUME),
}

MUSIC_FILE = 'background_music.wav'
