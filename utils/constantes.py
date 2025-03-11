# Sergio Gabriel Pérez A.
# 23-EISN-2-028

from pathlib import Path
import pygame as pg
from enum import Enum

import pygame_menu
from utils.strings import STRINGS

# Root path
ROOT_PATH: Path = Path(__file__).parent.parent
ROOT_PATH_STR: str = str(ROOT_PATH)

# Initialize display to get screen info
pg.display.init()
INFO = pg.display.Info()


class CONSTANTES (Enum):
    '''
    Todas las constantes utilizadas en el juego
    '''

    # Root paths
    ROOT_PATH = Path(__file__).parent.parent
    ROOT_PATH_STR = str(ROOT_PATH)
    ASSETS_PATH = ROOT_PATH / 'assets'
    ASSETS_PATH_STR = str(ASSETS_PATH)

    # Constantes de ventana general
    WINDOW_SCALE = 1.00
    TILE_SIZE = int(INFO.current_h * 0.06)
    WINDOW_SIZE = (16 * TILE_SIZE, 11.7 * TILE_SIZE)
    FPS = 60.0

    # Constantes de la ventana del menu
    ANCHO_VENTANA = 800
    ALTO_VENTANA = 600
    TITULO_VENTANA = STRINGS.TITLE_VENTANA.value

    # Constantes de la ventana del juego
    ANCHO_VENTANA_JUEGO = 800
    ALTO_VENTANA_JUEGO = 600
    TITULO_VENTANA_JUEGO = STRINGS.TITLE_VENTANA.value
    FPS_JUEGO = 60

    # Colores estilo Shadow Hunter
    COLOR_BLACK = (0, 0, 0)
    COLOR_WHITE = (255,255,255)       # Blanco suave
    COLOR_string_white = (255,255,255)         # Blanco para ambiente sigiloso
    # For testing : MENU_BACKGROUND_COLOR = (10, 10, 15)
    MENU_TITLE_COLOR = (180, 180, 200)  # Casi negro con un toque de azul
    TRANSPARENT_COLOR = (0, 0, 0, 0)

    # Configuración del menú
    MENU_WIDGET_FONT = pygame_menu.font.FONT_8BIT
    MENU_TITLE_FONT_SIZE = TILE_SIZE - 10
    MENU_OPTIONS_FONT = pygame_menu.font.FONT_MUNRO
    MENU_WIDGET_FONT_SIZE = int(TILE_SIZE * 0.6) + 20
    MENU_WIDGET_MARGIN = (0, 14)
    MENU_WIDGET_PADDING = 14
    MENU_WIDGET_BORDER_WIDTH = 1

    # * Constantes de colores

    # * Fuentes (pygame.font.Font)

    # * Extras
