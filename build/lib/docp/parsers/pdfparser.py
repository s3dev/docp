#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module serves as the public interface for interacting
            with PDF files and parsing their contents.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

:Example:   For example code usage, please refer to the
            :class:`PDFParser` class docstring.

"""
# pylint: disable=import-error
# pylint: disable=wrong-import-position

# Set sys.path for relative imports.
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
# locals
from parsers._pdftableparser import _PDFTableParser
from parsers._pdftextparser import _PDFTextParser


class PDFParser(_PDFTableParser, _PDFTextParser):
    """PDF document parser.

    Args:
        path (str): Full path to the PDF document to be parsed.

    :Example:

        Extract text from a PDF file::

            >>> from docp import PDFParser

            >>> pdf = PDFParser(path='/path/to/myfile.pdf')
            >>> pdf.extract_text()

            # Access the content of page 1.
            >>> pg1 = pdf.doc.pages[1].content


        Extract tables from a PDF file::

            >>> from docp import PDFParser

            >>> pdf = PDFParser('/path/to/myfile.pdf')
            >>> pdf.extract_tables()

            # Access the first table on page 1.
            >>> tbl1 = pdf.doc.pages[1].tables[1]

    """

    def __init__(self, path: str):
        """PDF parser class initialiser."""
        super().__init__(path=path)
