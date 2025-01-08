#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the 'PDF Document' object structure into
            which PDF documents are parsed into for transport and onward
            use.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

"""
# pylint: disable=import-error

from objects._docbaseobject import _DocBase


class DocPDF(_DocBase):
    """Container class for storing data parsed from a PDF file."""

    def __init__(self):
        """PDF document object class initialiser."""
        super().__init__()
        self._tags = False

    @property
    def parsed_using_tags(self) -> bool:
        """Flag indicating if the document was parsed using tags.

        PDF documents can be created with 'marked content' tags. When
        a PDF document is parsed using tags, as this flag indicates, the
        parser respects columns and other page formatting schemes. If a
        multi-column page is parsed without tags, the parser reads
        straight across the line, thus corrupting the text.

        """
        return self._tags
