#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module serves as the public interface for interacting
            with PPTX files and parsing their contents.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

:Example:   For example code usage, please refer to the
            :class:`PPTXParser` class docstring.

"""

# Set sys.path for relative imports.
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
# locals
try:
    from .parsers._pptxtextparser import _PPTXTextParser
except ImportError:
    from parsers._pptxtextparser import _PPTXTextParser


class PPTXParser(_PPTXTextParser):
    """PPTX document parser.

    Args:
        path (str): Full path to the PPTX document to be parsed.

    :Example:

        Extract text from a PPTX file::

            >>> from docp import PPTXParser

            >>> pptx = PPTXParser(path='/path/to/myfile.pptx')
            >>> pptx.extract_text()

            # Access the text on slide 1.
            >>> pg1 = pptx.doc.slides[1].content

    """

    def __init__(self, path: str):
        """PPTX parser class initialiser."""
        super().__init__(path=path)
