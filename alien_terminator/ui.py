# -*- coding: utf-8 -*-
"""Telas e textos. Fontes são criadas uma vez e textos só são renderizados quando mudam."""
import pygame

from . import config

CENTER_X = config.SCREEN_WIDTH // 2
CENTER_Y = config.SCREEN_HEIGHT // 2

MENU_OPTIONS = (('play', 'Start'), ('instructions', 'Instructions'), ('quit', 'Quit'))

INSTRUCTION_LINES = (
    'Use the arrow keys to move the player.',
    'Use SPACEBAR to shoot.',
    'Destroy as many aliens as you can.',
    'Meteorites are not destructible, avoid them.',
    'Be careful with the predator.',
    'Press ESC to return to main menu.',
)


class Fonts:
    def __init__(self):
        self.hud = pygame.font.Font(None, 24)
        self.body = pygame.font.Font(None, 36)
        self.large = pygame.font.Font(None, 48)
        self.title = pygame.font.Font(None, 74)


class CachedText:
    """Texto que só é renderizado de novo quando o conteúdo muda."""

    def __init__(self, font, color):
        self.font = font
        self.color = color
        self._text = None
        self.surface = None

    def render(self, text):
        if text != self._text:
            self._text = text
            self.surface = self.font.render(text, True, self.color)
        return self.surface


def blit_centered(surface, text_surface, y):
    surface.blit(text_surface, (CENTER_X - text_surface.get_width() // 2, y))


class MainMenu:
    def __init__(self, fonts):
        self.title = fonts.title.render('ALIEN TERMINATOR', True, config.WHITE)
        self.items = [(key, fonts.large.render(label, True, config.WHITE)) for key, label in MENU_OPTIONS]
        self.index = 0

    @property
    def selected(self):
        return self.items[self.index][0]

    def move(self, delta):
        self.index = (self.index + delta) % len(self.items)

    def select(self, key):
        self.index = next(i for i, (item_key, _) in enumerate(self.items) if item_key == key)

    def draw(self, surface):
        surface.fill(config.BLACK)
        blit_centered(surface, self.title, CENTER_Y - 100)
        for i, (_, text) in enumerate(self.items):
            y = CENTER_Y + i * 50
            blit_centered(surface, text, y)
            if i == self.index:
                width, height = text.get_size()
                pygame.draw.rect(surface, config.WHITE,
                                 (CENTER_X - width // 2 - 10, y - 10, width + 20, height + 20), 2)


class InstructionsScreen:
    def __init__(self, fonts):
        # A tela é estática: é montada uma única vez
        self.surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.surface.fill(config.BLACK)
        blit_centered(self.surface, fonts.title.render('INSTRUÇÕES', True, config.WHITE), CENTER_Y - 200)
        for i, line in enumerate(INSTRUCTION_LINES):
            blit_centered(self.surface, fonts.body.render(line, True, config.WHITE), CENTER_Y - 100 + i * 40)

    def draw(self, surface):
        surface.blit(self.surface, (0, 0))


class Hud:
    def __init__(self, fonts):
        self.lines = [CachedText(fonts.hud, config.WHITE) for _ in range(4)]
        self.power = CachedText(fonts.hud, config.GREEN)

    def draw(self, surface, session):
        texts = (
            f'Score: {session.score}',
            f'Power({config.POWER_KILLS_REQUIRED}): {session.power_kills}',
            f'Total Kills: {session.total_kills}',
            f'Predator Kills: {session.predator_kills}',
        )
        for i, (line, text) in enumerate(zip(self.lines, texts)):
            surface.blit(line.render(text), (10, 10 + i * 40))

        if session.power_ready:
            power = self.power.render(f'Power ready - Press B ({session.special_uses} left)')
            surface.blit(power, (config.SCREEN_WIDTH - power.get_width() - 10,
                                 config.SCREEN_HEIGHT - power.get_height() - 10))


class GameOverScreen:
    def __init__(self, fonts, background, session):
        # Os valores finais não mudam mais: a tela é montada uma única vez
        font = fonts.large
        self.surface = background.copy()
        lines = (
            ('GAME OVER', config.RED, -100),
            (f'Final Score: {session.score}', config.WHITE, 10),
            (f'Total Kills: {session.total_kills}', config.WHITE, 70),
            (f'Predator Kills: {session.predator_kills}', config.WHITE, 130),
            ('Press ESC to return to the main menu', config.WHITE, 190),
        )
        for text, color, offset in lines:
            blit_centered(self.surface, font.render(text, True, color), CENTER_Y + offset)

    def draw(self, surface):
        surface.blit(self.surface, (0, 0))
