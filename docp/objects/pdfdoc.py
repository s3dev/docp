#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the 'PDF Document' object structure into
            which PDF documents are parsed into for transport and onward
            use.

:Platform:  Linux
:Developer: J Berendt
:Email:     jeremy.berendt@rolls-royce.com

:Comments:  n/a

"""
# pylint: disable=import-error

from objects.basedoc import _BaseDoc


class PDFDoc(_BaseDoc):
    """Container class for storing data parsed from a PDF file."""

    def __init__(self):
        """PDF document object class initialiser."""
        super().__init__()
        self._pdf = None

    @property
    def pages(self):
        """Accessor to the document's ``pages`` object."""
        return self._pdf.pages
