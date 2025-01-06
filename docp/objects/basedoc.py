#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the 'Base Document' object structure
            which is inherited by the type-specific document classes.

:Platform:  Linux
:Developer: J Berendt
:Email:     jeremy.berendt@rolls-royce.com

:Comments:  n/a

"""

import os


class _BaseDoc:
    """Private document base class.

    This class is *not* designed to be interacted with directly, but
    rather forms the basis for the type-specific document objects.

    """

    def __init__(self):
        """Base document object class initialiser."""
        self._base = None
        self._common = None
        self._meta = None
        self._npages = None
        self._ntables = None
        self._path = None
        self._tables = []
        self._text = []

    @property
    def basename(self):
        """Accessor for the file's basename."""
        return self._base

    @property
    def filepath(self):
        """Accessor for the explicit path to this file."""
        return os.path.realpath(self._path)

    @property
    def metadata(self):
        """The meta data as extracted from the document."""
        return self._meta

    @property
    def npages(self):
        """The number of pages successfully extracted from the source."""
        return self._npages

    @property
    def ntables(self):
        """The number of tables successfully extracted from the source."""
        return len(self._tables)

    @property
    def tables(self):
        """Accessor to a list containing the extracted table data."""
        return self._tables

    @property
    def text(self):
        """A list of containing the text extracted from the document."""
        return self._text
