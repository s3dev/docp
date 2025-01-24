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

try:
    from .objects._docbaseobject import _DocBase
    from .objects._pageobject import PageObject
except ImportError:
    from objects._docbaseobject import _DocBase
    from objects._pageobject import PageObject


class DocPDF(_DocBase):
    """Container class for storing data parsed from a PDF file."""

    def __init__(self):
        """PDF document object class initialiser."""
        super().__init__()
        self._tags = False
        # List of PageObjects, offset by 1 to align the index with page numbers.
        self._pages = [PageObject(pageno=0)]

    @property
    def pages(self) -> list[PageObject]:
        """A list of containing an object for each page in the document.

        .. tip::

            The page number index aligns to the page number in the PDF
            file.

            For example, to access the ``PageObject`` for page 42, use::

                pages[42]

       """
        return self._pages

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
