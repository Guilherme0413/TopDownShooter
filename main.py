# Top Down Shooter Game - Autor: Guilherme Oliveira 40119106

import pygame
import random
import os
import sys

pygame.init()

# Configurações da Tela do Jogo
WIDTH, HEIGHT = 800, 600
FPS = 60
ASSET_DIR = "assets"

# Inicialização da Tela
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Top-Down Shooter - Completo")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)
big_font = pygame.font.SysFont(None, 44)

# Funções Auxiliares para Carregar Recursos
def load_image(path, scale=None, alpha=True):
    try:
        if alpha:
            img = pygame.image.load(path).convert_alpha()
        else:
            img = pygame.image.load(path).convert()
        if scale:
            img = pygame.transform.scale(img, scale)
        return img
    except Exception as e:
        print(f"Erro carregando {path}: {e}")
        return None

def load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except Exception as e:
        print(f"Erro carregando {path}: {e}")
        return None

def draw_text(surf, text, x, y, color=(255,255,255), center=False, font_obj=None):
    if font_obj is None:
        font_obj = font
    img = font_obj.render(text, True, color)
    if center:
        r = img.get_rect(center=(x,y))
        surf.blit(img, r)
    else:
        surf.blit(img, (x,y))
        