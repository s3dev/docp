#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module serves as the public interface for interacting
            with PDF files and parsing their contents.

:Platform:  Linux
:Developer: J Berendt
:Email:     jeremy.berendt@rolls-royce.com

:Comments:  n/a

:Example:   For example code use, please refer to the :class:`ParsePDF`
            class docstring.

"""
# pylint: disable=import-error
# pylint: disable=wrong-import-position

import os
import sys
# Set sys.path for relative imports.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
# locals
from parsers._pdftable import _ParsePDFTable
from parsers._pdftext import _ParsePDFText


class ParsePDF(_ParsePDFTable, _ParsePDFText):
    """PDF document parser.

    Args:
        path (str): Full path to the PDF document to be parsed.

    :Example:

        Extract text from a PDF file::

            >>> from docutils import ParsePDF

            >>> path = '/path/to/myfile.pdf'
            >>> pdf = ParsePDF(path)
            >>> pdf.extract_text()

            >>> text = pdf.doc.text


        Extract tables from a PDF file::

            >>> from docutils import ParsePDF

            >>> path = '/path/to/myfile.pdf'
            >>> pdf = ParsePDF(path)
            >>> pdf.extract_tables()

            >>> tables = pdf.doc.tables

    """

    def __init__(self, path: str):
        """PDF parser class initialiser."""
        super().__init__(path=path)
