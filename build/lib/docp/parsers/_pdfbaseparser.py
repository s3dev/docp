#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides generalised base functionality for
            parsing PDF documents.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

Note:       This module is *not* designed to be interacted with
            directly, only via the appropriate interface class(es).

            Rather, please create an instance of a PDF document parsing
            object using the following:

                - :class:`pdfparser.PDFParser`

"""
# pylint: disable=import-error
# pylint: disable=protected-access
# pylint: disable=wrong-import-order

import os
import pdfplumber
from collections import Counter
from unidecode import unidecode
# locals
from objects.pdfobject import DocPDF


class _PDFBaseParser:
    """Base class containing generalised PDF parsing functionality."""

    def __init__(self, path: str):
        """Private base parser class initialiser.

        Args:
            path (str): Full path to the document to be parsed.

        """
        self._path = path
        self._doc = DocPDF()
        self._tbl_opath = None
        self._set_paths()
        self._open()

    def __del__(self):
        """Class deconstructor.

        :Tasks:
            - Ensure the PDF document is closed.

        """
        if hasattr(self._doc, '_parser'):
            self._doc._parser.close()

    @property
    def doc(self) -> DocPDF:
        """Accessor to the document object."""
        return self._doc

    def _get_crop_coordinates(self,
                              skip_header: bool=False,
                              skip_footer: bool=False) -> tuple[float]:
        """Determine the bounding box coordinates.

        These coordinates are used for removing the header and/or footer.

        Args:
            skip_header (bool, optional): If True, set the coordinates
                such that the header is skipped. Defaults to False.
            skip_footer (bool, optional): If True, set the coordinates
                such that the footer is skipped. Defaults to False.

        :Logic:
            When excluding a header and/or footer, the following page
            numbers are used for header/footer *position* detection,
            given the length of the document:

                - Number of pages [1]: 1
                - Number of pages [2,10]: 2
                - Number of pages [11,]: 5

        Returns:
            tuple: A bounding box tuple of the following form, to be
            passed directly into the :func:`Page.crop` method::

                (x0, top, x1, bottom)

        """
        npages = self._doc.npages
        match npages:
            case 1: num = 1
            case _ if npages in range(2, 11): num = 2
            case _: num = 5
        pg = self._doc.parser.pages[num]  # The pages list has a has a page offset at [0].
        # Default coordinates to the whole page.
        coords = {'x0': 0, 'top': 0, 'x1': pg.width, 'bottom': pg.height}
        # If the header and/or footer is to be skipped, find and iterate
        # through the common lines and overwrite the coordinates as
        # appropriate, given the key and the line's location on the page.
        if skip_header or skip_footer:
            lines = self._scan_common()
            for line in lines:
                s = pg.search(line)
                if s:
                    for key in coords:
                        v = s[0][key]
                        match key:
                            case 'top' if v < pg.height/2 and skip_header:
                                coords[key] = max(coords[key], v+2)
                            case 'bottom' if v > pg.height/2 and skip_footer:
                                coords[key] = min(coords[key], v-2)
        return tuple(coords.values())

    def _open(self) -> None:
        """Open the PDF document for reading.

        :Other Operations:

            - Store the ``pdfplumber`` parser object returned from the
              :func:`pdfplumber.open` function into the
              :attr:`self._doc._parser` attribute.
            - Store the number of pages into the
              :attr:`self._doc._npages` attribute.
            - Store the document's meta data into the
              :attr:`self._doc._meta` attribute.

        """
        self._doc._parser = pdfplumber.open(self._doc._fpath)
        self._doc._npages = len(self._doc._parser.pages)
        self._doc._meta = self._doc._parser.metadata

    @staticmethod
    def _prepare_row(row: list) -> str:
        """Prepare the table row for writing a table to to CSV.

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
        trans = {34: '', 8220: '', 8221: ''}  # Remove double quotes in Unicode.
        row = [e.translate(trans) if e else 'None' for e in row]  # Cannot be a generator.
        for idx, e in enumerate(row):
            if ',' in e:
                row[idx] = f'"{e}"'  # Escape comma-separation by quoting.
        line = unidecode(','.join(row).replace('\n', ' '), errors='replace', replace_str='?')
        return line

    def _scan_common(self) -> list[str]:
        """Scan the PDF document to find the most common lines.

        :Rationale:
            Generally, the most common lines in a document will be the
            header and footer, as these are expected to be repeated on
            each page of the document.

            'Most common' is defined as line occurring on 90% of the
            pages throughout the document. Therefore, only documents with
            more than three pages are scanned. Otherwise, the 90% may
            exclude relevant pieces of the document (as was discovered in
            testing).

        :Logic:
            For documents with more than three pages, the entire PDF is
            read through and each line extracted. The occurrence of each
            line is counted, with the most common occurrences returned
            to the caller.

            The returned lines are to be passed into a page search to
            determine the x/y coordinates of the header and footer.

        Returns:
            list: For documents with more than three pages, a list
            containing the most common lines in the document. Otherwise,
            an empty list if returned.

        """
        # Only scan if document has more than three pages.
        if self._doc.npages < 4:
            return []
        if self._doc.common is None:
            # Create a line generator for all pages.
            lines = (l for p in self._doc.parser.pages for l in p.extract_text().split('\n'))
            # Return the lines whose occurrence rate is 90% of document pages.
            self._doc._common = [i[0] for i in Counter(lines).most_common()
                                 if i[1] > self._doc.npages * 0.9]
        return self._doc.common

    def _set_paths(self) -> None:
        """Set the document's file path attributes."""
        self._doc._fpath = os.path.realpath(self._path)
        self._doc._fname = os.path.basename(self._path)
