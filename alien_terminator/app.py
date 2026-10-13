# -*- coding: utf-8 -*-
"""Inicialização, laço principal e navegação entre menu, instruções e partida."""
import logging
import sys

import pygame

from . import config
from .assets import AssetError, load_images
from .audio import Audio
from .game import GameSession
from .timing import FixedStepTimer
from .ui import Fonts, GameOverScreen, Hud, InstructionsScreen, MainMenu

log = logging.getLogger(__name__)


class QuitRequested(Exception):
    """A janela foi fechada: encerra o jogo de qualquer tela."""


class App:
    def __init__(self):
        pygame.init()
        try:
            self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        except pygame.error as exc:
            raise RuntimeError(
                f'Não foi possível abrir a janela do jogo ({exc}). '
                'No WSL, verifique se o WSLg está ativo (variáveis DISPLAY/WAYLAND_DISPLAY).'
            ) from exc
        pygame.display.set_caption(config.TITLE)

        self.clock = pygame.time.Clock()
        self.images = load_images()
        self.audio = Audio()
        self.fonts = Fonts()
        self.menu = MainMenu(self.fonts)
        self.instructions = InstructionsScreen(self.fonts)

    def run(self):
        try:
            self._main_menu()
        except QuitRequested:
            pass

    def _events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise QuitRequested
            yield event

    def _present(self):
        pygame.display.flip()
        return self.clock.tick(config.FPS) / 1000

    def _main_menu(self):
        menu = self.menu
        while True:
            for event in self._events():
                if event.type != pygame.KEYDOWN:
                    continue
                if event.key == pygame.K_RETURN:
                    if menu.selected == 'play':
                        self._play()
                    elif menu.selected == 'instructions':
                        self._show_instructions()
                    elif menu.selected == 'quit':
                        return
                elif event.key == pygame.K_DOWN:
                    menu.move(1)
                elif event.key == pygame.K_UP:
                    menu.move(-1)
                elif event.key == pygame.K_i:
                    menu.select('instructions')
                elif event.key == pygame.K_ESCAPE:
                    return

            menu.draw(self.screen)
            self._present()

    def _show_instructions(self):
        while True:
            for event in self._events():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return
            self.instructions.draw(self.screen)
            self._present()

    def _play(self):
        session = GameSession(self.images, self.audio)
        hud = Hud(self.fonts)
        timer = FixedStepTimer()
        game_over_screen = None
        self.audio.play_music()
        self.clock.tick()  # descarta o tempo gasto no menu
        try:
            elapsed = 0.0
            while True:
                for event in self._events():
                    if event.type != pygame.KEYDOWN:
                        continue
                    if event.key == pygame.K_ESCAPE:
                        return
                    if event.key == pygame.K_SPACE:
                        session.fire()
                    elif event.key == pygame.K_b:
                        session.fire_special()

                keys = pygame.key.get_pressed()
                for _ in range(timer.advance(elapsed)):
                    session.update(keys[pygame.K_LEFT], keys[pygame.K_RIGHT])
                    if session.game_over:
                        break

                if session.game_over:
                    if game_over_screen is None:
                        self.audio.stop_music()
                        game_over_screen = GameOverScreen(self.fonts, self.images.background, session)
                    game_over_screen.draw(self.screen)
                else:
                    session.draw(self.screen)
                    hud.draw(self.screen, session)
                elapsed = self._present()
        finally:
            # Sair com ESC no meio da partida também silencia a música
            self.audio.stop_music()


def main():
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
    try:
        app = App()
    except (AssetError, RuntimeError) as exc:
        log.error('%s', exc)
        pygame.quit()
        return 1
    try:
        app.run()
    finally:
        pygame.quit()
    return 0


if __name__ == '__main__':
    sys.exit(main())
