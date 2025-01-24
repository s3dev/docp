#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides utility-based functionality for the
            project.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../'))
import re
from glob import glob
from utils4 import futils


class Utilities:
    """General (cross-project) utility functions."""

    @staticmethod
    def collect_files(path: str, ext: str, recursive: bool) -> list:
        """Collect all files for a given extension from a path.

        Args:
            path (str): Full path serving as the root for the search.
            ext (str, optional): If the ``path`` argument refers to a
                *directory*, a specific file extension can be specified
                here. For example: ``ext = 'pdf'``.

                If anything other than ``'**'`` is provided, all
                alpha-characters are parsed from the string, and prefixed
                with ``*.``. Meaning, if ``'.pdf'`` is passed, the
                characters ``'pdf'`` are parsed and prefixed with ``*.``
                to create ``'*.pdf'``. However, if ``'things.foo'`` is
                passed, the derived extension will be ``'*.thingsfoo'``.
                Defaults to '**', for a recursive search.

            recursive (bool): Instruct the search to recurse into
                sub-directories.

        Returns:
            list: The list of full file paths returned by the ``glob``
            call. Any directory-only paths are removed.

        """
        if ext != '**':
            ext = f'*.{re.findall("[a-zA-Z]+", ext)[0]}'
        return list(filter(os.path.isfile, glob(os.path.join(path, ext), recursive=recursive)))

    # !!!: Replace this with utils4.futils when available.
    @staticmethod
    def ispdf(path: str) -> bool:
        """Test the file signature. Verify this is a valid PDF file.

        Args:
            path (str): Path to the file being tested.

        Returns:
            bool: True if this is a valid PDF file, otherwise False.

        """
        with open(path, 'rb') as f:
            sig = f.read(5)
        return sig == b'\x25\x50\x44\x46\x2d'

    @staticmethod
    def iszip(path: str) -> bool:
        """Test the file signature. Verify this is a valid ZIP archive.

        Args:
            path (str): Path to the file being tested.

        Returns:
            bool: True if this is a valid ZIP archive, otherwise False.

        """
        return futils.iszip(path)

    @staticmethod
    def parse_to_keywords(resp: str) -> list:
        """Parse the bot's response into a list of keywords.

        Args:
            resp (str): Text response directly from the bot.

        Returns:
            list: A list of keywords extracted from the response,
            separated by asterisks as bullet points.

        """
        # Capture asterisk bullet points or a numbered list.
        rexp = re.compile(r'(?:\*|[0-9]+\.)\s*(.*)\n')
        trans = {45: ' ', 47: ' '}
        resp_ = resp.translate(trans).lower()
        kwds = rexp.findall(resp_)
        if kwds:
            return ', '.join(kwds)
        return ''


utilities = Utilities()
