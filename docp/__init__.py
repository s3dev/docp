import os
import sys
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
# Bring entry-points to the surface.
try:
    from loaders.chroma import LoadChroma
except ImportError:
    # The chroma loader requires a lot of backend which is not required for the parser.
    pass  
from parsers.pdf import ParsePDF
from ._version import __version__
