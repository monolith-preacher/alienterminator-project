# -*- coding: utf-8 -*-
"""Passo fixo de simulação, independente da taxa de quadros real."""
from . import config


class FixedStepTimer:
    """Converte o tempo decorrido entre frames em um número de passos de 1/60 s.

    Com o jogo rodando normalmente, cada frame resulta em exatamente um passo,
    reproduzindo o comportamento original. ``Clock.tick`` oscila alguns
    milissegundos (16 ms, 17 ms...); essas variações são "encaixadas" no
    múltiplo de passo mais próximo para não gerar frames sem atualização ou
    com atualização dupla. Se a máquina não acompanhar 60 FPS, são executados
    vários passos por frame para manter a velocidade do jogo, limitados a
    ``max_steps`` para evitar saltos grandes após travamentos.
    """

    SNAP_TOLERANCE = 0.002  # segundos

    def __init__(self, step=config.STEP_SECONDS, max_steps=config.MAX_STEPS_PER_FRAME):
        self.step = step
        self.max_steps = max_steps
        self._accumulator = 0.0

    def advance(self, elapsed):
        """Recebe o tempo do frame (segundos) e devolve quantos passos simular."""
        elapsed = min(max(elapsed, 0.0), self.step * self.max_steps)
        nearest = round(elapsed / self.step)
        if abs(elapsed - nearest * self.step) < self.SNAP_TOLERANCE:
            elapsed = nearest * self.step

        self._accumulator += elapsed
        # Pequena folga contra erros de ponto flutuante na comparação
        steps = int(self._accumulator / self.step + 1e-9)
        self._accumulator = max(self._accumulator - steps * self.step, 0.0)
        return steps
