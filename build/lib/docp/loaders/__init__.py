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
from utils4.user_interface import ui

# TODO: Change these to use logging.

# Bring entry-points to the surface.
try:
    from .chromapdfloader import ChromaPDFLoader
except ImportError as err:
    # The chroma loader requires a lot of backend which is not required for the parser.
    msg = ( 'An error occurred while importing the Chroma PDF loader:\n'
           f'- {err}\n'
            '  - This can be ignored if the loader is not in use.\n')
    ui.print_warning(f'\n[ImportError]: {msg}')

try:
    from .chromapptxloader import ChromaPPTXLoader
except ImportError as err:
    # The chroma loader requires a lot of backend which is not required for the parser.
    msg = ( 'An error occurred while importing the Chroma PPTX loader:\n'
           f'- {err}\n'
            '  - This can be ignored if the loader is not in use.\n')
    ui.print_warning(f'\n[ImportError]: {msg}')
