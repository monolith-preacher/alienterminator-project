# -*- coding: utf-8 -*-
"""Regras da partida, testadas sem interface gráfica."""
import unittest

from helpers import clear_field, images, new_session

from alien_terminator import config
from alien_terminator.entities import FallingObject, Laser, Predator


def add_alien(session, topleft):
    alien = FallingObject(images().alien, 0, config.ALIEN_SPAWN_MAX_X, session.rng)
    alien.rect.topleft = topleft
    session.aliens.add(alien)
    return alien


def add_meteorite_away(session):
    """Garante que o campo não fique vazio sem afetar o jogador."""
    meteorite = FallingObject(images().meteorite, 0, config.METEORITE_SPAWN_MAX_X, session.rng)
    meteorite.rect.topleft = (0, -500)
    session.meteorites.add(meteorite)


class InitialStateTest(unittest.TestCase):
    def test_new_session_starts_clean(self):
        session = new_session()
        self.assertEqual(len(session.aliens), config.ALIEN_WAVE_SIZE)
        self.assertEqual(len(session.meteorites), config.METEORITE_COUNT)
        self.assertEqual(session.player.rect.midbottom, config.PLAYER_START_MIDBOTTOM)
        self.assertEqual((session.score, session.total_kills, session.predator_kills), (0, 0, 0))
        self.assertIsNone(session.predator)
        self.assertFalse(session.game_over)

    def test_each_session_resets_player_position(self):
        first = new_session()
        clear_field(first)
        for _ in range(20):
            first.update(left=True)
        second = new_session()
        self.assertEqual(second.player.rect.midbottom, config.PLAYER_START_MIDBOTTOM)

    def test_enemies_spawn_above_screen_within_bounds(self):
        session = new_session(seed=42)
        for alien in session.aliens:
            self.assertLessEqual(alien.rect.bottom, 0)
            self.assertTrue(0 <= alien.rect.x <= config.ALIEN_SPAWN_MAX_X)
        for meteorite in session.meteorites:
            self.assertTrue(0 <= meteorite.rect.x <= config.METEORITE_SPAWN_MAX_X)


class PlayerTest(unittest.TestCase):
    def test_moves_by_fixed_speed(self):
        session = new_session()
        clear_field(session)
        x = session.player.rect.x
        session.update(right=True)
        self.assertEqual(session.player.rect.x, x + config.PLAYER_SPEED)
        session.update(left=True)
        self.assertEqual(session.player.rect.x, x)

    def test_cannot_leave_screen(self):
        session = new_session()
        clear_field(session)
        for _ in range(200):
            session.update(left=True)
        self.assertGreaterEqual(session.player.rect.left, -config.PLAYER_SPEED)
        self.assertLessEqual(session.player.rect.left, 0)
        for _ in range(200):
            session.update(right=True)
        self.assertLessEqual(session.player.rect.right, config.SCREEN_WIDTH + config.PLAYER_SPEED)


class ShootingTest(unittest.TestCase):
    def test_bullet_kills_alien_and_scores(self):
        session = new_session()
        clear_field(session)
        add_meteorite_away(session)
        player = session.player.rect
        alien = add_alien(session, (player.centerx - 14, player.top - 60))
        session.fire()
        for _ in range(10):
            session.update()
        self.assertFalse(alien.alive())
        self.assertEqual(len(session.bullets), 0)
        self.assertEqual((session.score, session.power_kills, session.total_kills), (10, 1, 1))
        self.assertEqual(session.audio.played, ['shoot', 'damage'])

    def test_bullet_kills_only_one_of_overlapping_aliens(self):
        session = new_session()
        clear_field(session)
        add_meteorite_away(session)
        player = session.player.rect
        first = add_alien(session, (player.centerx - 14, player.top - 60))
        second = add_alien(session, (player.centerx - 14, player.top - 60))
        session.fire()
        for _ in range(4):
            session.update()
        self.assertFalse(first.alive())
        self.assertTrue(second.alive())
        self.assertEqual(session.total_kills, 1)

    def test_bullets_disappear_above_screen(self):
        session = new_session()
        clear_field(session)
        session.fire()
        for _ in range(70):
            session.update()
        self.assertEqual(len(session.bullets), 0)

    def test_cannot_fire_after_game_over(self):
        session = new_session()
        session.game_over = True
        session.fire()
        self.assertEqual(len(session.bullets), 0)


