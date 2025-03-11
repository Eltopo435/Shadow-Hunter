# Sergio Gabriel Pérez A.
# 23-EISN-2-028

import pygame
import pygame_menu
import pygame_menu.sound
from utils.constantes import CONSTANTES
from utils.assets import ASSETS
from utils.strings import STRINGS


class Theme:
    """
    Clase que maneja la configuración del tema del menú del juego
    """
    # Inicialización de variables de clase
    surface = None
    menu_background_image = None

    @classmethod
    def initialize(cls):
        """
        Inicializa la superficie y carga la imagen de fondo
        """
        pygame.display.init()
        cls.surface = pygame.display.set_mode(CONSTANTES.WINDOW_SIZE.value)
        cls.menu_background_image = pygame.image.load(
            str(ASSETS.BACKGROUND_MENU.value))
        return cls.surface

    @classmethod
    def main_background(cls):
        """
        Dibuja el fondo del menú
        """
        # Obtener dimensiones
        window_width, window_height = cls.surface.get_rect().size
        image_width, image_height = cls.menu_background_image.get_rect().size

        # Forzar ajuste a la altura de la ventana
        scale_ratio = window_height / image_height

        # Calcular nuevas dimensiones
        new_width = int(image_width * scale_ratio)
        new_height = window_height

        # Escalar imagen
        scaled_background = pygame.transform.scale(
            cls.menu_background_image, (new_width, new_height))

        # Centrar horizontalmente
        x = (window_width - new_width) // 2
        y = 0

        # Limpiar superficie
        cls.surface.fill(CONSTANTES.COLOR_BLACK.value)

        # Dibujar imagen centrada
        cls.surface.blit(scaled_background, (x, y))

        # Dibujar borde
        pygame.draw.rect(cls.surface, CONSTANTES.COLOR_string_white.value,
                         cls.surface.get_rect(), 3)

    @staticmethod
    def get_shadow_hunter_theme() -> pygame_menu.Theme:
        """
        Crea y retorna el tema personalizado Shadow Hunter para el menú

        Returns:
            pygame_menu.Theme: Tema configurado para el menú
        """
        return pygame_menu.Theme(
            selection_color=CONSTANTES.COLOR_string_white.value,
            widget_font=CONSTANTES.MENU_OPTIONS_FONT.value,
            title_font_size=int(CONSTANTES.MENU_TITLE_FONT_SIZE.value),
            title_font_color=CONSTANTES.COLOR_string_white.value,
            title_font=CONSTANTES.MENU_WIDGET_FONT.value,
            widget_font_color=CONSTANTES.COLOR_WHITE.value,
            widget_font_size=int(CONSTANTES.MENU_WIDGET_FONT_SIZE.value),
            background_color=CONSTANTES.TRANSPARENT_COLOR.value,
            title_background_color=CONSTANTES.TRANSPARENT_COLOR.value,
            widget_border_color=CONSTANTES.COLOR_string_white.value,
            widget_border_width=int(CONSTANTES.MENU_WIDGET_BORDER_WIDTH.value),
            widget_margin=CONSTANTES.MENU_WIDGET_MARGIN.value,
            widget_padding=int(CONSTANTES.MENU_WIDGET_PADDING.value)
        )

    @classmethod
    def create_menu(cls, title: str, width: int, height: int, onclose=None) -> pygame_menu.Menu:
        """
        Crea un menú con el tema Shadow Hunter

        Args:
            title (str): Título del menú
            width (int): Ancho del menú
            height (int): Alto del menú
            onclose: Acción al cerrar el menú (opcional)

        Returns:
            pygame_menu.Menu: Menú configurado
        """
        theme = cls.get_shadow_hunter_theme()
        return pygame_menu.Menu(
            theme=theme,
            height=height,
            width=width,
            onclose=onclose,
            title=title
        )

    @staticmethod
    def set_button_sounds(menu, sound):
        """
        Asigna sonidos a los botones del menú
        """
        for widget in menu.get_widgets():
            if isinstance(widget, pygame_menu.widgets.Button):
                widget.set_sound(sound)

    @classmethod
    def create_controls_menu(cls, window_width: int, window_height: int) -> pygame_menu.Menu:
        """
        Crea el menú de controles y mecánicas
        """
        controls_menu = cls.create_menu(
            title=STRINGS.CONTROLS_TITLE.value,
            width=window_width,
            height=window_height
        )

        controls_menu.add.label(STRINGS.CONTROLS_HEADER.value)
        controls_menu.add.label(STRINGS.CONTROL_MOVE.value)
        controls_menu.add.label(STRINGS.CONTROL_INTERACT.value)
        controls_menu.add.vertical_margin(20)
        controls_menu.add.label(STRINGS.MECHANICS_HEADER.value)
        controls_menu.add.label(STRINGS.MECHANIC_SHADOWS.value)
        controls_menu.add.label(STRINGS.MECHANIC_DETECTION.value)
        controls_menu.add.vertical_margin(25)
        controls_menu.add.button(
            STRINGS.BTN_VOLVER.value, pygame_menu.events.BACK)

        return controls_menu

    @classmethod
    def menu_loop(cls, run_game):
        """
        Ejecuta el bucle principal del menú
        """
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load(ASSETS.MENU_MUSIC.value)
        pygame.mixer.music.play(-1)
        pygame.display.set_caption(STRINGS.TITLE_VENTANA.value)
        clock = pygame.time.Clock()

        # Configurar sonidos del menú
        menu_sound = pygame_menu.sound.Sound()
        menu_sound.set_sound(pygame_menu.sound.SOUND_TYPE_WIDGET_SELECTION,
                             str(ASSETS.SELECTION_SOUND.value))

        # Calcular dimensiones
        window_height = int(
            CONSTANTES.WINDOW_SIZE.value[1] * CONSTANTES.WINDOW_SCALE.value)
        window_width = int(
            CONSTANTES.WINDOW_SIZE.value[0] * CONSTANTES.WINDOW_SCALE.value)

        # Crear menús
        controls_menu = cls.create_controls_menu(window_width, window_height)

        main_menu = cls.create_menu(
            title=STRINGS.TITLE_VENTANA.value,
            width=window_width,
            height=window_height,
            onclose=pygame_menu.events.EXIT
        )

        def start_game():
            # Fade out music
            pygame.mixer.music.fadeout(500)

            # Run the game
            continue_menu = run_game()

            # When game returns, restart menu music
            pygame.mixer.music.load(ASSETS.MENU_MUSIC.value)
            pygame.mixer.music.play(-1)

            # Return to menu
            return continue_menu

        main_menu.add.button(STRINGS.BTN_BEGIN_INFILTRATION.value, start_game)
        main_menu.add.button(
            STRINGS.BTN_INFILTRATION_GUIDE.value, controls_menu)
        main_menu.add.button(STRINGS.BTN_EXIT_MISSION.value,
                             pygame_menu.events.EXIT)

        # Asignar sonidos
        main_menu.set_sound(menu_sound)
        controls_menu.set_sound(menu_sound)
        cls.set_button_sounds(main_menu, menu_sound)
        cls.set_button_sounds(controls_menu, menu_sound)

        running = True
        while running:
            clock.tick(CONSTANTES.FPS.value)
            cls.main_background()
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False

            if main_menu.is_enabled():
                main_menu.mainloop(cls.surface, cls.main_background)

            pygame.display.flip()
        exit()
