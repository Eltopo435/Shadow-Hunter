# Sergio Gabriel Pérez A.
# 23-EISN-2-028

import pygame
from utils.theme import Theme
from utils.setup import Setup
from Game.game import Game


def run_game():
    # pygame.mixer.music.stop()

    try:
        # Crear y ejecutar el juego
        game = Game()
        game.run()
    except Exception as e:
        print(f"Error durante la ejecución del juego: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Inicializar pygame si es necesario
    if not pygame.get_init():
        pygame.init()

    # Validar assets antes de inicializar pygame
    if not Setup.validate_assets():

    try:
        # Si quieres saltarte el menú y probar directamente el juego:
        # run_game()

        # O usar el menú normalmente:
        surface = Theme.initialize()
        Theme.menu_loop(run_game)
    except Exception as e:
        import traceback
        traceback.print_exc()
