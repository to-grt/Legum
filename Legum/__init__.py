# Legum/__init__.py

# Imports
from Legum.Board import Board
from Legum.Piece import Piece

# Accessibility from package
__all__ = ['Board', 'Piece']

# Package version
__version__ = '0.1.0'

# Author of package
__author__ = 'Théo Gueuret'
__email__ = 'tgueuret@live.fr'

_initialized = False


# Package initialization
def initialize_package():
    global _initialized
    if not _initialized:
        print(f"initializing {__name__} package version {__version__}")
        _initialized = True


initialize_package()
