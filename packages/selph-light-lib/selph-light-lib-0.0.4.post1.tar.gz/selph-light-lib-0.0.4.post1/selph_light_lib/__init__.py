import _selph_light_lib

from .pkginfo import __author__, __version__

assert _sepl_light_lib.__version__ == __version__, \
    ImportError(f"selph_light_lib {__version__} and _selph_light_lib {_selph_light_lib.__version__} version mismatch!")

import selph_light_lib.color as color
import selph_light_lib.wave as wave

from selph_light_lib.const import *
