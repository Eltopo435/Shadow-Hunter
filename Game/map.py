# Sergio Gabriel Pérez A.
# 23-EISN-2-028

import numpy as np  # type: ignore
import random


class Map:
    # Constantes para los tipos de casillas
    EMPTY = 0      # Suelo/camino
    WALL = 1       # Muro/pared
    HIDING = 2     # Escondite
    TRAP = 3       # Trampa
    EXIT = 4       # Salida
    DEACTIVATED = 5  # Trampa desactivada

    def __init__(self, width=40, height=30):  # Tamaño de mapa aumentado
        """Inicializa un mapa con dimensiones dadas ajustando la cantidad de celdas"""
        self.width = width - 1   # Se resta 1 para evitar la columna extra a la derecha
        self.height = height - 1  # Se resta 1 para evitar la fila extra inferior
        self.grid = np.zeros((self.height, self.width), dtype=int)
        self.player_position = (1, 1)  # Posición inicial del jugador
        self.enemies = []  # Lista para almacenar posiciones de enemigos

    def generate_map(self):
        """Genera un laberinto utilizando DFS (backtracking)"""
        # Inicializar todo el grid como muros
        self.grid.fill(self.WALL)
        # Crear el pasillo inicial
        self.grid[1, 1] = self.EMPTY
        stack = [(1, 1)]
        while stack:
            x, y = stack[-1]
            # Buscar vecinos a dos celdas de distancia que aún sean muros
            neighbors = []
            for dx, dy in [(2, 0), (-2, 0), (0, 2), (0, -2)]:
                nx, ny = x + dx, y + dy
                if 0 < nx < self.width - 1 and 0 < ny < self.height - 1 and self.grid[ny, nx] == self.WALL:
                    neighbors.append((nx, ny, dx, dy))
            if neighbors:
                nx, ny, dx, dy = random.choice(neighbors)
                # Quitar la pared intermedia para conectar las celdas
                self.grid[y + dy//2, x + dx//2] = self.EMPTY
                self.grid[ny, nx] = self.EMPTY
                stack.append((nx, ny))
            else:
                stack.pop()
        # Agregar pasajes aleatorios para crear rutas alternativas
        additional_passages = max(3, (self.width * self.height) // 200)
        self._add_random_passages(additional_passages)
        # Agregar casillas especiales (escondites y trampas)
        hiding_spots = max(6, (self.width * self.height) // 50)
        self._add_special_tiles(self.HIDING, hiding_spots)
        trap_spots = max(2, (self.width * self.height) // 150)
        self._add_special_tiles(self.TRAP, trap_spots)
        # Colocar la salida en la esquina inferior derecha del área interior
        exit_x = self.width - 2
        exit_y = self.height - 2
        self.grid[exit_y, exit_x] = self.EXIT
        # Asegurar la conexión a la salida: despejar celda izquierda y superior si son muros
        if self.grid[exit_y, exit_x-1] != self.EMPTY:
            self.grid[exit_y, exit_x-1] = self.EMPTY
        if self.grid[exit_y-1, exit_x] != self.EMPTY:
            self.grid[exit_y-1, exit_x] = self.EMPTY

    def _divide(self, x, y, width, height, min_size=3, orientation=None):
        """Algoritmo de división recursiva mejorado para generar el laberinto"""
        if width < min_size or height < min_size:
            return

        # Decidir orientación de la división si no se especificó
        if orientation is None:
            # Favorecer la división en la dimensión más larga
            if width < height:
                orientation = 'h'  # horizontal
            elif height < width:
                orientation = 'v'  # vertical
            else:
                orientation = random.choice(['h', 'v'])

        is_horizontal = orientation == 'h'

        if is_horizontal:
            # Dividir horizontalmente
            wall_y = y + random.randint(1, height - 2)
            door_x = x + random.randint(0, width - 1)

            for i in range(x, x + width):
                if i != door_x:
                    self.grid[wall_y][i] = self.WALL

            # Cambiar orientación para siguiente división (crear patrones más interesantes)
            next_orientation = 'v'

            # Dividir recursivamente las dos áreas creadas
            self._divide(x, y, width, wall_y - y, min_size, next_orientation)
            self._divide(x, wall_y + 1, width, y + height - wall_y - 1, min_size, next_orientation)
        else:
            # Dividir verticalmente
            wall_x = x + random.randint(1, width - 2)
            door_y = y + random.randint(0, height - 1)

            for i in range(y, y + height):
                if i != door_y:
                    self.grid[i][wall_x] = self.WALL

            # Cambiar orientación para siguiente división
            next_orientation = 'h'

            # Dividir recursivamente las dos áreas creadas
            self._divide(x, y, wall_x - x, height, min_size, next_orientation)
            self._divide(wall_x + 1, y, x + width - wall_x - 1, height, min_size, next_orientation)

    def _add_special_tiles(self, tile_type, count):
        """Añade casillas especiales (escondites, trampas, etc.)"""
        empty_cells = [(x, y) for y in range(1, self.height-1)
                       for x in range(1, self.width-1)
                       if self.grid[y][x] == self.EMPTY]
        if not empty_cells:
            return

        # Para rastrear las casillas ya colocadas (solo para HIDING)
        placed = []
        for _ in range(count):
            if not empty_cells:
                break
            # Si se añaden escondites, filtrar para que no estén muy juntos
            if tile_type == self.HIDING and placed:
                # distancia mínima (Manhattan) entre escondites
                min_distance = 3
                empty_cells = [cell for cell in empty_cells
                               if all(abs(cell[0] - p[0]) + abs(cell[1] - p[1]) >= min_distance for p in placed)]
                if not empty_cells:
                    break
            choice = random.choice(empty_cells)
            self.grid[choice[1]][choice[0]] = tile_type
            placed.append(choice)
            empty_cells.remove(choice)

    def _ensure_path_exists(self, start, end):
        """Asegura que existe un camino desde start hasta end usando pathfinding"""
        start_x, start_y = start
        end_x, end_y = end

        # Implementamos un pathfinding básico A* para encontrar un camino
        open_set = [(start_x, start_y)]
        came_from = {}

        g_score = {(start_x, start_y): 0}
        f_score = {(start_x, start_y): abs(
            end_x - start_x) + abs(end_y - start_y)}

        while open_set:
            # Encontrar nodo con menor f_score
            current = min(
                open_set, key=lambda pos: f_score.get(pos, float('inf')))

            if current == (end_x, end_y):
                # Reconstruir y abrir el camino
                while current in came_from:
                    x, y = current
                    self.grid[y][x] = self.EMPTY
                    current = came_from[current]
                return True

            open_set.remove(current)
            x, y = current

            # Explorar vecinos (4 direcciones)
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy

                if not self.is_valid_position(nx, ny):
                    continue

                # Calcular nueva puntuación
                tentative_g = g_score[current] + 1

                if (nx, ny) not in g_score or tentative_g < g_score[(nx, ny)]:
                    came_from[(nx, ny)] = current
                    g_score[(nx, ny)] = tentative_g
                    f_score[(nx, ny)] = tentative_g + \
                        abs(end_x - nx) + abs(end_y - ny)

                    if (nx, ny) not in open_set:
                        open_set.append((nx, ny))

        # Si no se encuentra camino, crear uno directo
        x, y = start_x, start_y
        while x != end_x:
            x += 1 if x < end_x else -1
            self.grid[y][x] = self.EMPTY

        while y != end_y:
            y += 1 if y < end_y else -1
            self.grid[y][x] = self.EMPTY

        return True

    def _add_random_passages(self, count):
        """Añadir pasajes aleatorios para hacer el laberinto menos predecible"""
        for _ in range(count):
            # Elegir un muro interior aleatorio
            wall_positions = [(x, y) for y in range(2, self.height-2)
                              for x in range(2, self.width-2)
                              if self.grid[y][x] == self.WALL]

            if not wall_positions:
                continue

            x, y = random.choice(wall_positions)

            # Verificar si es un muro interior adecuado para crear un pasaje
            horizontal_walls = (self.grid[y][x-1] == self.WALL and self.grid[y][x+1] == self.WALL and
                                self.grid[y-1][x] != self.WALL and self.grid[y+1][x] != self.WALL)

            vertical_walls = (self.grid[y-1][x] == self.WALL and self.grid[y+1][x] == self.WALL and
                              self.grid[y][x-1] != self.WALL and self.grid[y][x+1] != self.WALL)

            if horizontal_walls or vertical_walls:
                self.grid[y][x] = self.EMPTY

    def _clean_isolated_walls(self):
        """Elimina paredes aisladas para mejorar la apariencia del laberinto"""
        for y in range(1, self.height-1):
            for x in range(1, self.width-1):
                if self.grid[y][x] == self.WALL:
                    # Contar paredes vecinas
                    wall_neighbors = 0
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        nx, ny = x + dx, y + dy
                        if self.is_valid_position(nx, ny) and self.grid[ny][nx] == self.WALL:
                            wall_neighbors += 1

                    # Si está aislada (sin paredes vecinas), convertirla en suelo
                    if wall_neighbors == 0:
                        self.grid[y][x] = self.EMPTY

    def is_valid_position(self, x, y):
        """Verifica si una posición está dentro de los límites del mapa"""
        return 0 <= x < self.width and 0 <= y < self.height

    def is_walkable(self, x, y):
        """Verifica si una posición es transitable"""
        if not self.is_valid_position(x, y):
            return False
        # Se permite transitar si la celda es EMPTY, HIDING, EXIT o DEACTIVATED
        # NO se permite transitar si es un TRAP (trampa no desactivada)
        return self.grid[y][x] in (self.EMPTY, self.HIDING, self.EXIT, self.DEACTIVATED)

    def find_safe_spawn(self, min_distance_from_player=10):
        """Encuentra un lugar seguro para aparecer (no en paredes, no cerca del jugador)"""
        import random

        player_x, player_y = self.player_position
        safe_positions = []

        # Buscar todas las posiciones seguras que estén lejos del jugador
        for y in range(1, self.height-1):
            for x in range(1, self.width-1):
                if self.grid[y][x] == self.EMPTY:  # Solo en casillas vacías
                    distance = abs(x - player_x) + \
                        abs(y - player_y)  # Distancia Manhattan
                    if distance >= min_distance_from_player:
                        safe_positions.append((x, y))

        # Si no hay posiciones seguras lejanas, aceptar cualquier posición vacía
        if not safe_positions:
            for y in range(1, self.height-1):
                for x in range(1, self.width-1):
                    if self.grid[y][x] == self.EMPTY:
                        safe_positions.append((x, y))

        # Si aún no hay posiciones seguras, la última opción es al lado del jugador
        if not safe_positions:
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = player_x + dx, player_y + dy
                if self.is_valid_position(nx, ny) and self.grid[ny][nx] == self.EMPTY:
                    return nx, ny

        # Elegir una posición aleatoria de las seguras
        if safe_positions:
            return random.choice(safe_positions)

        # Si todo falla, retornar None (aunque esto no debería ocurrir en un mapa bien generado)
        return None

    def is_hiding_spot(self, x, y):
        """Verifica si una posición es un lugar para esconderse"""
        if not self.is_valid_position(x, y):
            return False
        return self.grid[y][x] == self.HIDING

    def is_trap(self, x, y):
        """Verifica si una posición es una trampa"""
        if not self.is_valid_position(x, y):
            return False
        return self.grid[y][x] == self.TRAP

    def is_player_hidden(self):
        """Verifica si el jugador está en un escondite"""
        x, y = self.player_position
        return self.is_hiding_spot(x, y)

    def check_trap(self, x, y):
        """Verifica si hay una trampa en la posición dada"""
        return self.is_trap(x, y)

    def is_exit(self, x, y):
        """Verifica si una posición es la salida"""
        if not self.is_valid_position(x, y):
            return False
        return self.grid[y][x] == self.EXIT

    def get_cell_type(self, x, y):
        """Devuelve el tipo de celda en la posición dada"""
        if not self.is_valid_position(x, y):
            return None
        return self.grid[y][x]

    def set_player_position(self, x, y):
        """Establece la posición del jugador"""
        if self.is_walkable(x, y):
            self.player_position = (x, y)
            return True
        return False

    def add_enemy(self, x, y):
        """Añade un enemigo en la posición especificada"""
        if self.is_walkable(x, y):
            self.enemies.append((x, y))
            return True
        return False

    def can_see(self, x1, y1, x2, y2):
        """Determina si desde (x1,y1) se puede ver (x2,y2) usando el algoritmo de Bresenham"""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        current_x, current_y = x1, y1

        while True:
            # Si llegamos a una pared, no hay línea de visión
            if self.get_cell_type(current_x, current_y) == self.WALL and (current_x != x1 or current_y != y1):
                return False

            # Si llegamos al destino, hay línea de visión
            if current_x == x2 and current_y == y2:
                return True

            e2 = 2 * err
            if e2 > -dy:
                if current_x == x2:
                    break
                err -= dy
                current_x += sx
            if e2 < dx:
                if current_y == y2:
                    break
                err += dx
                current_y += sy

        return True
