#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the entry point for loading a document
            into a Chroma database.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

:Example:   For example code use, please refer to the :class:`LoadChroma`
            class docstring.

"""
# pylint: disable=import-error
# pylint: disable=wrong-import-position

import os
import sys
# Set sys.path for relative imports.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import re
from glob import glob
# locals
from loaders._chromabase import _LoadChromaBase


class LoadChroma(_LoadChromaBase):
    """Chroma database document loader.

    Args:
        path (str): Full path to the file (or *directory*) to be parsed
            and loaded. Note: If this is a directory, a specific file
            extension can be passed into the :meth:`load` method using
            the ``ext`` argument.
        db (str): Full path to the Chroma database *directory*.
        collection (str): Name of the Chroma database collection into
            which the data is to be loaded.

    :Example:

        Parse and load a *single* document into a Chroma database
        collection::

            >>> from docp import LoadChroma

            >>> l = LoadChroma(path='/path/to/file.pdf',
                               db='/path/to/chroma',
                               collection='spam')
            >>> l.load()


        Parse and load a *directory* of PDF documents into a Chroma
        database collection::

            >>> from docp import LoadChroma

            >>> l = LoadChroma(path='/path/to/directory',
                               db='/path/to/chroma',
                               collection='spam')
            >>> l.load(ext='pdf')

    """

    def __init__(self, path: str, db: str, collection: str):
        """Chroma database loader class initialiser."""
        super().__init__(db=db, collection=collection)
        self._path = path

    def load(self,
             *,
             ext: str='**',
             recursive: bool=True,
             remove_header: bool=True,
             remove_footer: bool=True,
             remove_newlines: bool=True,
             ignore_tags: set=None,
             convert_to_ascii: bool=True) -> None:
        """Load a document (or documents) into a Chroma database.

        Args:
            ext (str): If the ``path`` argument refers to a *directory*,
                a specific file extension can be specified here.
                For example::

                    ext = 'pdf'

                If anything other than ``'**'`` is provided, all
                alpha-characters are parsed from the string, and prefixed
                with ``*.``. Meaning, if ``'.pdf'`` is passed, the
                characters ``'pdf'`` are parsed and prefixed with ``*.``
                to create ``'*.pdf'``. However, if ``'things.foo'`` is
                passed, the derived extension will be ``'*.thingsfoo'``.
                Defaults to '**', for a recursive search.

            recursive (bool, optional): If True, subdirectories are
                searched. Defaults to True.
            remove_header (bool, optional): Attempt to remove the header
                from each page. Defaults to True.
            remove_footer (bool, optional): Attempt to remove the footer
                from each page. Defaults to True.
            remove_newlines (bool, optional): Replace newline characters
                with a space. Defaults to True, as this helps with
                document chunk splitting.
            ignore_tags (set, optional): If provided, these are the
                PDF 'marked content' tags which will be ignored. Note
                that the PDF document must contain tags, otherwise the
                bounding box method is used and this argument is ignored.
                Defaults to ``{'Artifact'}``, as these generally
                relate to a header and/or footer. To include all tags,
                (not skip any) pass this argument as ``'na'``.
            convert_to_ascii (bool, optional): Convert all characters to
                ASCII. Defaults to True.

        """
        if os.path.isdir(self._path):
            if ext != '**':
                ext = f'*.{re.findall("[a-zA-Z]+", ext)[0]}'
            files = glob(os.path.join(self._path, ext), recursive=recursive)
            count = len(files)
            for idx, f in enumerate(files, 1):
                print(f'\nProcessing {idx} of {count}: {os.path.basename(f)}')
                self._load(path=f)
        else:
            print(f'Processing: {os.path.basename(self._path)} ...')
            self._load(path=self._path,
                       remove_header=remove_header,
                       remove_footer=remove_footer,
                       remove_newlines=remove_newlines,
                       ignore_tags=ignore_tags,
                       convert_to_ascii=convert_to_ascii)
