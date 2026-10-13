# -*- coding: utf-8 -*-
"""Entidades do jogo como sprites do Pygame.

Cada ``update()`` corresponde a um passo de simulação (1/60 s). As posições
ficam em ``pygame.Rect`` (inteiros), como no original, para manter idênticos
os deslocamentos e as colisões.
"""
import math

import pygame

from . import config

_bullet_images = {}


def _solid_image(size, color):
    """Superfície de cor sólida compartilhada entre todos os projéteis iguais."""
    key = (size, color)
    if key not in _bullet_images:
        surface = pygame.Surface(size)
        surface.fill(color)
        _bullet_images[key] = surface
    return _bullet_images[key]


class Player(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = image.get_rect(midbottom=config.PLAYER_START_MIDBOTTOM)

    def move(self, left, right):
        if left and self.rect.left > 0:
            self.rect.x -= config.PLAYER_SPEED
        if right and self.rect.right < config.SCREEN_WIDTH:
            self.rect.x += config.PLAYER_SPEED


def _muzzle_rect(player_rect):
    """Retângulo de um projétil saindo do topo do jogador."""
    width, height = config.BULLET_SIZE
    return pygame.Rect(player_rect.centerx - 2, player_rect.top - 10, width, height)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, player_rect):
        super().__init__()
        self.image = _solid_image(config.BULLET_SIZE, config.RED)
        self.rect = _muzzle_rect(player_rect)

    def update(self):
        self.rect.y -= config.BULLET_SPEED
        if self.rect.bottom < 0:
            self.kill()


class SpecialBullet(pygame.sprite.Sprite):
    """Projétil do tiro especial.

    O original empilhava 4 projéteis idênticos por direção; cada um eliminava
    um alien. ``pierce`` representa essa pilha: quantos aliens ainda pode atingir.
    """

    def __init__(self, player_rect, angle):
        super().__init__()
        self.image = _solid_image(config.BULLET_SIZE, config.GREEN)
        self.rect = _muzzle_rect(player_rect)
        radians = math.radians(angle)
        self.velocity = pygame.Vector2(config.SPECIAL_SPEED * math.sin(radians),
                                       -config.SPECIAL_SPEED * math.cos(radians))
        self.pierce = config.SPECIAL_PIERCE

    def update(self):
        # Rect arredonda a velocidade fracionária, como no jogo original
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y
        if self.rect.right < 0 or self.rect.left > config.SCREEN_WIDTH or self.rect.bottom < 0:
            self.kill()


class FallingObject(pygame.sprite.Sprite):
    """Alien ou meteoro: desce e, ao sair por baixo, volta acima da tela."""

    def __init__(self, image, speed, max_x, rng):
        super().__init__()
        self.image = image
        self.speed = speed
        self.max_x = max_x
        self.rng = rng
        self.rect = image.get_rect(topleft=(rng.randint(0, max_x), rng.randint(*config.SPAWN_Y_RANGE)))

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > config.SCREEN_HEIGHT:
            self.rect.y = self.rng.randint(*config.SPAWN_Y_RANGE)
            self.rect.x = self.rng.randint(0, self.max_x)


class Predator(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = image.get_rect(midtop=config.PREDATOR_START_MIDTOP)
        self.health = config.PREDATOR_HEALTH

    def update(self):
        self.rect.x -= config.PREDATOR_SPEED
        if self.rect.right < 0:  # saiu pela esquerda: reaparece na direita
            self.rect.left = config.SCREEN_WIDTH


class Laser(pygame.sprite.Sprite):
    def __init__(self, image, midtop, speed):
        super().__init__()
        self.image = image
        self.rect = image.get_rect(midtop=midtop)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > config.SCREEN_HEIGHT:
            self.kill()
