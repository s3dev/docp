#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides generalised functionality for parsing
            PDF documents.

:Platform:  Linux
:Developer: J Berendt
:Email:     jeremy.berendt@rolls-royce.com

Note:       This module is *not* designed to be interacted with
            directly, only via the appropriate interface class(es).

"""
# pylint: disable=import-error
# pylint: disable=protected-access
# pylint: disable=wrong-import-order

import os
import pdfplumber
from collections import Counter
from unidecode import unidecode
# locals
from objects.pdfdoc import PDFDoc


class _ParsePDFBase:
    """Base class containing generalised PDF parsing functionality."""

    def __init__(self, path: str):
        """Private base parser class initialiser.

        Args:
            path (str): Full path to the document to be parsed.

        """
        self._path = path
        self._doc = PDFDoc()
        self._table_opath = None
        self._set_path()
        self._open()

    def __del__(self):
        """Class deconstructor.

        :Tasks:
            - Ensure the PDF document is closed.

        """
        if self._doc:
            self._doc._pdf.close()

    @property
    def doc(self):
        """Accessor to the document object."""
        return self._doc

    def _get_crop_coordinates(self,
                              skip_header: bool=True,
                              skip_footer: bool=True) -> tuple[float]:
        """Determine the bounding box coordinates.

        These coordinates are used for removing the header and footer.

        Args:
            skip_header (bool, optional): If True, set the coordinates
                such that the header is skipped. Defaults to True.
            skip_footer (bool, optional): If True, set the coordinates
                such that the footer is skipped. Defaults to True.

        Returns:
            tuple: A bounding box tuple of the following form, to be
            passed directly into the :func:`Page.crop` method::

                (x0, top, x1, bottom)

        """
        # pylint: disable=invalid-name
        # Use page 2 as a template for locating the header and footer.
        p2 = self._doc._pdf.pages[1]
        # Default coordinates to the whole page.
        coords = {'x0': 0, 'top': 0, 'x1': p2.width, 'bottom': p2.height}
        lines = self._scan_common()
        # Iterate through the common lines and overwrite the coordinates
        # as appropriate, given the key and the line's location on the page.
        for line in lines:
            s = p2.search(line)[0]
            for key in coords:
                v = s[key]
                match key:
                    case 'top' if v < p2.height/2 and skip_header:
                        coords[key] = max(coords[key], v+2)
                    case 'bottom' if v > p2.height/2 and skip_footer:
                        coords[key] = min(coords[key], v-2)
        return tuple(coords.values())

    def _open(self):
        """Open the PDF document for reading.

        :Other Operations:

            - Store the ``pdf`` object returned from the
              :func:`pdfplumber.open` function into the
              :attr:`self._doc._pdf` attribute.
            - Store the number of pages is stored into the
              :attr:`self._doc._npages` attribute.
            - Store the document's meta data into the
              :attr:`self._doc._meta` attribute.

        """
        self._doc._pdf = pdfplumber.open(self._doc._path)
        self._doc._meta = self._doc._pdf.metadata
        self._doc._npages = len(self._doc._pdf.pages)

    @staticmethod
    def _prepare_row(row: list) -> str:
        """Prepare the row for writing to CSV.

        Args:
            row (list): A list of strings, constituting a table row.

        :Processing Tasks:

            For each element in the row:

                - Remove any double quote characters (ASCII and Unicode).
                - Replace any empty values with ``'None'``.
                - If the element contains a comma, wrap the element in
                  double quotes.
                - Attempt to convert any non-ASCII characters to an
                  associated ASCII character. If the replacement cannot
                  be made, the character is replaced with a ``'?'``.

        Returns:
            str: A processed comma-separated string, ready to be written
            to a CSV file.

        """
        trans = {34: '', 8220: '', 8221: ''}  # Remove double quotes.
        row = [e.translate(trans) if e else 'None' for e in row]
        for idx, e in enumerate(row):
            if ',' in e:
                row[idx] = f'"{e}"'
        line = unidecode(','.join(row).replace('\n', ' '), errors='replace', replace_str='?')
        return line

    def _scan_common(self) -> list[str]:
        """Scan the PDF document to find the most common lines.

        :Rationale:
            The most common lines in a document will be the header and
            footer, as these are repeated on each page of the document.

            'Most common' is defined as line occurring on 90% of the
            pages throughout the document.

        :Logic:
            The entire PDF is read through and each line extracted. The
            occurrence of each line is counted, with the most common
            occurrences returned to the caller.

            The returned lines are to be passed into a page search to
            determine the x/y coordinates of the header and footer.

        Returns:
            list: A list containing the most common lines in the
            document.

        """
        if self._doc._common is None:
            # Create a line generator for all pages.
            lines = (l for p in self._doc._pdf.pages for l in p.extract_text().split('\n'))
            # Return the lines whose occurrence rate is 90% of document pages.
            self._doc._common = [i[0] for i in Counter(lines).most_common()
                                 if i[1] > self._doc._npages * 0.9]
        return self._doc._common

    def _set_path(self):
        """Set the parser's file path attributes."""
        self._doc._path = self._path
        self._doc._base = os.path.basename(self._path)
