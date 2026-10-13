# -*- coding: utf-8 -*-
"""Sons e música, tolerantes à ausência de dispositivo de áudio ou de arquivos.

Se o mixer não puder ser iniciado (por exemplo, sem PulseAudio no WSL), ou se
um arquivo estiver ausente, um aviso é registrado e o jogo continua sem aquele som.
"""
import logging

import pygame

from . import config

log = logging.getLogger(__name__)


class Audio:
    def __init__(self, assets_dir=config.ASSETS_DIR):
        self.enabled = self._init_mixer()
        self._sounds = {}
        self._music_loaded = False
        if self.enabled:
            self._load_sounds(assets_dir)
            self._music_loaded = self._load_music(assets_dir / config.MUSIC_FILE)

    @staticmethod
    def _init_mixer():
        # pygame.init() já tenta iniciar o mixer; só tentamos de novo se falhou
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            return True
        except (pygame.error, NotImplementedError) as exc:
            log.warning('Áudio indisponível (%s). O jogo continuará sem som.', exc)
            return False

    def _load_sounds(self, assets_dir):
        for name, (filename, volume) in config.SOUND_FILES.items():
            path = assets_dir / filename
            try:
                sound = pygame.mixer.Sound(str(path))
            except (pygame.error, FileNotFoundError) as exc:
                log.warning('Efeito sonoro "%s" não carregado (%s): %s', name, path, exc)
                continue
            sound.set_volume(volume)
            self._sounds[name] = sound

    @staticmethod
    def _load_music(path):
        try:
            pygame.mixer.music.load(str(path))
        except (pygame.error, FileNotFoundError) as exc:
            log.warning('Música de fundo não carregada (%s): %s', path, exc)
            return False
        return True

    def play(self, name):
        sound = self._sounds.get(name)
        if sound is not None:
            sound.play()

    def play_music(self):
        """Toca a música de fundo em loop, sempre a partir do início."""
        if self._music_loaded:
            pygame.mixer.music.set_volume(config.MUSIC_VOLUME)
            pygame.mixer.music.play(-1)

    def stop_music(self):
        if self._music_loaded:
            pygame.mixer.music.stop()
