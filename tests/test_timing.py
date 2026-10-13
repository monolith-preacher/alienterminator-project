# -*- coding: utf-8 -*-
"""Passo fixo de simulação."""
import unittest

from alien_terminator import config
from alien_terminator.timing import FixedStepTimer


class FixedStepTimerTest(unittest.TestCase):
    def test_normal_clock_jitter_gives_one_step_per_frame(self):
        # Clock.tick(60) devolve 16 ou 17 ms: cada frame deve virar exatamente 1 passo
        timer = FixedStepTimer()
        steps = [timer.advance(ms / 1000) for ms in [16, 17, 17, 16, 17, 16, 16, 17] * 50]
        self.assertEqual(set(steps), {1})

    def test_slow_machine_keeps_game_speed(self):
        # A 30 FPS cada frame precisa avançar 2 passos para manter a velocidade
        timer = FixedStepTimer()
        steps = [timer.advance(ms / 1000) for ms in [33, 34] * 30]
        self.assertEqual(set(steps), {2})

    def test_irregular_frames_preserve_total_time(self):
        timer = FixedStepTimer()
        frames = [0.025] * 120  # 40 FPS durante 3 segundos
        total = sum(timer.advance(dt) for dt in frames)
        self.assertAlmostEqual(total, 3 * config.FPS, delta=1)

    def test_long_pause_is_capped(self):
        timer = FixedStepTimer()
        self.assertEqual(timer.advance(5.0), config.MAX_STEPS_PER_FRAME)
        self.assertEqual(timer.advance(1 / config.FPS), 1)  # sem "dívida" acumulada

    def test_zero_or_negative_elapsed(self):
        timer = FixedStepTimer()
        self.assertEqual(timer.advance(0.0), 0)
        self.assertEqual(timer.advance(-1.0), 0)


if __name__ == '__main__':
    unittest.main()
