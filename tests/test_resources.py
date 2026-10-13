# -*- coding: utf-8 -*-
"""Integridade dos recursos, tolerância a falhas de áudio e telas."""
import shutil
import tempfile
import unittest
import wave
from pathlib import Path
from unittest import mock

import helpers  # noqa: F401  (configura o Pygame sem janela/áudio)
import pygame

from alien_terminator import config
from alien_terminator.assets import AssetError, load_images
from alien_terminator.audio import Audio
from alien_terminator.ui import CachedText, Fonts, GameOverScreen, Hud, InstructionsScreen, MainMenu


class AssetFilesTest(unittest.TestCase):
    def test_all_images_load(self):
        images = helpers.images()
        for name in config.IMAGE_FILES:
            self.assertGreater(getattr(images, name).get_width(), 0, name)
        self.assertEqual(images.background.get_size(), (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))

    def test_all_audio_files_are_valid_wav(self):
        files = [filename for filename, _ in config.SOUND_FILES.values()] + [config.MUSIC_FILE]
        for filename in files:
            with wave.open(str(config.ASSETS_DIR / filename)) as wav:
                self.assertGreater(wav.getnframes(), 0, filename)

    def test_missing_images_are_all_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            for filename in config.IMAGE_FILES.values():
                shutil.copy(config.ASSETS_DIR / filename, tmp)
            (Path(tmp) / 'alien.png').unlink()
            (Path(tmp) / 'heart.png').unlink()
            with self.assertRaises(AssetError) as ctx:
                load_images(Path(tmp), convert=False)
        message = str(ctx.exception)
        self.assertIn('alien.png', message)
        self.assertIn('heart.png', message)


class AudioFallbackTest(unittest.TestCase):
    def test_game_continues_without_audio_device(self):
        with mock.patch('pygame.mixer.get_init', return_value=None), \
                mock.patch('pygame.mixer.init', side_effect=pygame.error('no device')), \
                self.assertLogs('alien_terminator.audio', 'WARNING'):
            audio = Audio()
        self.assertFalse(audio.enabled)
        audio.play('shoot')
        audio.play_music()
        audio.stop_music()

    def test_missing_sound_files_are_skipped(self):
        pygame.mixer.init()
        with tempfile.TemporaryDirectory() as tmp, self.assertLogs('alien_terminator.audio', 'WARNING'):
            audio = Audio(Path(tmp))
        self.assertTrue(audio.enabled)
        audio.play('shoot')
        audio.play_music()
        audio.stop_music()

    def test_sounds_load_with_configured_volumes(self):
        pygame.mixer.init()
        audio = Audio()
        for name, (_, volume) in config.SOUND_FILES.items():
            self.assertAlmostEqual(audio._sounds[name].get_volume(), volume, places=1)


class UiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.font.init()
        cls.fonts = Fonts()
        cls.surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))

    def test_cached_text_renders_only_on_change(self):
        text = CachedText(self.fonts.hud, config.WHITE)
        first = text.render('Score: 10')
        self.assertIs(text.render('Score: 10'), first)
        self.assertIsNot(text.render('Score: 20'), first)

    def test_menu_navigation_wraps_around(self):
        menu = MainMenu(self.fonts)
        self.assertEqual(menu.selected, 'play')
        menu.move(-1)
        self.assertEqual(menu.selected, 'quit')
        menu.move(1)
        menu.move(1)
        self.assertEqual(menu.selected, 'instructions')
        menu.select('quit')
        self.assertEqual(menu.selected, 'quit')

    def test_screens_draw_without_errors(self):
        session = helpers.new_session()
        session.power_ready = True
        MainMenu(self.fonts).draw(self.surface)
        InstructionsScreen(self.fonts).draw(self.surface)
        session.draw(self.surface)
        Hud(self.fonts).draw(self.surface, session)
        GameOverScreen(self.fonts, helpers.images().background, session).draw(self.surface)


if __name__ == '__main__':
    unittest.main()
