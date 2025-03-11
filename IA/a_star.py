# Sergio Gabriel Pérez A.
# 23-EISN-2-028

import heapq


class AStar:
    def __init__(self, game_map):
        self.map = game_map
        self.max_search_distance = 40  # Limitar la búsqueda para evitar cálculos excesivos
        self.cache = {}  # Cache para almacenar caminos frecuentes

    def heuristic(self, a, b):
        # Usar distancia Manhattan para la heurística
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def get_neighbors(self, pos):
        x, y = pos
        # Optimización: orden de exploración direccionado hacia el objetivo cuando es posible
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        neighbors = []

        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if (0 <= new_x < self.map.width and
                0 <= new_y < self.map.height and
                    self.map.is_walkable(new_x, new_y)):
                neighbors.append((new_x, new_y))

        return neighbors

    def find_path(self, start, goal):
        # Verificar el caché primero
        cache_key = (start, goal)
        if cache_key in self.cache:
            return self.cache[cache_key].copy()

        # Si la distancia es demasiado grande, usar un camino aproximado
        if self.heuristic(start, goal) > self.max_search_distance:
            return self.find_approximate_path(start, goal)

        # Implementación estándar A*
        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}

        while frontier:
            _, current = heapq.heappop(frontier)

            if current == goal:
                break

            # Optimización: si la distancia es excesiva, abortar
            if cost_so_far[current] > self.max_search_distance * 1.5:
                break

            for next_pos in self.get_neighbors(current):
                new_cost = cost_so_far[current] + 1
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + self.heuristic(goal, next_pos)
                    heapq.heappush(frontier, (priority, next_pos))
                    came_from[next_pos] = current

        if goal not in came_from:
            # Si no hay camino al objetivo, buscar el punto más cercano alcanzable
            closest = min(came_from.keys(), key=lambda pos: self.heuristic(
                pos, goal), default=start)
            if closest == start:
                return []
            goal = closest

        # Reconstruir el camino
        path = []
        current = goal
        while current is not None:
            path.append(current)
            current = came_from[current]
        path.reverse()

        # Guardar en caché para uso futuro (solo si no es demasiado largo)
        if len(path) <= 20:
            self.cache[cache_key] = path.copy()

        return path

    def find_approximate_path(self, start, goal):
        """Encuentra un camino aproximado cuando el objetivo está muy lejos"""
        # Dirección general hacia el objetivo
        path = [start]
        current_x, current_y = start
        goal_x, goal_y = goal

        # Calcular una trayectoria en línea recta hasta el límite de búsqueda
        steps = min(self.max_search_distance, self.heuristic(start, goal))
        for _ in range(steps):
            # Determinar dirección principal
            if abs(current_x - goal_x) > abs(current_y - goal_y):
                dx = 1 if current_x < goal_x else -1
                dy = 0
            else:
                dx = 0
                dy = 1 if current_y < goal_y else -1

            # Verificar si la nueva posición es válida
            new_x, new_y = current_x + dx, current_y + dy
            if (0 <= new_x < self.map.width and
                0 <= new_y < self.map.height and
                    self.map.is_walkable(new_x, new_y)):
                current_x, current_y = new_x, new_y
                path.append((current_x, current_y))
            else:
                # Intentar otra dirección
                if dx != 0:  # Si estábamos moviéndonos horizontalmente
                    dy = 1 if current_y < goal_y else -1
                    dx = 0
                else:  # Si estábamos moviéndonos verticalmente
                    dx = 1 if current_x < goal_x else -1
                    dy = 0

                # Verificar la nueva dirección
                new_x, new_y = current_x + dx, current_y + dy
                if (0 <= new_x < self.map.width and
                    0 <= new_y < self.map.height and
                        self.map.is_walkable(new_x, new_y)):
                    current_x, current_y = new_x, new_y
                    path.append((current_x, current_y))

        return path
