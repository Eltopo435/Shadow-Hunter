# Sergio Gabriel Pérez A.
# 23-EISN-2-028

import pygame
from Game.map import Map
from Entities.Player import Jugador
from Entities.Enemy import Enemy
from utils.popup import Popup
from utils.theme import Theme
from utils.assets import ASSETS
from utils.strings import STRINGS


class Game:
    def __init__(self, width=800, height=600):
        # Initialize pygame if not already initialized
        if not pygame.get_init():
            pygame.init()

        # Fixed tile size for consistency
        self.tile_size = 20
        # Calcular dimensiones originales del mapa basadas en el tamaño de ventana inicial
        orig_map_width = width // self.tile_size
        orig_map_height = height // self.tile_size
        # Ajustar la ventana para que se adapte al área dibujada (recordando que en Map se resta 1 a cada dimensión)
        self.width = (orig_map_width - 1) * self.tile_size
        self.height = (orig_map_height - 1) * self.tile_size
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Shadow Hunter")

        # Clock for controlling game speed
        self.clock = pygame.time.Clock()
        self.FPS = 60

        # Calculate optimal map dimensions based on screen size
        # Use the entire screen space
        map_width = orig_map_width
        map_height = orig_map_height

        # Create map
        self.map = Map(map_width, map_height)
        self.map.generate_map()

        # Create player at a safe position
        self.player = Jugador()
        self._spawn_player()
        self.player.bomb_limit = 1  # Starting with 1 bomb
        self.player.cargar_animaciones(self.tile_size)

        # Create enemies
        self.enemies = []
        self._spawn_enemies(4)  # Un enemigo más

        # Game state
        self.game_over = False
        self.victory = False
        self.is_hidden = False  # Nuevo estado para mostrar si el jugador está oculto
        # Nuevo temporizador para mensaje de trampa desactivada
        self.trap_deactivated_timer = 0
        # Add pause functionality
        self.paused = False

        # Load textures
        self._load_textures()
        self._load_enemy_sprites()

        # Load sounds
        self._load_sounds()

        # Font for messages
        self.font = pygame.font.SysFont(
            None, 36) if pygame.font.get_init() else None
        # Larger font for important messages
        self.large_font = pygame.font.SysFont(
            None, 64) if pygame.font.get_init() else None

        # Inicializar lista de popups y fuente para popups
        self.popups = []
        self.popup_font = pygame.font.SysFont(
            None, 28) if pygame.font.get_init() else None

        # Initialize joystick
        self.joystick = None
        self._init_joystick()

    def _init_joystick(self):
        """Initialize joystick if available"""
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

    def _load_textures(self):
        """Load and prepare game textures using sprites"""
        self.textures = {
            Map.EMPTY: pygame.image.load(str(ASSETS.TILE_EMPTY.value)).convert(),
            Map.WALL: pygame.image.load(str(ASSETS.TILE_WALL.value)).convert(),
            Map.HIDING: pygame.image.load(str(ASSETS.TILE_HIDING.value)).convert(),
            Map.TRAP: pygame.image.load(str(ASSETS.TILE_TRAP.value)).convert(),
            Map.EXIT: pygame.image.load(str(ASSETS.TILE_EXIT.value)).convert(),
            Map.DEACTIVATED: pygame.image.load(str(ASSETS.TILE_DEACTIVATED.value)).convert()
        }

        # Scale textures to the tile size
        for key in self.textures:
            self.textures[key] = pygame.transform.scale(self.textures[key], (self.tile_size, self.tile_size))

    def _load_enemy_sprites(self):
        """Load and prepare enemy sprites"""
        self.enemy_sprites = {
            'idle': [
                pygame.image.load(str(ASSETS.ENEMY_IDLE_1.value)).convert_alpha(),
                pygame.image.load(str(ASSETS.ENEMY_IDLE_2.value)).convert_alpha(),
                pygame.image.load(str(ASSETS.ENEMY_IDLE_3.value)).convert_alpha(),
                pygame.image.load(str(ASSETS.ENEMY_IDLE_4.value)).convert_alpha()
            ],
            'attack': [
                pygame.image.load(str(ASSETS.ENEMY_ATTACK_1.value)).convert_alpha(),
                pygame.image.load(str(ASSETS.ENEMY_ATTACK_2.value)).convert_alpha(),
                pygame.image.load(str(ASSETS.ENEMY_ATTACK_3.value)).convert_alpha(),
                pygame.image.load(str(ASSETS.ENEMY_ATTACK_4.value)).convert_alpha()
            ],
            'walk': [
                pygame.image.load(str(ASSETS.ENEMY_WALK_1.value)).convert_alpha(),
                pygame.image.load(str(ASSETS.ENEMY_WALK_2.value)).convert_alpha(),
                pygame.image.load(str(ASSETS.ENEMY_WALK_3.value)).convert_alpha(),
                pygame.image.load(str(ASSETS.ENEMY_WALK_4.value)).convert_alpha()
            ]
        }
        # Scale sprites to the tile size
        for key in self.enemy_sprites:
            self.enemy_sprites[key] = [pygame.transform.scale(sprite, (self.tile_size, self.tile_size)) for sprite in self.enemy_sprites[key]]

    def _load_sounds(self):
        """Load and prepare game sounds"""
        self.sounds = {
            'attack': pygame.mixer.Sound(str(ASSETS.ATTACK_SOUND.value)),
            'victory': pygame.mixer.Sound(str(ASSETS.VICTORY_SOUND.value)),  # Add victory sound
            'game_over': pygame.mixer.Sound(str(ASSETS.GAME_OVER_SOUND.value))  # Add game over sound
        }

    def _spawn_player(self):
        """Coloca al jugador en una posición válida después de generar el mapa"""
        # Buscar una posición válida comenzando por la esquina superior izquierda
        for y in range(1, self.map.height - 1):
            for x in range(1, self.map.width - 1):
                if self.map.is_walkable(x, y):
                    self.player.pos_x = x * Jugador.TAMAÑO_AZULEJO
                    self.player.pos_y = y * Jugador.TAMAÑO_AZULEJO
                    self.map.player_position = (x, y)
                    return

        # Si por alguna razón no encontramos un lugar, usar la posición por defecto
        self.player.pos_x = 1 * Jugador.TAMAÑO_AZULEJO
        self.player.pos_y = 1 * Jugador.TAMAÑO_AZULEJO
        self.map.player_position = (1, 1)

    def _spawn_enemies(self, count):
        """Spawn enemies at safe positions, away from the player and spaced apart from each other"""
        import random

        # Limpiar lista de enemigos por si acaso
        self.enemies = []
        # Guardar las posiciones (en grid) ya asignadas a enemigos
        spawned_positions = []

        # Obtener la posición del jugador en coordenadas de mapa
        player_tile_x = self.player.pos_x // Jugador.TAMAÑO_AZULEJO
        player_tile_y = self.player.pos_y // Jugador.TAMAÑO_AZULEJO
        min_enemy_distance = 5  # distancia Manhattan mínima entre enemigos

        for _ in range(count):
            # Buscar una posición segura para el enemigo
            safe_pos = self.map.find_safe_spawn(min_distance_from_player=8)

            if safe_pos and all(abs(safe_pos[0] - pos[0]) + abs(safe_pos[1] - pos[1]) >= min_enemy_distance for pos in spawned_positions):
                x, y = safe_pos
                enemy = Enemy(x * Jugador.TAMAÑO_AZULEJO,
                              y * Jugador.TAMAÑO_AZULEJO)
                self.enemies.append(enemy)
                spawned_positions.append((x, y))
                continue

            # Si no encontramos posición segura, usar método alternativo (menos óptimo)
            attempts = 0
            found = False
            while attempts < 50 and not found:  # Limit attempts to prevent infinite loop
                x = random.randint(5, self.map.width - 2)
                y = random.randint(5, self.map.height - 2)

                # Verificar si la posición es válida
                if (self.map.is_walkable(x, y) and
                    not self.map.is_exit(x, y) and
                    not self.map.is_hiding_spot(x, y) and
                        # Mantener distancia del jugador
                        abs(x - player_tile_x) + abs(y - player_tile_y) > 5 and
                        all(abs(x - pos[0]) + abs(y - pos[1]) >= min_enemy_distance for pos in spawned_positions)):

                    enemy = Enemy(x * Jugador.TAMAÑO_AZULEJO,
                                  y * Jugador.TAMAÑO_AZULEJO)
                    self.enemies.append(enemy)
                    spawned_positions.append((x, y))
                    found = True
                    break

                attempts += 1

    def update(self):
        """Update game state"""
        if self.paused:
            return

        keys = pygame.key.get_pressed()

        # Get player input
        dx = 0
        dy = 0

        # Get player input from keyboard
        if keys[pygame.K_RIGHT]:
            dx = 1
            self.player.direccion = 1  # Right
        elif keys[pygame.K_LEFT]:
            dx = -1
            self.player.direccion = 3  # Left

        if keys[pygame.K_DOWN]:
            dy = 1
            self.player.direccion = 0  # Front
        elif keys[pygame.K_UP]:
            dy = -1
            self.player.direccion = 2  # Back

        # Get player input from joystick
        if self.joystick:
            axis_x = self.joystick.get_axis(0)
            axis_y = self.joystick.get_axis(1)
            if axis_x > 0.5:
                dx = 1
                self.player.direccion = 1  # Right
            elif axis_x < -0.5:
                dx = -1
                self.player.direccion = 3  # Left
            if axis_y > 0.5:
                dy = 1
                self.player.direccion = 0  # Front
            elif axis_y < -0.5:
                dy = -1
                self.player.direccion = 2  # Back

        # Move player
        if not self.game_over and not self.victory:
            self.player.mover(dx, dy, self.map.grid, self.enemies, [])
            # Update player position in the map for enemy reference
            player_tile_x = self.player.pos_x // Jugador.TAMAÑO_AZULEJO
            player_tile_y = self.player.pos_y // Jugador.TAMAÑO_AZULEJO
            self.map.player_position = (player_tile_x, player_tile_y)

            if 0 <= player_tile_x < self.map.width and 0 <= player_tile_y < self.map.height:
                self.is_hidden = self.map.is_player_hidden()

                # Priorizar victoria: si se alcanza el exit, se gana el juego
                if self.map.is_exit(player_tile_x, player_tile_y):
                    self.victory = True
                    self.sounds['victory'].play()  # Play victory sound

                # Check for traps - if player moves onto a trap tile, game over
                if self.map.is_trap(player_tile_x, player_tile_y):
                    self.game_over = True
                    self.sounds['game_over'].play()  # Play game over sound
                    return

                # Update enemies if player not hidden
                for enemy in self.enemies:
                    enemy.update(self.player, self.map)
                    if not self.is_hidden:
                        enemy_tile_x = enemy.pos_x // Jugador.TAMAÑO_AZULEJO
                        enemy_tile_y = enemy.pos_y // Jugador.TAMAÑO_AZULEJO
                        if player_tile_x == enemy_tile_x and player_tile_y == enemy_tile_y:
                            self.game_over = True
                            self.sounds['game_over'].play()  # Play game over sound
                            return
        # Decrementar temporizador de mensaje de trampa desactivada si está activo
        if self.trap_deactivated_timer > 0:
            self.trap_deactivated_timer -= 1

        # Agregar popup para cuando el jugador está oculto
        if self.is_hidden:
            if not any(p.message == STRINGS.SHOW_HIDDEN_MESSAGE.value for p in self.popups):
                self.show_popup(
                    STRINGS.SHOW_HIDDEN_MESSAGE.value, duration=120)
        # Agregar popup cuando el jugador está oculto y un enemigo lo persigue
        from Entities.Enemy import EnemyState
        if self.is_hidden and any(enemy.state == EnemyState.PURSUING for enemy in self.enemies):
            if not any(p.message == STRINGS.PURSUING_ALERT.value for p in self.popups):
                self.show_popup(STRINGS.PURSUING_ALERT.value, duration=90)

        for popup in self.popups:
            popup.update()
        self.popups = [p for p in self.popups if p.remaining > 0]

    def render(self):
        """Render the game"""
        self.screen.fill((0, 0, 0))  # Fill screen with black

        # Draw map - fill the entire screen
        for y in range(self.map.height):
            for x in range(self.map.width):
                # Convertir a int
                cell_type = int(self.map.get_cell_type(x, y))
                self.screen.blit(self.textures[cell_type],
                                 (x * self.tile_size, y * self.tile_size))

        # Draw player
        if self.player.animacion and self.player.animacion[self.player.direccion]:
            player_frame = 0  # Use a fixed frame for simplicity
            player_surface = self.player.animacion[self.player.direccion][player_frame].copy(
            )

            # Si el jugador está oculto, hacerlo semi-transparente
            if self.is_hidden:
                player_surface.set_alpha(128)  # 50% transparencia

            self.screen.blit(player_surface,
                             ((self.player.pos_x * self.tile_size) // Jugador.TAMAÑO_AZULEJO,
                              (self.player.pos_y * self.tile_size) // Jugador.TAMAÑO_AZULEJO))
            self.player.frame += 1

        # Draw enemies
        for enemy in self.enemies:
            if enemy.vivo:
                # Use idle sprite for simplicity
                enemy_sprite = self.enemy_sprites['idle'][0]
                self.screen.blit(enemy_sprite,
                                 ((enemy.pos_x * self.tile_size) // Jugador.TAMAÑO_AZULEJO,
                                  (enemy.pos_y * self.tile_size) // Jugador.TAMAÑO_AZULEJO))
                # Add a marker to make enemies more visible
                pygame.draw.circle(self.screen, (0, 0, 0),
                                   ((enemy.pos_x * self.tile_size) // Jugador.TAMAÑO_AZULEJO + self.tile_size//2,
                                    (enemy.pos_y * self.tile_size) // Jugador.TAMAÑO_AZULEJO + self.tile_size//2),
                                   self.tile_size // 3)

        # Dibujar rutas A* de los enemigos en persecución con línea mejorada
        from Entities.Enemy import EnemyState
        for enemy in self.enemies:
            if enemy.current_path and enemy.state == EnemyState.PURSUING:
                points = []
                for (tx, ty) in enemy.current_path:
                    points.append((tx * self.tile_size + self.tile_size // 2,
                                   ty * self.tile_size + self.tile_size // 2))
                # Dibujar línea más gruesa y de color más claro solo si hay suficientes puntos
                if len(points) >= 2:  # Verificar que hay al menos 2 puntos para dibujar la línea
                    pygame.draw.lines(
                        self.screen, (255, 100, 100), False, points, 4)
                # Dibujar marcadores en cada punto del camino
                for point in points:
                    pygame.draw.circle(self.screen, (255, 0, 0), point, 3)

            # Mostrar la última posición conocida del jugador (memoria) si existe
            if enemy.last_seen_position and enemy.memory_timer > 0:
                mem_x, mem_y = enemy.last_seen_position
                pygame.draw.circle(
                    self.screen,
                    (255, 200, 0),  # Color amarillo
                    (mem_x * self.tile_size + self.tile_size // 2,
                     mem_y * self.tile_size + self.tile_size // 2),
                    self.tile_size // 3,
                    2  # Solo el contorno, grosor 2
                )

        # Mostrar mensaje de trampa desactivada si el temporizador está activo
        if self.font and self.trap_deactivated_timer > 0:
            msg = self.font.render(
                STRINGS.TRAP_DEACTIVATED.value, True, (255, 255, 0))
            self.screen.blit(msg, (self.width//2 - msg.get_width()//2, 50))

        # Draw game over or victory message with improved style
        if self.game_over or self.victory:
            # Create semi-transparent overlay
            overlay = pygame.Surface(
                (self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # Semi-transparent black
            self.screen.blit(overlay, (0, 0))

            # Draw title
            if self.large_font:
                title_text = STRINGS.GAME_OVER_TITLE.value if self.game_over else STRINGS.VICTORY_TITLE.value
                title_color = (255, 0, 0) if self.game_over else (0, 255, 0)
                title_surf = self.large_font.render(
                    title_text, True, title_color)
                self.screen.blit(
                    title_surf,
                    (self.width // 2 - title_surf.get_width() // 2,
                     self.height // 2 - title_surf.get_height() - 20)
                )

            # Draw instruction
            if self.font:
                instr_text = STRINGS.RESTART_INSTRUCTION.value
                instr_surf = self.font.render(
                    instr_text, True, (255, 255, 255))
                self.screen.blit(
                    instr_surf,
                    (self.width // 2 - instr_surf.get_width() // 2,
                     self.height // 2 + 20)
                )

        # Draw pause screen if paused
        if self.paused:
            # Create semi-transparent overlay
            overlay = pygame.Surface(
                (self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # Semi-transparent black
            self.screen.blit(overlay, (0, 0))

            # Draw pause title
            if self.large_font:
                pause_text = STRINGS.PAUSED_TITLE.value
                text_surf = self.large_font.render(
                    pause_text, True, (255, 255, 255))
                self.screen.blit(
                    text_surf,
                    (self.width // 2 - text_surf.get_width() // 2,
                     self.height // 3)
                )

            # Draw instructions
            if self.font:
                continue_text = STRINGS.PAUSE_CONTINUE.value
                continue_surf = self.font.render(
                    continue_text, True, (200, 200, 200))
                self.screen.blit(
                    continue_surf,
                    (self.width // 2 - continue_surf.get_width() // 2,
                     self.height // 2)
                )

                quit_text = STRINGS.PAUSE_QUIT.value
                quit_surf = self.font.render(quit_text, True, (200, 200, 200))
                self.screen.blit(
                    quit_surf,
                    (self.width // 2 - quit_surf.get_width() // 2,
                     self.height // 2 + 40)
                )

        # Después de renderizar todo el juego, dibujar popups
        for popup in self.popups:
            popup.render(self.screen)

        pygame.display.flip()

    def run(self):
        """Main game loop"""
        running = True

        while running:
            # Handle events
            try:
                events = pygame.event.get()
            except SystemError as e:
                print(f"Error during event handling: {e}")
                continue

            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and (self.game_over or self.victory):
                        # Restart game
                        self.__init__(self.width, self.height)
                    elif event.key == pygame.K_ESCAPE:
                        if self.game_over or self.victory:
                            running = False
                        else:
                            self.paused = not self.paused
                    elif event.key == pygame.K_q and self.paused:
                        return False  # Return to main menu
                    elif event.key == pygame.K_e and not self.paused:
                        self._handle_interaction()  # Nueva interacción con E
                    elif event.key == pygame.K_a and not self.paused:
                        self._handle_attack()  # Agregar efecto de ataque
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:  # Assuming button 0 is for interaction
                        self._handle_interaction()
                    elif event.button == 1:  # Assuming button 1 is for attack
                        self._handle_attack()
                    elif event.button == 7:  # Assuming button 7 is for pause
                        self.paused = not self.paused
                    elif event.button == 6:  # Assuming button 6 is for quit
                        return False  # Return to main menu

            self.update()
            self.render()
            self.clock.tick(self.FPS)

        return True

    def show_popup(self, message, duration=120):
        """Agrega un nuevo popup en la parte superior central de la pantalla."""
        if self.popup_font:
            pos = (self.width // 2, 30)
            self.popups.append(Popup(message, duration, self.popup_font, pos))

    def _handle_interaction(self):
        """Permite interactuar presionando E para esconderse o desactivar trampas"""
        from Entities.Player import Jugador  # Asegurarse de tener acceso a Jugador

        # Obtener la posición actual del jugador (en celdas del mapa)
        px, py = self.map.player_position

        # Determinar la celda 'al frente' basada en la dirección:
        # 0: abajo, 1: derecha, 2: arriba, 3: izquierda
        if self.player.direccion == 0:       # Abajo
            target = (px, py + 1)
        elif self.player.direccion == 1:     # Derecha
            target = (px + 1, py)
        elif self.player.direccion == 2:     # Arriba
            target = (px, py - 1)
        elif self.player.direccion == 3:     # Izquierda
            target = (px - 1, py)
        else:
            target = (px, py)

        x, y = target

        # Verificar que la celda objetivo esté dentro del mapa
        if not self.map.is_valid_position(x, y):
            return

        cell_type = self.map.get_cell_type(x, y)

        # Si es un escondite, mover al jugador a esa celda (para "esconderse")
        if cell_type == self.map.HIDING:
            self.player.pos_x = x * Jugador.TAMAÑO_AZULEJO
            self.player.pos_y = y * Jugador.TAMAÑO_AZULEJO
            self.map.player_position = (x, y)
        # Si es una trampa, desactivarla cambiando la celda a EMPTY
        elif cell_type == self.map.TRAP:
            # Desactivar la trampa y activar mensaje
            self.map.grid[y][x] = self.map.DEACTIVATED
            self.show_popup(STRINGS.TRAP_DEACTIVATED.value, duration=120)

    def _handle_attack(self):
        """Handle player attack effect"""
        # Reproducir sonido de ataque
        self.sounds['attack'].play()

        # Obtener la posición actual del jugador (en celdas del mapa)
        px, py = self.map.player_position
