#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the generalised base functionality for
            the document-type-specific base classes.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

"""


class _DocBase:
    """Private document base class.

    .. attention::

        This class is *not* designed to be interacted with directly, but
        rather to be inherited by the document-type-specific document
        objects.

    """

    def __init__(self):
        """Base document object class initialiser."""
        self._common = None     # Used by the header/footer scanner.
        self._fname = None      # Filename (basename)
        self._fpath = None      # Full file path
        self._meta = None       # Metadata from the document parger
        self._npages = 0        # Number of pages in the document
        self._ntables = 0       # Number of tables extracted
        self._parser = None     # Underlying document parser functionality

    @property
    def basename(self) -> str:
        """Accessor for the file's basename."""
        return self._fname

    @property
    def filepath(self) -> str:
        """Accessor for the explicit path to this file."""
        return self._fpath

    @property
    def metadata(self) -> dict | object:
        """The meta data as extracted from the document."""
        return self._meta

    @property
    def npages(self) -> int:
        """The number of pages successfully extracted from the source."""
        return self._npages

    @property
    def ntables(self) -> int:
        """The number of tables successfully extracted from the source."""
        return self._ntables

    @property
    def parser(self) -> object:
        """Accessor to the underlying document parser's functionality."""
        return self._parser
