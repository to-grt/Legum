import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from legum.components.Piece import Piece
# Also try importing via package
from legum.components import Piece as Piece_from_pkg

print('Imported Piece from module:', Piece)
print('Type of Piece:', type(Piece))
print('Piece from package import:', Piece_from_pkg)
print('Type piece from package:', type(Piece_from_pkg))

try:
    p = Piece(board=None, name='King', color='white', position=(0,0), is_alive=True)
    print('Created instance:', p)
except Exception as e:
    print('Error when instantiating Piece:', e)

