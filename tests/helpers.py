# -*- coding: utf-8 -*-
"""Utilitários dos testes: Pygame sem janela e sem dispositivo de áudio."""
import os

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')

import random  # noqa: E402

import pygame  # noqa: E402

from alien_terminator.assets import load_images  # noqa: E402
from alien_terminator.game import GameSession  # noqa: E402

_images = None


def images():
    """Imagens reais do jogo, carregadas uma vez (sem conversão: não há janela)."""
    global _images
    if _images is None:
        pygame.init()
        _images = load_images(convert=False)
    return _images


class SilentAudio:
    """Registra os sons pedidos em vez de tocá-los."""

    def __init__(self):
        self.played = []

    def play(self, name):
        self.played.append(name)


def new_session(seed=0):
    return GameSession(images(), SilentAudio(), rng=random.Random(seed))


def clear_field(session):
    """Remove aliens e meteoros para montar cenários controlados."""
    session.aliens.empty()
    session.meteorites.empty()
