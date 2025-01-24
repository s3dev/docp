#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the 'PPTX Document' object structure
            into which MS PowerPoint documents are parsed into for
            transport and onward use.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

"""

try:
    from .objects._docbaseobject import _DocBase
    from .objects._slideobject import SlideObject
except ImportError:
    from objects._docbaseobject import _DocBase
    from objects._slideobject import SlideObject


class DocPPTX(_DocBase):
    """Container class for storing data parsed from a PPTX file."""

    def __init__(self):
        """PPTX document object class initialiser."""
        super().__init__()
        self._slides = [SlideObject(pageno=0)]

    @property
    def slides(self) -> list[SlideObject]:
        """A list of containing an object for each slide in the document.

        .. tip::

            The slide number index aligns to the slide number in the
            PPTX file.

            For example, to access the ``SlideObject`` for side 42, use::

                slides[42]

       """
        return self._slides
