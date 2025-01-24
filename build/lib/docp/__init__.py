#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the project initilisation logic.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  Ths loader modules/classes have *not* been imported due to the
            heavy dependency requirements. Refer to the loaders/__init__.py
            module instead.

"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from utils4.user_interface import ui
# locals
from .libs._version import __version__

# TODO: Change these to use logging.

# Bring entry-points to the surface.
try:
    from .parsers.pdfparser import PDFParser
except ImportError as err:
    msg = ( 'An error occurred while importing the PDF parser:\n'
           f'- {err}\n'
            '  - This can be ignored if the parser is not in use.\n')
    ui.print_warning(f'\n[ImportError]: {msg}')

try:
    from .parsers.pptxparser import PPTXParser
except ImportError as err:
    msg = ( 'An error occurred while importing the PPTX parser:\n'
           f'- {err}\n'
            '  - This can be ignored if the parser is not in use.\n')
    ui.print_warning(f'\n[ImportError]: {msg}')
