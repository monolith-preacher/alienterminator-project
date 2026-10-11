# -*- coding: utf-8 -*-
"""Gera a música de fundo do jogo (assets/background_music.wav).

Trilha chiptune original, sintetizada do zero só com a biblioteca padrão
(onda quadrada na melodia, triangular no baixo e ruído na bateria).
Por ser gerada por este script, não depende de nenhum material de terceiros.

Uso:
    python tools/generate_music.py
"""
import math
import random
import struct
import wave
from pathlib import Path

SAMPLE_RATE = 22050
BPM = 140
EIGHTH = 60 / BPM / 2  # duração de uma colcheia em segundos
BAR = EIGHTH * 8
OUTPUT = Path(__file__).resolve().parent.parent / 'assets' / 'background_music.wav'

# Progressão Am - F - C - G, repetida 4 vezes (16 compassos)
BASS_ROOTS = [45, 41, 48, 43] * 4  # notas MIDI: A2, F2, C3, G2

# Melodia: (nota MIDI ou None para pausa, duração em colcheias); 8 colcheias por compasso
MELODY = [
    # Parte A
    (69, 2), (72, 1), (76, 1), (81, 2), (76, 2),
    (77, 2), (76, 1), (72, 1), (69, 2), (72, 2),
    (79, 2), (76, 1), (72, 1), (67, 2), (72, 2),
    (71, 3), (74, 1), (79, 4),
    (81, 1), (79, 1), (76, 1), (72, 1), (69, 2), (76, 2),
    (77, 1), (76, 1), (72, 1), (69, 1), (65, 2), (69, 2),
    (76, 2), (79, 2), (84, 2), (79, 2),
    (74, 2), (71, 2), (67, 4),
    # Parte B
    (76, 1), (81, 1), (84, 1), (81, 1), (76, 1), (81, 1), (84, 1), (88, 1),
    (77, 1), (81, 1), (84, 1), (81, 1), (77, 1), (81, 1), (84, 1), (89, 1),
    (79, 1), (84, 1), (88, 1), (84, 1), (79, 1), (84, 1), (88, 1), (91, 1),
    (86, 2), (83, 2), (79, 2), (74, 2),
    (81, 4), (79, 2), (76, 2),
    (77, 4), (76, 2), (72, 2),
    (76, 2), (74, 2), (72, 2), (76, 2),
    (71, 2), (74, 2), (79, 2), (83, 2),
]


def midi_to_freq(note):
    return 440.0 * 2 ** ((note - 69) / 12)


def add(buffer, start, samples):
    """Soma as amostras no buffer; o que passar do fim volta ao início (loop sem emenda)."""
    n = len(buffer)
    for i, s in enumerate(samples):
        buffer[(start + i) % n] += s


def tone(freq, duration, wave_fn, volume):
    length = int(duration * SAMPLE_RATE)
    attack = int(0.005 * SAMPLE_RATE)
    release = int(0.03 * SAMPLE_RATE)
    out = []
    for i in range(length):
        phase = (i * freq / SAMPLE_RATE) % 1.0
        env = min(1.0, i / attack, (length - i) / release)
        out.append(wave_fn(phase) * env * volume)
    return out


def square(phase):
    return 1.0 if phase < 0.25 else -1.0  # duty cycle de 25%, timbre "NES"


def triangle(phase):
    return 4 * abs(phase - 0.5) - 1


def kick():
    length = int(0.15 * SAMPLE_RATE)
    out, phase = [], 0.0
    for i in range(length):
        t = i / SAMPLE_RATE
        phase += (40 + 100 * math.exp(-t * 30)) / SAMPLE_RATE
        out.append(math.sin(2 * math.pi * phase) * math.exp(-t * 18) * 0.6)
    return out


def snare(rng):
    length = int(0.12 * SAMPLE_RATE)
    out = []
    for i in range(length):
        t = i / SAMPLE_RATE
        noise = rng.uniform(-1, 1) * math.exp(-t * 30)
        body = math.sin(2 * math.pi * 180 * t) * math.exp(-t * 40)
        out.append((noise * 0.25 + body * 0.15))
    return out


def hihat(rng):
    length = int(0.03 * SAMPLE_RATE)
    out, prev = [], 0.0
    for i in range(length):
        n = rng.uniform(-1, 1)
        out.append((n - prev) * math.exp(-i / SAMPLE_RATE * 120) * 0.05)  # diferença = passa-altas simples
        prev = n
    return out


def main():
    rng = random.Random(2024)  # semente fixa: o arquivo gerado é sempre o mesmo
    total = int(len(BASS_ROOTS) * BAR * SAMPLE_RATE)
    buffer = [0.0] * total

    def at(seconds):
        return int(seconds * SAMPLE_RATE)

    # Melodia
    t = 0.0
    for note, length in MELODY:
        if note is not None:
            add(buffer, at(t), tone(midi_to_freq(note), length * EIGHTH * 0.9, square, 0.12))
        t += length * EIGHTH

    # Baixo em colcheias, alternando a fundamental e a oitava
    for bar, root in enumerate(BASS_ROOTS):
        for step in range(8):
            note = root + (12 if step % 2 else 0)
            add(buffer, at(bar * BAR + step * EIGHTH), tone(midi_to_freq(note), EIGHTH * 0.8, triangle, 0.3))

    # Bateria: bumbo nos tempos 1 e 3, caixa nos tempos 2 e 4, chimbal em toda colcheia
    kick_samples = kick()
    for bar in range(len(BASS_ROOTS)):
        for step in range(8):
            start = at(bar * BAR + step * EIGHTH)
            if step in (0, 4):
                add(buffer, start, kick_samples)
            if step in (2, 6):
                add(buffer, start, snare(rng))
            add(buffer, start, hihat(rng))

    peak = max(abs(s) for s in buffer)
    scale = 0.9 / peak
    frames = b''.join(struct.pack('<h', int(s * scale * 32767)) for s in buffer)

    with wave.open(str(OUTPUT), 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(frames)
    print(f'Gerado {OUTPUT} ({total / SAMPLE_RATE:.1f}s)')


if __name__ == '__main__':
    main()
