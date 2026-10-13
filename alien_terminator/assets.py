# -*- coding: utf-8 -*-
"""Carregamento das imagens do jogo, feito uma única vez na inicialização."""
from dataclasses import dataclass

import pygame

from . import config


class AssetError(Exception):
    """Recurso obrigatório ausente ou inválido."""


@dataclass(frozen=True)
class Images:
    player: pygame.Surface
    background: pygame.Surface
    alien: pygame.Surface
    meteorite: pygame.Surface
    predator: pygame.Surface
    predator_laser: pygame.Surface
    predator_laser2: pygame.Surface
    heart: pygame.Surface


def load_images(assets_dir=config.ASSETS_DIR, convert=True):
    """Carrega todas as imagens e as devolve em um único objeto compartilhado.

    Com ``convert=True`` (exige uma janela já criada) as superfícies são
    convertidas para o formato da tela, o que acelera os blits a cada frame.
    Todos os arquivos ausentes ou inválidos são relatados de uma vez.
    """
    loaded, problems = {}, []
    for key, filename in config.IMAGE_FILES.items():
        path = assets_dir / filename
        if not path.is_file():
            problems.append(f'arquivo não encontrado: {path}')
            continue
        try:
            surface = pygame.image.load(str(path))
        except pygame.error as exc:
            problems.append(f'falha ao ler {path}: {exc}')
            continue
        if convert:
            # O fundo é opaco; os demais sprites têm transparência
            surface = surface.convert() if key == 'background' else surface.convert_alpha()
        loaded[key] = surface

    if problems:
        raise AssetError('Não foi possível carregar as imagens do jogo:\n  - ' + '\n  - '.join(problems))
    return Images(**loaded)