class SpecialShotTest(unittest.TestCase):
    def charged_session(self):
        session = new_session()
        clear_field(session)
        session.power_kills = config.POWER_KILLS_REQUIRED
        session.update()
        return session

    def test_power_charges_after_required_kills(self):
        session = new_session()
        clear_field(session)
        session.power_kills = config.POWER_KILLS_REQUIRED + 2
        session.update()
        self.assertTrue(session.power_ready)
        self.assertEqual(session.special_uses, config.SPECIAL_USES)
        self.assertEqual(session.power_kills, 2)

    def test_unavailable_without_power(self):
        session = new_session()
        self.assertFalse(session.fire_special())
        self.assertEqual(len(session.special_bullets), 0)

    def test_fires_five_directions(self):
        session = self.charged_session()
        self.assertTrue(session.fire_special())
        self.assertEqual(len(session.special_bullets), len(config.SPECIAL_ANGLES))
        self.assertEqual(session.special_uses, config.SPECIAL_USES - 1)
        self.assertIn('special_shot', session.audio.played)

    def test_spread_is_symmetric(self):
        session = self.charged_session()
        session.fire_special()
        start = session.player.rect.centerx - 2
        for _ in range(10):
            session.update()
        offsets = sorted(bullet.rect.x - start for bullet in session.special_bullets)
        self.assertEqual(offsets, [-o for o in reversed(offsets)])

    def test_cooldown_does_not_consume_uses(self):
        session = self.charged_session()
        self.assertTrue(session.fire_special())
        self.assertFalse(session.fire_special())
        self.assertEqual(session.special_uses, config.SPECIAL_USES - 1)
        for _ in range(config.SPECIAL_COOLDOWN_STEPS):
            session.update()
        self.assertTrue(session.fire_special())

    def test_power_ends_after_last_use(self):
        session = self.charged_session()
        for _ in range(config.SPECIAL_USES):
            self.assertTrue(session.fire_special())
            for _ in range(config.SPECIAL_COOLDOWN_STEPS):
                session.update()
        self.assertEqual(session.special_uses, 0)
        self.assertFalse(session.power_ready)

    def test_each_direction_pierces_up_to_four_aliens(self):
        session = self.charged_session()
        add_meteorite_away(session)
        player = session.player.rect
        # Bem acima do jogador, onde só o projétil central (0°) passa
        stack = [add_alien(session, (player.centerx - 14, player.top - 250)) for _ in range(6)]
        session.fire_special()
        for _ in range(30):
            session.update()
        self.assertEqual(sum(not alien.alive() for alien in stack), config.SPECIAL_PIERCE)
        self.assertEqual(session.total_kills, config.SPECIAL_PIERCE)


class PredatorTest(unittest.TestCase):
    def session_with_predator(self):
        session = new_session()
        clear_field(session)
        add_meteorite_away(session)
        session.score = config.PREDATOR_FIRST_APPEARANCE
        session.update()
        return session

    def test_appears_at_threshold_and_schedules_next(self):
        session = self.session_with_predator()
        self.assertIsInstance(session.predator, Predator)
        self.assertEqual(session.next_predator_appearance,
                         config.PREDATOR_FIRST_APPEARANCE + config.PREDATOR_APPEARANCE_INTERVAL)

    def test_moves_left_and_wraps(self):
        session = self.session_with_predator()
        predator = session.predator
        predator.rect.right = 2
        session.predator_lasers.empty()
        predator.update()
        self.assertEqual(predator.rect.left, config.SCREEN_WIDTH)

    def test_no_new_alien_wave_while_predator_alive(self):
        session = self.session_with_predator()
        session.aliens.empty()
        session.update()
        self.assertEqual(len(session.aliens), 0)

    def test_new_wave_when_field_is_empty_without_predator(self):
        session = new_session()
        session.aliens.empty()
        session.update()
        self.assertEqual(len(session.aliens), config.ALIEN_WAVE_SIZE)

    def hit_predator_once(self, session, bullets=1):
        for _ in range(bullets):
            session.fire()
        for bullet in session.bullets:
            bullet.rect.center = session.predator.rect.center
        # Remove os lasers para que só os tiros sejam avaliados
        session.predator_lasers.empty()
        session.predator_lasers2.empty()
        session._check_collisions()

    def test_takes_at_most_one_hit_per_step(self):
        session = self.session_with_predator()
        self.hit_predator_once(session, bullets=3)
        self.assertEqual(session.predator.health, config.PREDATOR_HEALTH - 1)
        self.assertEqual(len(session.bullets), 2)

    def test_defeat_counts_and_clears_lasers(self):
        session = self.session_with_predator()
        session.predator_lasers.add(Laser(images().predator_laser, (100, 0), 0))
        for _ in range(config.PREDATOR_HEALTH):
            session.bullets.empty()
            self.hit_predator_once(session)
        self.assertIsNone(session.predator)
        self.assertEqual(session.predator_kills, 1)
        self.assertEqual(len(session.predator_lasers), 0)
        self.assertEqual(len(session.predator_lasers2), 0)

    def test_special_bullets_do_not_hurt_predator(self):
        session = self.session_with_predator()
        session.power_kills = config.POWER_KILLS_REQUIRED
        session.update()
        session.fire_special()
        for bullet in session.special_bullets:
            bullet.rect.center = session.predator.rect.center
        session.predator_lasers.empty()
        session.predator_lasers2.empty()
        session._check_collisions()
        self.assertEqual(session.predator.health, config.PREDATOR_HEALTH)


class GameOverTest(unittest.TestCase):
    def assert_collision_ends_game(self, sprite_group_name, image):
        session = new_session()
        clear_field(session)
        hazard = Laser(image, session.player.rect.midtop, 0)
        getattr(session, sprite_group_name).add(hazard)
        session.update()
        self.assertTrue(session.game_over)
        self.assertEqual(session.audio.played, ['damage'])

    def test_alien_touching_player(self):
        self.assert_collision_ends_game('aliens', images().alien)

    def test_meteorite_touching_player(self):
        self.assert_collision_ends_game('meteorites', images().meteorite)

    def test_laser_touching_player(self):
        self.assert_collision_ends_game('predator_lasers', images().predator_laser)
        self.assert_collision_ends_game('predator_lasers2', images().predator_laser2)

    def test_game_freezes_after_game_over(self):
        session = new_session()
        session.game_over = True
        positions = [tuple(alien.rect) for alien in session.aliens]
        session.update(right=True)
        self.assertEqual(positions, [tuple(alien.rect) for alien in session.aliens])
        self.assertEqual(session.steps, 0)


class FallingObjectTest(unittest.TestCase):
    def test_respawns_above_screen_after_leaving(self):
        session = new_session()
        alien = next(iter(session.aliens))
        alien.rect.top = config.SCREEN_HEIGHT - config.ALIEN_SPEED + 1
        alien.update()
        self.assertLess(alien.rect.top, 0)
        self.assertTrue(alien.alive())


if __name__ == '__main__':
    unittest.main()
