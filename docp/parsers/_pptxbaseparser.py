#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides generalised base functionality for
            parsing PPTX documents.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

.. attention::

            This module is *not* designed to be interacted with
            directly, only via the appropriate interface class(es).

            Rather, please create an instance of a PPTX document parsing
            object using the following:

                - :class:`~docp.parsers.pptxparser.PPTXParser`

"""
# pylint: disable=protected-access

import os
from pptx import Presentation
# locals
try:
    from libs.utilities import utilities
    from objects.pptxobject import DocPPTX
except ImportError:
    from .libs.utilities import utilities
    from .objects.pptxobject import DocPPTX


class _PPTXBaseParser:
    """Base class containing generalised PPTX parsing functionality."""

    def __init__(self, path: str):
        """Private base parser class initialiser.

        Args:
            path (str): Full path to the document to be parsed.

        """
        self._path = path
        self._doc = DocPPTX()
        self._set_paths()
        self._open()

    @property
    def doc(self) -> DocPPTX:
        """Accessor to the document object."""
        return self._doc

    def _open(self) -> None:
        """Open the PPTX document for reading.

        Before opening the file, a test is performed to ensure the PPTX
        is valid. The file must:

            - exist
            - be a ZIP archive, per the file signature
            - have a .pptx file extension

        :Other Operations:

            - Store the ``pptx.Presentation`` parser object returned
              from the :func:`pptx.Presentation` instance creation into
              the :attr:`self._doc._parser` attribute.
            - Store the number of pages into the
              :attr:`self._doc._npages` attribute.
            - Store the document's meta data into the
              :attr:`self._doc._meta` attribute.

        Raises:
            TypeError: Raised if the file type criteria above are not
            met.

        """
        if all((os.path.exists(self._doc._fpath),
                utilities.iszip(self._doc._fpath),
                os.path.splitext(self._doc._fpath)[1].lower() == '.pptx')):
            self._doc._parser = Presentation(self._doc._fpath)
            self._doc._npages = len(self._doc._parser.slides)
            self._doc._meta = self._doc._parser.core_properties
        else:
            msg = f'{self._doc._fname} is not a valid PPTX file.'
            raise TypeError(msg)

    def _set_paths(self) -> None:
        """Set the document's file path attributes."""
        self._doc._fpath = os.path.realpath(self._path)
        self._doc._fname = os.path.basename(self._path)
