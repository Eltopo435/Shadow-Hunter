# Sergio Gabriel Pérez A.
# 23-EISN-2-028

import math
from typing import List
import pygame
from utils.assets import ASSETS


class Jugador:
    pos_x = 4
    pos_y = 4
    direccion = 0
    frame = 0
    animacion: List = []
    rango = 3
    TAMAÑO_AZULEJO = 4

    def __init__(self):
        self.vivo = True
        self.bomb_limit = 0  # Add missing attribute for bombs
        # Initialize animation lists for simple colored rectangles
        self.animacion = [[], [], [], []]

    def mover(self, dx, dy, grid, enemigos, power_ups):
        """ Summary :
                Método que se encarga de mover al jugador

            Parámetros :
                dx : int
                    Movimiento en x
                dy : int
                    Movimiento en y
                grid : list
                    Lista de grid
                enemigos : list
                    Lista de enemigos
        """
        tempx = int(self.pos_x / Jugador.TAMAÑO_AZULEJO)
        tempy = int(self.pos_y / Jugador.TAMAÑO_AZULEJO)

        mapa = []

        for i in range(len(grid)):
            mapa.append([])
            for j in range(len(grid[i])):
                mapa[i].append(grid[i][j])

        # Fix for enemy positions outside map area
        for x in enemigos:
            if x == self:
                continue
            elif not x.vivo:
                continue
            else:
                enemy_x = int(x.pos_x / Jugador.TAMAÑO_AZULEJO)
                enemy_y = int(x.pos_y / Jugador.TAMAÑO_AZULEJO)
                # Make sure the enemy position is within valid map boundaries
                if 0 <= enemy_x < len(mapa[0]) and 0 <= enemy_y < len(mapa):
                    mapa[enemy_y][enemy_x] = 2

        if self.pos_x % Jugador.TAMAÑO_AZULEJO != 0 and dx == 0:
            if self.pos_x % Jugador.TAMAÑO_AZULEJO == 1:
                self.pos_x -= 1
            elif self.pos_x % Jugador.TAMAÑO_AZULEJO == 3:
                self.pos_x += 1
            return
        if self.pos_y % Jugador.TAMAÑO_AZULEJO != 0 and dy == 0:
            if self.pos_y % Jugador.TAMAÑO_AZULEJO == 1:
                self.pos_y -= 1
            elif self.pos_y % Jugador.TAMAÑO_AZULEJO == 3:
                self.pos_y += 1
            return

        # Usar valores permitidos en lugar de solo 0 (EMPTY)
        # Exclude traps (3) from allowed values - player can't walk through them
        allowed = (0, 2, 4, 5)  # EMPTY, HIDING, EXIT, DEACTIVATED
        # Derecha
        if dx == 1:
            if tempx+1 < len(mapa[0]) and mapa[tempy][tempx+1] in allowed:
                self.pos_x += 1
        # Izquierda
        elif dx == -1:
            tempx = math.ceil(self.pos_x / Jugador.TAMAÑO_AZULEJO)
            if tempx-1 >= 0 and mapa[tempy][tempx-1] in allowed:
                self.pos_x -= 1

        # Abajo
        if dy == 1:
            if tempy+1 < len(mapa) and mapa[tempy+1][tempx] in allowed:
                self.pos_y += 1
        # Arriba
        elif dy == -1:
            tempy = math.ceil(self.pos_y / Jugador.TAMAÑO_AZULEJO)
            if tempy-1 >= 0 and mapa[tempy-1][tempx] in allowed:
                self.pos_y -= 1

        for pu in power_ups:
            if pu.pos_x == math.ceil(self.pos_x / Jugador.TAMAÑO_AZULEJO) \
                    and pu.pos_y == math.ceil(self.pos_y / Jugador.TAMAÑO_AZULEJO):
                self.consumir_power_up(pu, power_ups)

    def validar_muerte(self, exp):
        """ Summary :
                Método que se encarga de validar la muerte del jugador

            Parámetros :
                exp : list
                    Lista de explosiones
        """
        for e in exp:
            for s in e.sectores:
                if int(self.pos_x / Jugador.TAMAÑO_AZULEJO) == s[0] and int(self.pos_y / Jugador.TAMAÑO_AZULEJO) == s[1]:
                    self.vivo = False

    def cargar_animaciones(self, scale):
        """Load character sprites from assets

        Args:
            scale: Size to scale the sprites to
        """
        self.animacion = [[], [], [], []]

        # Load all images and scale them
        def load_and_scale(asset_path):
            img = pygame.image.load(str(asset_path))
            return pygame.transform.scale(img, (scale, scale))

        # Down animations (0)
        self.animacion[0].extend([
            load_and_scale(ASSETS.CHARACTER_IDLE_DOWN_1.value),
            load_and_scale(ASSETS.CHARACTER_IDLE_DOWN_2.value),
            load_and_scale(ASSETS.CHARACTER_IDLE_DOWN_3.value),
            load_and_scale(ASSETS.CHARACTER_IDLE_DOWN_4.value),
            load_and_scale(ASSETS.CHARACTER_IDLE_DOWN_5.value)
        ])

        # Right animations (1)
        self.animacion[1].extend([
            load_and_scale(ASSETS.CHARACTER_IDLE_RIGHT_1.value),
            load_and_scale(ASSETS.CHARACTER_IDLE_RIGHT_2.value),
            load_and_scale(ASSETS.CHARACTER_IDLE_RIGHT_3.value),
            load_and_scale(ASSETS.CHARACTER_WALK_RIGHT_1.value),
            load_and_scale(ASSETS.CHARACTER_WALK_RIGHT_2.value)
        ])

        # Up animations (2)
        self.animacion[2].extend([
            load_and_scale(ASSETS.CHARACTER_IDLE_UP_1.value),
            load_and_scale(ASSETS.CHARACTER_IDLE_UP_2.value),
            load_and_scale(ASSETS.CHARACTER_IDLE_UP_3.value),
            load_and_scale(ASSETS.CHARACTER_IDLE_UP_4.value),
            load_and_scale(ASSETS.CHARACTER_IDLE_UP_5.value)
        ])

        # Left animations (3)
        self.animacion[3].extend([
            load_and_scale(ASSETS.CHARACTER_WALK_LEFT_1.value),
            load_and_scale(ASSETS.CHARACTER_WALK_LEFT_2.value),
            load_and_scale(ASSETS.CHARACTER_WALK_LEFT_3.value),
            load_and_scale(ASSETS.CHARACTER_WALK_LEFT_4.value),
            load_and_scale(ASSETS.CHARACTER_WALK_LEFT_5.value)
        ])
