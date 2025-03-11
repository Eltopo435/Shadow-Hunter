# Sergio Gabriel Pérez A.
# 23-EISN-2-028

from pathlib import Path
from utils.assets import ASSETS
from typing import List, Tuple
import os


class Setup:
    # Códigos de color ANSI
    COLORS = {
        'GREEN': '\033[92m',
        'RED': '\033[91m',
        'YELLOW': '\033[93m',
        'BLUE': '\033[94m',
        'RESET': '\033[0m'
    }

    @staticmethod
    def validate_assets() -> bool:
        """
        Valida todos los recursos requeridos del juego.

        Realiza una validación completa de los recursos del juego incluyendo:
        - Existencia del archivo
        - Permisos del archivo
        - Integridad básica del archivo

        Returns:
            bool: True si todos los recursos son válidos, False en caso contrario
        """
        missing_assets: List[Tuple[str, str, str]
                             ] = []  # (nombre, ruta, razón)
        total_assets = len(
            [asset for asset in ASSETS if asset.name != 'ASSETS_DIR'])
        validated = 0

        print(
            f"\n{Setup.COLORS['BLUE']}Validando recursos del juego...{Setup.COLORS['RESET']}")

        for asset_enum in ASSETS:
            if asset_enum.name == 'ASSETS_DIR':
                continue

            asset_path = asset_enum.value
            validated += 1
            print(
                f"\rProgreso: {validated}/{total_assets} recursos revisados", end="")

            if not isinstance(asset_path, Path):
                missing_assets.append((
                    asset_enum.name,
                    str(asset_path),
                    "Tipo de ruta inválido"
                ))
                continue

            if not asset_path.exists():
                missing_assets.append((
                    asset_enum.name,
                    str(asset_path),
                    "Archivo no encontrado"
                ))
                continue

            if not os.access(asset_path, os.R_OK):
                missing_assets.append((
                    asset_enum.name,
                    str(asset_path),
                    "Archivo no legible"
                ))
                continue

            if asset_path.stat().st_size == 0:
                missing_assets.append((
                    asset_enum.name,
                    str(asset_path),
                    "Archivo está vacío"
                ))

        print()  # Nueva línea después del progreso

        if missing_assets:
            print(
                f"\n{Setup.COLORS['RED']}ERROR: ¡Falló la validación de recursos!{Setup.COLORS['RESET']}")
            print(
                f"{Setup.COLORS['YELLOW']}Los siguientes recursos tienen problemas:{Setup.COLORS['RESET']}")
            for name, path, reason in missing_assets:
                print(f"\n- {name}:")
                print(f"\n  Ruta: {path}")
                print(f"\n  Problema: {reason}")
            print(
                f"\n{Setup.COLORS['YELLOW']}Por favor, resuelva estos problemas antes de ejecutar el juego.{Setup.COLORS['RESET']}")
            return False

        print(
            f"\n{Setup.COLORS['GREEN']}✓ ¡Todos los recursos validados exitosamente!{Setup.COLORS['RESET']}")
        print(
            f"{Setup.COLORS['GREEN']}✓ Juego iniciado...{Setup.COLORS['RESET']}")
        return True
