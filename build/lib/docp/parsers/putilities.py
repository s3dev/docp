#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides parser-specific utility functions for
            the project.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

"""

# locals
try:
    from .libs.utilities import utilities
    from .parsers.pdfparser import PDFParser
    from .parsers.pptxparser import PPTXParser
except ImportError:
    from libs.utilities import utilities
    from parsers.pdfparser import PDFParser
    from parsers.pptxparser import PPTXParser


class ParserUtilities:
    """Parser-based (cross-project) utility functions."""

    def get_parser(self, path: str) -> PDFParser | PPTXParser:
        """Return the appropriate parser for the file type.

        Args:
            path (str): Full path to the file to be tested.

        Returns:
            PDFParser | PPTXParser: The appropriate parser for the file,
            given the *file signature*; this test is not file extension
            based.

        """
        if utilities.ispdf(path=path):
            return PDFParser
        if utilities.iszip(path=path):
            return PPTXParser
        raise NotImplementedError('A parser is not available for: os.path.basename(path)')


putilities = ParserUtilities()
