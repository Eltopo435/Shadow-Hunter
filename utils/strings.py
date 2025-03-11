# Sergio Gabriel Pérez A.
# 23-EISN-2-028

from enum import Enum


class STRINGS (Enum):

    '''
    Textos que utiliza el juego centralizado en una misma clase
    '''

    # Textos de la interfaz
    TITLE_VENTANA = "      Shadow Hunter"
    MENU_TITLE = "Menu Principal"

    # Textos del menú de controles
    CONTROLS_TITLE = "GUIA DE INFILTRACION"
    CONTROLS_HEADER = "CONTROLES DE SIGILO:"
    CONTROL_MOVE = "MOVERSE - WASD"
    CONTROL_INTERACT = "INTERACTUAR - E"

    # Textos del menú de mecánicas
    MECHANICS_HEADER = "MECANICAS DE SIGILO:"
    MECHANIC_SHADOWS = "MANTENTE EN LAS ESCONDITES"
    MECHANIC_DETECTION = "DESACTIVA LAS TRAMPAS"

    # Textos de botones del menú principal
    BTN_BEGIN_INFILTRATION = "COMENZAR INFILTRACION"
    BTN_INFILTRATION_GUIDE = "GUIA DE INFILTRACION"
    BTN_EXIT_MISSION = "SALIR"
    BTN_VOLVER = "Volver"

    # Nuevos textos UI
    SHOW_HIDDEN_MESSAGE = "¡Estás oculto!"
    PURSUING_ALERT = "¡Te están persiguiendo!"
    TRAP_DEACTIVATED = "Trampa desactivada!"
    GAME_OVER_TITLE = "MISIÓN FALLIDA"
    VICTORY_TITLE = "MISIÓN CUMPLIDA"
    RESTART_INSTRUCTION = "Presiona R para intentar de nuevo"
    PAUSED_TITLE = "JUEGO PAUSADO"
    PAUSE_CONTINUE = "Presiona ESC para continuar"
    PAUSE_QUIT = "Presiona Q para salir al menú principal"

    # ? Aca se irán agregando según se vayan necesitando strings para la interfaz del juego
