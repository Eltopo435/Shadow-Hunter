# Sergio Gabriel Pérez A.
# 23-EISN-2-028

import math
import random
from enum import Enum
from IA.nodo import Accion, Secuencia, Selector, Timer
from IA.a_star import AStar


class EnemyState(Enum):
    IDLE = 1
    PATROLLING = 2
    PURSUING = 3


class Enemy:
    all_enemies: list = []  # Registra todas las instancias de Enemy

    def __init__(self, x, y):
        # Añadir la instancia a la lista de enemigos
        Enemy.all_enemies.append(self)
        self.pos_x = x
        self.pos_y = y
        self.vivo = True
        self.velocidad = 0.1
        self.vision_range = 15  # Incrementado para perseguir desde mayor distancia
        self.max_vision_range = 20  # Rango máximo para detección con probabilidad
        self.patrol_timer = 0
        self.move_cooldown = 0  # Agregar cooldown para movimiento
        self.max_move_cooldown = 5  # Cuadros antes de mover
        self.patrol_direction = self._random_direction()
        self.color = (200, 50, 50)  # Red color for enemies
        self.last_valid_pos = (x, y)  # Track last valid position

        # Estado actual del enemigo
        self.state = EnemyState.PATROLLING

        # Para A*
        self.current_path = []
        self.path_index = 0
        self.path_update_timer = 0
        self.path_update_interval = 20  # Antes era 100; ahora se actualiza más seguido
        # Nueva variable para seguimiento
        self.distance_to_player = float('inf')
        self.pathfinder = None  # Se inicializará en el update

        # Agregar temporizador para mantener estado de persecución
        self.pursuing_timer = 0
        # 3 segundos a 60 FPS (máximo tiempo persiguiendo)
        self.max_pursuing_time = 180

        # Memoria del último avistamiento
        self.last_seen_position = None  # Posición donde se vio al jugador por última vez
        # El enemigo recordará la última posición por 5 segundos
        self.memory_persistence = 300
        self.memory_timer = 0  # Contador para la memoria

        # Variables para patrullaje fluido
        self.patrol_target_x = None
        self.patrol_target_y = None
        self.patrol_has_target = False

        # Comportamiento
        self.setup_behavior_tree()

    def _random_direction(self):
        """Returns a random direction (dx, dy) different from the previous one"""
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        # Filter out the current direction to avoid repeating it
        if hasattr(self, 'patrol_direction') and self.patrol_direction in directions:
            directions.remove(self.patrol_direction)

        return random.choice(directions)

    def setup_behavior_tree(self):
        """Configura el árbol de comportamiento del enemigo"""
        # Acciones básicas
        is_in_attack_range = Accion(self.is_in_attack_range)
        attack_player = Accion(self.attack_player)
        check_player_visible = Accion(self.is_player_visible)
        pursue_player = Accion(self.pursue_player)
        patrol = Accion(self.patrol)
        check_position = Accion(self.check_valid_position)

        # Secuencia de ataque (si el jugador está en rango, ataca)
        secuencia_attack = Secuencia()
        secuencia_attack.agregar_hijo(is_in_attack_range)
        secuencia_attack.agregar_hijo(attack_player)

        # Secuencia de persecución (si ve al jugador, lo persigue)
        secuencia_perseguir = Secuencia()
        secuencia_perseguir.agregar_hijo(check_player_visible)
        secuencia_perseguir.agregar_hijo(pursue_player)

        # Selector de comportamiento: atacar, perseguir o patrullar
        selector_comportamiento = Selector()
        selector_comportamiento.agregar_hijo(
            secuencia_attack)    # Intentar atacar primero
        selector_comportamiento.agregar_hijo(
            secuencia_perseguir)   # Luego perseguir
        selector_comportamiento.agregar_hijo(
            patrol)                # Finalmente patrullar

        # Secuencia principal (verificar posición y luego decidir comportamiento)
        secuencia_principal = Secuencia()
        secuencia_principal.agregar_hijo(check_position)
        secuencia_principal.agregar_hijo(selector_comportamiento)

        self.comportamiento = secuencia_principal

    def update(self, player, mapa):
        """Update enemy position based on player location and map"""

        # Inicializar pathfinder si es necesario
        if self.pathfinder is None and mapa is not None:
            self.pathfinder = AStar(mapa)

        # Guardar el jugador y el mapa para usar en el comportamiento
        self.player = player
        self.mapa = mapa

        # Verificación adicional: si no estamos en rango de ataque pero
        # estábamos persiguiendo sin ruta válida, reiniciar el estado
        if (self.state == EnemyState.PURSUING and
            not self.current_path and
                self.pursuing_timer <= 0):
            self._reset_pursuit_state()
            self.state = EnemyState.PATROLLING

        # REACTIVADO: ejecutar el árbol de comportamiento para permitir movimiento (patrulla/persigue)
        self.comportamiento.ejecutar()

        # Verificación adicional después de cualquier movimiento para asegurar posición válida
        from Entities.Player import Jugador
        grid_x = int(self.pos_x / Jugador.TAMAÑO_AZULEJO)
        grid_y = int(self.pos_y / Jugador.TAMAÑO_AZULEJO)

        # Si por alguna razón terminamos en una posición no válida, restaurar a última posición válida
        if not mapa.is_valid_position(grid_x, grid_y) or not mapa.is_walkable(grid_x, grid_y):
            self.pos_x, self.pos_y = self.last_valid_pos
            # Reiniciar patrones de movimiento si detectamos esta situación anormal
            self.current_path = []
            self.path_index = 0
            if self.state == EnemyState.PURSUING:
                self.pursuing_timer = 0
                self.state = EnemyState.PATROLLING

    def check_valid_position(self):
        """Verificar si el enemigo está en una posición válida"""
        from Entities.Player import Jugador

        # Verificar si el enemigo está en una posición válida
        if not self.mapa.is_valid_position(int(self.pos_x / Jugador.TAMAÑO_AZULEJO), int(self.pos_y / Jugador.TAMAÑO_AZULEJO)) or \
           not self.mapa.is_walkable(int(self.pos_x / Jugador.TAMAÑO_AZULEJO), int(self.pos_y / Jugador.TAMAÑO_AZULEJO)):
            # Restaurar a la última posición válida
            self.pos_x, self.pos_y = self.last_valid_pos
        return True  # Siempre continuar con el árbol de comportamiento

    def is_player_visible(self):
        """Verifica si el jugador está en rango de visión y no está escondido"""
        if not self.player:
            return False

        from Entities.Player import Jugador

        # Get positions in grid
        enemy_x = int(self.pos_x / Jugador.TAMAÑO_AZULEJO)
        enemy_y = int(self.pos_y / Jugador.TAMAÑO_AZULEJO)
        player_x = int(self.player.pos_x / Jugador.TAMAÑO_AZULEJO)
        player_y = int(self.player.pos_y / Jugador.TAMAÑO_AZULEJO)

        # Check if player is hiding
        if self.mapa.is_hiding_spot(player_x, player_y):
            self._reset_pursuit_state()
            return False

        # Calculate distance
        distance = math.sqrt((enemy_x - player_x) ** 2 +
                             (enemy_y - player_y) ** 2)
        self.distance_to_player = distance  # Actualizar la distancia actual

        # Si el jugador está muy lejos, no puede ser visto de ninguna manera
        if distance > self.max_vision_range:
            # Si estábamos persiguiendo pero ahora está muy lejos, reducir los timers más rápido
            if self.state == EnemyState.PURSUING:
                self.pursuing_timer = max(
                    0, self.pursuing_timer - 2)  # Reducción más rápida
            return False

        # System with probability based on distance:
        # - If very close (<=vision_range/2), 100% detection
        # - If at vision_range, 70% detection
        # - If at max_vision_range, 20% detection

        detection_chance = 0
        if distance <= self.vision_range / 2:
            detection_chance = 1.0  # 100% de detección si está muy cerca
        elif distance <= self.vision_range:
            detection_chance = 0.7  # 70% de detección en el rango normal
        elif distance <= self.max_vision_range:
            # Probabilidad decreciente entre vision_range y max_vision_range
            ratio = (self.max_vision_range - distance) / \
                (self.max_vision_range - self.vision_range)
            detection_chance = 0.2 + (0.5 * ratio)  # Entre 20% y 70%

        # Check if player is in vision range and has line of sight
        if detection_chance > 0 and random.random() <= detection_chance and self.has_line_of_sight(enemy_x, enemy_y, player_x, player_y):
            # Ajustar tiempo de persecución según la distancia (más cerca = persigue más tiempo)
            pursuing_time = int(self.max_pursuing_time *
                                (1 - (distance / (self.max_vision_range * 2))))
            # Mínimo 1 segundo de persecución
            pursuing_time = max(60, pursuing_time)

            self.pursuing_timer = pursuing_time
            self.state = EnemyState.PURSUING

            # Actualizar posición de última vez que vio al jugador
            self.last_seen_position = (player_x, player_y)
            self.memory_timer = self.memory_persistence

            return True
        else:
            # Si ya se estaba persiguiendo y aún queda tiempo en el temporizador, continuar persiguiendo
            if self.state == EnemyState.PURSUING and self.pursuing_timer > 0:
                self.pursuing_timer -= 1
                return True
            elif self.last_seen_position and self.memory_timer > 0:
                # Si aún tiene memoria de dónde vio al jugador, ir a esa posición
                self.memory_timer -= 1
                # Verificar si estamos muy lejos de la última posición conocida
                last_pos_distance = self.heuristic_distance(enemy_x, enemy_y,
                                                            self.last_seen_position[0],
                                                            self.last_seen_position[1])
                if last_pos_distance > self.max_vision_range * 1.5:
                    # Si estamos muy lejos del último punto, olvidar y volver a patrullar
                    self._reset_pursuit_state()
                    return False
                return True

            self._reset_pursuit_state()
            return False

    def heuristic_distance(self, x1, y1, x2, y2):
        """Calcula la distancia Manhattan entre dos puntos"""
        return abs(x1 - x2) + abs(y1 - y2)

    def _reset_pursuit_state(self):
        """Resetea el estado de persecución"""
        self.state = EnemyState.PATROLLING
        self.pursuing_timer = 0
        self.current_path = []  # Limpiar el camino actual
        self.path_index = 0
        if self.memory_timer <= 0:
            self.last_seen_position = None

    def has_line_of_sight(self, start_x, start_y, end_x, end_y):
        """Implementa el algoritmo de Bresenham para verificar línea de visión"""
        points = self.bresenham_line(start_x, start_y, end_x, end_y)

        # Verificar cada punto en la línea
        # Ignorar la primera posición (donde está el enemigo)
        for x, y in points[1:]:
            if not self.is_valid_position(x, y) or not self.mapa.is_walkable(x, y):
                return False

        return True

    def is_valid_position(self, x, y):
        """Verifica si una posición está dentro de los límites del mapa"""
        return self.mapa and self.mapa.is_valid_position(x, y)

    def bresenham_line(self, x0, y0, x1, y1):
        """Algoritmo de Bresenham para trazar línea entre dos puntos"""
        points = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            points.append((x0, y0))
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

        return points

    def pursue_player(self):
        """Persigue al jugador utilizando A*"""
        from Entities.Player import Jugador

        if not self.player or not self.pathfinder:
            return False

        # Obtener posiciones en la cuadrícula
        start_x = int(self.pos_x / Jugador.TAMAÑO_AZULEJO)
        start_y = int(self.pos_y / Jugador.TAMAÑO_AZULEJO)

        # Validación adicional: verificar que la posición inicial es válida
        if not self.mapa.is_valid_position(start_x, start_y) or not self.mapa.is_walkable(start_x, start_y):
            # Restaurar a una posición conocida válida
            self.pos_x, self.pos_y = self.last_valid_pos
            start_x = int(self.pos_x / Jugador.TAMAÑO_AZULEJO)
            start_y = int(self.pos_y / Jugador.TAMAÑO_AZULEJO)
            # Si aún no es válida, cancelar persecución
            if not self.mapa.is_valid_position(start_x, start_y) or not self.mapa.is_walkable(start_x, start_y):
                self._reset_pursuit_state()
                return False

        # Verificar si el jugador está fuera de rango máximo para perseguir
        if self.distance_to_player > self.max_vision_range * 1.5:
            self._reset_pursuit_state()
            return False

        # Actualizar el camino con frecuencia variable según la distancia
        update_interval_factor = 1
        if self.distance_to_player < self.vision_range / 2:
            # Muy cerca: actualizar más frecuentemente
            update_interval_factor = 0.5
        elif self.distance_to_player > self.vision_range:
            # Lejos: actualizar menos frecuentemente
            update_interval_factor = 1.5

        adjusted_interval = max(
            5, int(self.path_update_interval * update_interval_factor))

        # Actualizar el camino periódicamente o cuando no hay camino válido
        self.path_update_timer += 1
        if self.path_update_timer >= adjusted_interval or not self.current_path:
            self.path_update_timer = 0

            # Si el jugador está visible, perseguirlo directamente
            if self.state == EnemyState.PURSUING and self.pursuing_timer > 0:
                end_x = int(self.player.pos_x / Jugador.TAMAÑO_AZULEJO)
                end_y = int(self.player.pos_y / Jugador.TAMAÑO_AZULEJO)
            # Si tiene memoria de la última posición, ir allí
            elif self.last_seen_position and self.memory_timer > 0:
                end_x, end_y = self.last_seen_position
            else:
                # Esto no debería pasar, pero como fallback volvemos a patrullar
                self.state = EnemyState.PATROLLING
                return False

            # Verificar si ambos puntos son válidos
            if not self.is_valid_position(start_x, start_y) or not self.is_valid_position(end_x, end_y):
                return False

            # Si el punto de inicio y fin son iguales, no necesitamos un camino
            if (start_x, start_y) == (end_x, end_y):
                self.current_path = [(start_x, start_y)]
                self.path_index = 0
            else:
                # Usar A* para encontrar el camino
                self.current_path = self.pathfinder.find_path(
                    (start_x, start_y), (end_x, end_y))
                self.path_index = 0

            # Si no se encontró camino y estamos usando memoria, borrar la memoria
            if not self.current_path:
                if self.last_seen_position:
                    # Intentar encontrar un punto accesible cercano a la última posición conocida
                    nearby_points = []
                    for dx in range(-3, 4):
                        for dy in range(-3, 4):
                            nx, ny = self.last_seen_position[0] + \
                                dx, self.last_seen_position[1] + dy
                            if self.is_valid_position(nx, ny) and self.mapa.is_walkable(nx, ny):
                                dist = abs(dx) + abs(dy)
                                nearby_points.append((dist, (nx, ny)))

                    if nearby_points:
                        # Ordenar por distancia y usar el punto más cercano
                        nearby_points.sort()
                        end_x, end_y = nearby_points[0][1]
                        self.current_path = self.pathfinder.find_path(
                            (start_x, start_y), (end_x, end_y))
                        self.path_index = 0

                # Si todavía no hay camino, volver a patrullar
                if not self.current_path:
                    self.last_seen_position = None
                    self.memory_timer = 0
                    self.state = EnemyState.PATROLLING
                    return False

            # Validar que el camino tiene al menos un punto
            if not self.current_path:
                self.current_path = [(start_x, start_y)]

        # Si tenemos un camino válido, seguirlo
        if self.current_path and self.path_index < len(self.current_path):
            next_x, next_y = self.current_path[self.path_index]

            # Verificación adicional: asegurar que el siguiente punto es caminable
            if not self.mapa.is_walkable(next_x, next_y):
                # Si el siguiente punto no es caminable, recalcular ruta
                self.current_path = []
                self.path_index = 0
                # Forzar actualización inmediata
                self.path_update_timer = self.path_update_interval
                return False

            # Convertir coordenadas de grid a píxeles (centrando en el bloque)
            target_x = next_x * Jugador.TAMAÑO_AZULEJO + Jugador.TAMAÑO_AZULEJO / 2
            target_y = next_y * Jugador.TAMAÑO_AZULEJO + Jugador.TAMAÑO_AZULEJO / 2

            # Calcular dirección normalizada para un movimiento más suave
            diff_x = target_x - self.pos_x
            diff_y = target_y - self.pos_y
            threshold = Jugador.TAMAÑO_AZULEJO * 0.3

            dx = 0
            dy = 0
            if abs(diff_x) > abs(diff_y) and abs(diff_x) > threshold:
                dx = 1 if diff_x > 0 else -1
            elif abs(diff_y) > threshold:
                dy = 1 if diff_y > 0 else -1

            # Intentar moverse
            moved = self._move(dx, dy, self.mapa)
            # Calcular distancia real a la meta en píxeles
            distance_to_target = ((self.pos_x - target_x)
                                  ** 2 + (self.pos_y - target_y)**2)**0.5

            if distance_to_target < Jugador.TAMAÑO_AZULEJO * 0.5:
                # Forzar que el enemigo quede centrado en el bloque vacío
                self.pos_x = target_x
                self.pos_y = target_y
                self.path_index += 1

                # Si se terminó el camino y no se ve al jugador, ajustar temporizador
                if self.path_index >= len(self.current_path) and not self.is_player_in_los():
                    self.pursuing_timer = max(0, self.pursuing_timer - 5)

            return moved

        # Si no hay camino o hemos llegado al final, verificar si debemos volver a patrullar
        self.pursuing_timer = max(0, self.pursuing_timer - 1)
        if self.pursuing_timer <= 0:
            self.state = EnemyState.PATROLLING
            return False

        return False

    def is_player_in_los(self):
        """Verifica si el jugador está en línea de visión directa"""
        if not self.player:
            return False

        from Entities.Player import Jugador

        enemy_x = int(self.pos_x / Jugador.TAMAÑO_AZULEJO)
        enemy_y = int(self.pos_y / Jugador.TAMAÑO_AZULEJO)
        player_x = int(self.player.pos_x / Jugador.TAMAÑO_AZULEJO)
        player_y = int(self.player.pos_y / Jugador.TAMAÑO_AZULEJO)

        # Verificar distancia primero
        distance = math.sqrt((enemy_x - player_x)**2 + (enemy_y - player_y)**2)
        if distance > self.vision_range:
            return False

        # Verificar si hay línea de visión
        return self.has_line_of_sight(enemy_x, enemy_y, player_x, player_y)

    def patrol(self):
        """Patrol randomly around the map with smooth movement between tiles."""
        from Entities.Player import Jugador

        # Si no tenemos un objetivo de patrulla o hemos llegado al actual, escoger uno nuevo
        if not self.patrol_has_target:
            self.patrol_timer += 1
            if self.patrol_timer > 100:
                self.patrol_timer = 0
                self.patrol_direction = self._random_direction()

            dx, dy = self.patrol_direction
            current_tile_x = int(self.pos_x / Jugador.TAMAÑO_AZULEJO)
            current_tile_y = int(self.pos_y / Jugador.TAMAÑO_AZULEJO)
            new_tile_x = current_tile_x + dx
            new_tile_y = current_tile_y + dy

            # Verificar que el nuevo destino es válido y ningún otro enemigo ya está allí
            is_valid_target = self._validate_patrol_target(
                new_tile_x, new_tile_y)

            if (is_valid_target):
                # Establecer el nuevo objetivo de patrulla
                self.patrol_target_x = new_tile_x * Jugador.TAMAÑO_AZULEJO
                self.patrol_target_y = new_tile_y * Jugador.TAMAÑO_AZULEJO
                self.patrol_has_target = True
            else:
                # Si el objetivo no es válido, cambiar de dirección
                self.patrol_direction = self._random_direction()
                return False

        # Si tenemos un objetivo, movernos hacia él gradualmente
        if self.patrol_has_target:
            # Determinar la dirección hacia el objetivo
            dx = 0
            if self.patrol_target_x > self.pos_x:
                dx = 1
            elif self.patrol_target_x < self.pos_x:
                dx = -1

            dy = 0
            if self.patrol_target_y > self.pos_y:
                dy = 1
            elif self.patrol_target_y < self.pos_y:
                dy = -1

            # Usar _move para movimiento suave
            self._move(dx, dy, self.mapa)

            # Comprobar si hemos llegado al objetivo (con margen de error)
            margin = 0.5
            if (abs(self.pos_x - self.patrol_target_x) < margin and
                    abs(self.pos_y - self.patrol_target_y) < margin):
                # Ajustar la posición exactamente al centro del tile
                self.pos_x = self.patrol_target_x
                self.pos_y = self.patrol_target_y
                self.last_valid_pos = (self.pos_x, self.pos_y)
                self.patrol_has_target = False

            return True

        return False

    def _validate_patrol_target(self, tile_x, tile_y):
        """Valida si un tile es un objetivo válido para patrullar."""
        from Entities.Player import Jugador

        # Verificación más estricta: asegurarse que la posición es válida y caminable
        if not self.mapa.is_valid_position(tile_x, tile_y):
            return False

        if not self.mapa.is_walkable(tile_x, tile_y):
            return False

        # Verificar que no hay otros enemigos en esa casilla
        for enemy in Enemy.all_enemies:
            if enemy is not self:
                enemy_tile_x = int(enemy.pos_x / Jugador.TAMAÑO_AZULEJO)
                enemy_tile_y = int(enemy.pos_y / Jugador.TAMAÑO_AZULEJO)

                # Si hay otro enemigo en el destino o camino hacia ese destino
                if enemy_tile_x == tile_x and enemy_tile_y == tile_y:
                    return False

                # Si el enemigo también tiene un objetivo y es el mismo que queremos
                if (hasattr(enemy, 'patrol_has_target') and enemy.patrol_has_target and
                    enemy.patrol_target_x == tile_x * Jugador.TAMAÑO_AZULEJO and
                        enemy.patrol_target_y == tile_y * Jugador.TAMAÑO_AZULEJO):
                    return False

        return True

    def _move(self, dx, dy, mapa):
        """Try to move the enemy and return whether movement was successful"""
        from Entities.Player import Jugador

        if dx == 0 and dy == 0:
            return True

        # Calcular la posición actual y nueva en la cuadrícula
        current_grid_x = int(self.pos_x / Jugador.TAMAÑO_AZULEJO)
        current_grid_y = int(self.pos_y / Jugador.TAMAÑO_AZULEJO)

        # Calcular la nueva posición tentativa en píxeles
        new_x = self.pos_x + dx * self.velocidad * Jugador.TAMAÑO_AZULEJO
        new_y = self.pos_y + dy * self.velocidad * Jugador.TAMAÑO_AZULEJO

        # Calcular la nueva posición en la cuadrícula
        new_grid_x = int(new_x / Jugador.TAMAÑO_AZULEJO)
        new_grid_y = int(new_y / Jugador.TAMAÑO_AZULEJO)

        # Si vamos a cambiar de celda, verificar que la nueva celda es válida
        if new_grid_x != current_grid_x or new_grid_y != current_grid_y:
            # Verificar si la nueva posición es válida y caminable
            if not mapa.is_valid_position(new_grid_x, new_grid_y) or not mapa.is_walkable(new_grid_x, new_grid_y):
                # Si no podemos movernos a la nueva celda, intentar alinearnos con la celda actual
                if new_grid_x != current_grid_x:
                    # Alinear horizontalmente
                    target_x = current_grid_x * Jugador.TAMAÑO_AZULEJO
                    self.pos_x = target_x
                if new_grid_y != current_grid_y:
                    # Alinear verticalmente
                    target_y = current_grid_y * Jugador.TAMAÑO_AZULEJO
                    self.pos_y = target_y

                # Cancelar el movimiento actual
                self._reset_movement()
                return False

        # Si el movimiento es válido, actualizar posición
        self.pos_x = new_x
        self.pos_y = new_y
        self.last_valid_pos = (self.pos_x, self.pos_y)
        return True

    def _reset_movement(self):
        """Resetea el estado de movimiento cuando se encuentra un obstáculo"""
        # Limpiar el camino actual
        self.current_path = []
        self.path_index = 0

        # Si estábamos persiguiendo, volver a calcular ruta
        if self.state == EnemyState.PURSUING:
            self.path_update_timer = self.path_update_interval
        # Si estábamos patrullando, cambiar dirección
        else:
            self.patrol_direction = self._random_direction()
            self.patrol_has_target = False

    def is_in_attack_range(self):
        """Verifica si el jugador está en rango de ataque (adyacente en la grilla)"""
        from Entities.Player import Jugador
        if not self.player:
            return False

        enemy_x = int(self.pos_x / Jugador.TAMAÑO_AZULEJO)
        enemy_y = int(self.pos_y / Jugador.TAMAÑO_AZULEJO)
        player_x = int(self.player.pos_x / Jugador.TAMAÑO_AZULEJO)
        player_y = int(self.player.pos_y / Jugador.TAMAÑO_AZULEJO)

        # Añadir verificación: si el jugador está en un escondite, no puede ser atacado
        if self.mapa.is_hiding_spot(player_x, player_y):
            return False

        # Verificación más estricta: solo permitir ataque en posiciones adyacentes (no diagonales)
        # La suma de las diferencias debe ser exactamente 1 para ser ortogonalmente adyacentes
        manhattan_distance = abs(enemy_x - player_x) + abs(enemy_y - player_y)
        if manhattan_distance == 1:  # Solo inmediatamente arriba, abajo, izquierda o derecha
            # Verificar línea de visión directa (sin obstáculos)
            if self.has_line_of_sight(enemy_x, enemy_y, player_x, player_y):
                return True
        return False

    def attack_player(self):
        """Realiza la acción de atacar al jugador"""
        # Lógica de ataque; por ahora se simula con un print.
       
        return True
