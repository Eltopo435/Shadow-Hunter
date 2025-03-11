# Sergio Gabriel P?rez A.
# 23-EISN-2-028

from pathlib import Path
from enum import Enum
from utils.constantes import CONSTANTES

class ASSETS (Enum):
    '''
    Todas las constantes de los assets utilizados en el juego
    '''

    # Referencia al directorio de assets
    ASSETS_DIR = CONSTANTES.ASSETS_PATH.value

    # * Imagenes

    # ? Backgrounds
    BACKGROUND_MENU = ASSETS_DIR / 'image' / 'background' / 'background_menu_3.png'
    # background_menu_2.png / menu_background.png / background_menu_3.png

    # * Sprites

    # ? Personaje
    # Im?genes de personaje en estado idle mirando hacia arriba
    CHARACTER_IDLE_UP_1 = ASSETS_DIR / 'image' / 'Persons' / '11.png'
    CHARACTER_IDLE_UP_2 = ASSETS_DIR / 'image' / 'Persons' / '12.png'
    CHARACTER_IDLE_UP_3 = ASSETS_DIR / 'image' / 'Persons' / '13.png'
    CHARACTER_IDLE_UP_4 = ASSETS_DIR / 'image' / 'Persons' / '14.png'
    CHARACTER_IDLE_UP_5 = ASSETS_DIR / 'image' / 'Persons' / '15.png'

    # Im?genes de personaje atacando en estado idle mirando hacia arriba
    CHARACTER_IDLE_UP_ATTACK = ASSETS_DIR / 'image' / 'Persons' / '25.png'

    # Im?genes de personaje en estado idle mirando hacia abajo
    CHARACTER_IDLE_DOWN_1 = ASSETS_DIR / 'image' / 'Persons' / '4.png'
    CHARACTER_IDLE_DOWN_2 = ASSETS_DIR / 'image' / 'Persons' / '5.png'
    CHARACTER_IDLE_DOWN_3 = ASSETS_DIR / 'image' / 'Persons' / '6.png'
    CHARACTER_IDLE_DOWN_4 = ASSETS_DIR / 'image' / 'Persons' / '7.png'
    CHARACTER_IDLE_DOWN_5 = ASSETS_DIR / 'image' / 'Persons' / '10.png'

    # Im?genes de personaje atacando en estado idle mirando hacia abajo
    CHARACTER_IDLE_DOWN_ATTACK_1 = ASSETS_DIR / 'image' / 'Persons' / '27.png'
    CHARACTER_IDLE_DOWN_ATTACK_2 = ASSETS_DIR / 'image' / 'Persons' / '28.png'

    # Im?genes de personaje atacando en estado idle mirando hacia la izquierda
    CHARACTER_IDLE_LEFT_ATTACK_1 = ASSETS_DIR / 'image' / 'Persons' / '36.png'
    CHARACTER_IDLE_LEFT_ATTACK_2 = ASSETS_DIR / 'image' / 'Persons' / '37.png'

    # Im?genes de personaje en estado idle mirando hacia la derecha
    CHARACTER_IDLE_RIGHT_1 = ASSETS_DIR / 'image' / 'Persons' / '9.png'
    CHARACTER_IDLE_RIGHT_2 = ASSETS_DIR / 'image' / 'Persons' / '8.png'
    CHARACTER_IDLE_RIGHT_3 = ASSETS_DIR / 'image' / 'Persons' / '16.png'

    # Im?genes de personaje atacando en estado idle mirando hacia la derecha
    CHARACTER_IDLE_RIGHT_ATTACK_1 = ASSETS_DIR / 'image' / 'Persons' / '34.png'
    CHARACTER_IDLE_RIGHT_ATTACK_2 = ASSETS_DIR / 'image' / 'Persons' / '35.png'

    # Im?genes de personaje caminando hacia la izquierda
    CHARACTER_WALK_LEFT_1 = ASSETS_DIR / 'image' / 'Persons' / '33.png'
    CHARACTER_WALK_LEFT_2 = ASSETS_DIR / 'image' / 'Persons' / '19.png'
    CHARACTER_WALK_LEFT_3 = ASSETS_DIR / 'image' / 'Persons' / '20.png'
    CHARACTER_WALK_LEFT_4 = ASSETS_DIR / 'image' / 'Persons' / '28.png'
    CHARACTER_WALK_LEFT_5 = ASSETS_DIR / 'image' / 'Persons' / '29.png'

    # Im?genes de personaje caminando hacia la derecha
    CHARACTER_WALK_RIGHT_1 = ASSETS_DIR / 'image' / 'Persons' / '18.png'
    CHARACTER_WALK_RIGHT_2 = ASSETS_DIR / 'image' / 'Persons' / '32.png'
    CHARACTER_WALK_RIGHT_3 = ASSETS_DIR / 'image' / 'Persons' / '21.png'
    CHARACTER_WALK_RIGHT_4 = ASSETS_DIR / 'image' / 'Persons' / '22.png'

    # ? Enemigos
    # Im?genes de enemigo en estado idle
    ENEMY_IDLE_1 = ASSETS_DIR / 'image' / 'Enemy' / 'Golem_Armor_Idle' / '0.png'
    ENEMY_IDLE_2 = ASSETS_DIR / 'image' / 'Enemy' / 'Golem_Armor_Idle' / '1.png'
    ENEMY_IDLE_3 = ASSETS_DIR / 'image' / 'Enemy' / 'Golem_Armor_Idle' / '2.png'
    ENEMY_IDLE_4 = ASSETS_DIR / 'image' / 'Enemy' / 'Golem_Armor_Idle' / '3.png'

    # Im?genes de enemigo atacando
    ENEMY_ATTACK_1 = ASSETS_DIR / 'image' / 'Enemy' / 'Golem_Armor_AttackA' / '0.png'
    ENEMY_ATTACK_2 = ASSETS_DIR / 'image' / 'Enemy' / 'Golem_Armor_AttackA' / '1.png'
    ENEMY_ATTACK_3 = ASSETS_DIR / 'image' / 'Enemy' / 'Golem_Armor_AttackA' / '2.png'
    ENEMY_ATTACK_4 = ASSETS_DIR / 'image' / 'Enemy' / 'Golem_Armor_AttackA' / '3.png'

    # Im?genes de enemigo caminando
    ENEMY_WALK_1 = ASSETS_DIR / 'image' / 'Enemy' / 'Golem_Armor_Ability' / '0.png'
    ENEMY_WALK_2 = ASSETS_DIR / 'image' / 'Enemy' / 'Golem_Armor_Ability' / '1.png'
    ENEMY_WALK_3 = ASSETS_DIR / 'image' / 'Enemy' / 'Golem_Armor_Ability' / '2.png'
    ENEMY_WALK_4 = ASSETS_DIR / 'image' / 'Enemy' / 'Golem_Armor_Ability' / '3.png'

    # ? Objetos

    # * Map Tiles
    TILE_EMPTY = ASSETS_DIR / 'image' / 'tiles' / 'Tile_12.png'
    TILE_WALL = ASSETS_DIR / 'image' / 'tiles' / '4.png'
    TILE_HIDING = ASSETS_DIR / 'image' / 'tiles' / 'tile_hiding.png'
    TILE_TRAP = ASSETS_DIR / 'image' / 'tiles' / 'tile_trap.png'
    TILE_EXIT = ASSETS_DIR / 'image' / 'tiles' / 'tile_exit.png'
    TILE_DEACTIVATED = ASSETS_DIR / 'image' / 'tiles' / 'tile_deactivated.png'

    # * Fuentes

    # * Musica
    MENU_MUSIC = ASSETS_DIR / 'music' / 'music_menu.mp3'
    SELECTION_SOUND = ASSETS_DIR / 'sounds' / 'selection.mp3'

    # * Efectos de ataque
    ATTACK_EFFECT = ASSETS_DIR / 'image' / 'Persons' / '34.png'

    # * Efectos de sonido
    ATTACK_SOUND = ASSETS_DIR / 'sounds' / 'explosion.ogg'
    VICTORY_SOUND = ASSETS_DIR / 'sounds' / 'gamestart.ogg'  # Add victory sound asset
    GAME_OVER_SOUND = ASSETS_DIR / 'sounds' / 'gameover.ogg'  # Add game over sound asset
