# -*- coding: utf-8 -*-
"""Estado e regras de uma partida.

``GameSession`` não lida com janela, eventos ou relógio: recebe comandos
(``fire``, ``fire_special``) e avança um passo fixo por ``update``. Isso
permite testar as regras sem interface gráfica.
"""
import random

import pygame

from . import config
from .entities import Bullet, FallingObject, Laser, Player, Predator, SpecialBullet


class GameSession:
    def __init__(self, images, audio, rng=None):
        self.images = images
        self.audio = audio
        self.rng = rng or random.Random()

        self.player = Player(images.player)
        self.bullets = pygame.sprite.Group()
        self.special_bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.meteorites = pygame.sprite.Group()
        self.predator = None
        self.predator_lasers = pygame.sprite.Group()
        self.predator_lasers2 = pygame.sprite.Group()

        self.score = 0
        self.power_kills = 0  # kills acumulados para recarregar o poder especial
        self.total_kills = 0
        self.predator_kills = 0
        self.power_ready = False
        self.special_uses = config.SPECIAL_USES
        self.next_predator_appearance = config.PREDATOR_FIRST_APPEARANCE
        self.game_over = False

        self.steps = 0
        self._last_special_step = -config.SPECIAL_COOLDOWN_STEPS

        self._spawn_alien_wave()
        for _ in range(config.METEORITE_COUNT):
            self.meteorites.add(FallingObject(images.meteorite, config.METEORITE_SPEED,
                                              config.METEORITE_SPAWN_MAX_X, self.rng))

    def _spawn_alien_wave(self):
        for _ in range(config.ALIEN_WAVE_SIZE):
            self.aliens.add(FallingObject(self.images.alien, config.ALIEN_SPEED,
                                          config.ALIEN_SPAWN_MAX_X, self.rng))

    # Comandos do jogador -------------------------------------------------

    def fire(self):
        if self.game_over:
            return
        self.bullets.add(Bullet(self.player.rect))
        self.audio.play('shoot')

    def fire_special(self):
        """Dispara o tiro especial; só consome um uso se o tiro realmente sair."""
        if self.game_over or not self.power_ready or self.special_uses <= 0:
            return False
        if self.steps - self._last_special_step < config.SPECIAL_COOLDOWN_STEPS:
            return False
        for angle in config.SPECIAL_ANGLES:
            self.special_bullets.add(SpecialBullet(self.player.rect, angle))
        self.audio.play('special_shot')
        self._last_special_step = self.steps
        self.special_uses -= 1
        if self.special_uses == 0:
            self.power_ready = False
        return True

    # Simulação -------------------------------------------------------------

    def update(self, left=False, right=False):
        """Avança a partida em um passo fixo de simulação."""
        if self.game_over:
            return
        self.steps += 1
        self.player.move(left, right)

        self.bullets.update()
        self.special_bullets.update()
        self.aliens.update()
        self.meteorites.update()

        # Predator aparece aos 100 pontos e depois a cada 200 pontos
        if self.predator is None and self.score >= self.next_predator_appearance:
            self.predator = Predator(self.images.predator)
            self.next_predator_appearance += config.PREDATOR_APPEARANCE_INTERVAL

        if self.predator is not None:
            self._update_predator()
        elif not self.aliens:
            # Novas ondas só chegam quando não há chefe em campo
            self._spawn_alien_wave()

        # O excedente de kills continua contando enquanto o poder está carregado
        if self.power_kills >= config.POWER_KILLS_REQUIRED and not self.power_ready:
            self.power_ready = True
            self.special_uses = config.SPECIAL_USES
            self.power_kills -= config.POWER_KILLS_REQUIRED

        self._check_collisions()

    def _update_predator(self):
        predator = self.predator
        predator.update()
        if predator.rect.top > 0 and self.rng.random() < config.PREDATOR_LASER_CHANCE:
            self.predator_lasers.add(Laser(self.images.predator_laser,
                                           (predator.rect.centerx, predator.rect.bottom),
                                           config.PREDATOR_LASER_SPEED))
        if predator.rect.top > 0 and self.rng.random() < config.PREDATOR_LASER_CHANCE:
            self.predator_lasers2.add(Laser(self.images.predator_laser2,
                                            (predator.rect.centerx + config.PREDATOR_LASER2_OFFSET_X,
                                             predator.rect.bottom),
                                            config.PREDATOR_LASER2_SPEED))
        self.predator_lasers.update()
        self.predator_lasers2.update()

    def _register_alien_kill(self):
        self.score += config.ALIEN_SCORE
        self.power_kills += 1
        self.total_kills += 1
        self.audio.play('damage')

    def _check_collisions(self):
        # Cada tiro normal elimina no máximo um alien (o primeiro da onda que tocar)
        for bullet in self.bullets.sprites():
            alien = pygame.sprite.spritecollideany(bullet, self.aliens)
            if alien is not None:
                alien.kill()
                bullet.kill()
                self._register_alien_kill()

        # Tiros especiais atravessam até ``pierce`` aliens
        for special in self.special_bullets.sprites():
            for alien in pygame.sprite.spritecollide(special, self.aliens, False):
                alien.kill()
                self._register_alien_kill()
                special.pierce -= 1
                if special.pierce == 0:
                    special.kill()
                    break

        if self._player_hit():
            self.audio.play('damage')
            self.game_over = True
            return

        # Tiros normais ferem o Predator; no máximo um acerto por passo
        if self.predator is not None:
            for bullet in self.bullets.sprites():
                if bullet.rect.colliderect(self.predator.rect):
                    bullet.kill()
                    self.predator.health -= 1
                    self.audio.play('damage')
                    if self.predator.health <= 0:
                        self._defeat_predator()
                    break

    def _player_hit(self):
        player = self.player
        return bool(
            pygame.sprite.spritecollideany(player, self.aliens)
            or pygame.sprite.spritecollideany(player, self.meteorites)
            or pygame.sprite.spritecollideany(player, self.predator_lasers)
            or pygame.sprite.spritecollideany(player, self.predator_lasers2)
            or (self.predator is not None and self.predator.rect.colliderect(player.rect))
        )

    def _defeat_predator(self):
        self.predator_kills += 1
        self.predator = None
        # Sem o Predator os lasers deixariam de se mover, mas continuariam colidindo
        self.predator_lasers.empty()
        self.predator_lasers2.empty()

    # Desenho -----------------------------------------------------------------

    def draw(self, surface):
        """Desenha o mundo do jogo, na mesma ordem de camadas do original."""
        surface.blit(self.images.background, (0, 0))
        self.special_bullets.draw(surface)
        if self.predator is not None:
            surface.blit(self.predator.image, self.predator.rect)
            heart = self.images.heart
            for i in range(self.predator.health):
                surface.blit(heart, (config.SCREEN_WIDTH - 150 + i * config.HEART_SPACING, 10))
            self.predator_lasers.draw(surface)
            self.predator_lasers2.draw(surface)
        surface.blit(self.player.image, self.player.rect)
        self.bullets.draw(surface)
        self.aliens.draw(surface)
        self.meteorites.draw(surface)
