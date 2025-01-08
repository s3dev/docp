#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the project initilisation logic.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

# Bring entry-points to the surface.
try:
    from loaders.chroma import LoadChroma
except ImportError as err:
    # The chroma loader requires a lot of backend which is not required for the parser.
    msg = f'An error occurred while importing the Chroma loader:\n- {err}'
    raise ImportError(msg) from err

try:
    from .parsers.pdfparser import PDFParser
    from ._version import __version__
except ImportError:
    from parsers.pdfparser import PDFParser
    from _version import __version__
