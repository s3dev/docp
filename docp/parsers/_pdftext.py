#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the logic for parsing text from a PDF
            document.

:Platform:  Linux
:Developer: J Berendt
:Email:     jeremy.berendt@rolls-royce.com

Note:       This module is *not* designed to be interacted with
            directly, only via the appropriate interface class(es).

"""
# pylint: disable=import-error
# pylint: disable=protected-access

from unidecode import unidecode
# locals
from parsers._pdfbase import _ParsePDFBase


class _ParsePDFText(_ParsePDFBase):
    """Private PDF document text parser intermediate class.

    Args:
        path (str): Full path to the PDF document.

    :Example:

        Extract text from a PDF file::

            >>> from docutils.parsers.pdf import ParsePDF

            >>> path = '/path/to/myfile.pdf'
            >>> pdf = ParsePDF(path)
            >>> pdf.extract_text()

            >>> text = pdf.doc.text

    """

    def extract_text(self,
                     remove_header: bool=True,
                     remove_footer: bool=True,
                     remove_newlines: bool=False,
                     ignore_tags: tuple=None,
                     convert_to_ascii: bool=True) -> list:
        """Extract text from the document.

        If the PDF document contains 'marked content' tags, the tags are
        used to extract the data. Otherwise, a bounding box method is
        used to detect the header/footer regions for exclusion, if
        instructed.

        The extracted text is returned to the caller as a list of
        strings, with each list element containing the content from the
        associated page, as a string.

        Additionally, this list of string is stored to the class'
        :attr:`self.text` attribute.

        Args:
            remove_header (bool, optional): If True, the header is
                cropped (skipped) from text extraction. This only applies
                to the bounding box extraction method. Defaults to True.
            remove_footer (bool, optional): If True, the footer is
                cropped (skipped) from text extraction. This only applies
                to the bounding box extraction method. Defaults to True.
            remove_newlines (bool, optional): If True, the newline
                characters are replaced with a space. Newline removal
                is *not* available if the tag-based extraction method is
                used to extract data. Defaults to False.
            ignore_tags (tuple, optional): If provided, these are the
                PDF 'marked content' tags which will be ignored. Note
                that the PDF document must contain tags, otherwise the
                bounding box method is used and this argument is ignored.
                Defaults to ``(None, 'Artifact')``, as these generally
                relate to a header and/or footer. To include all tags,
                (not skip any) pass this argument as ``'na'``.
            convert_to_ascii (bool, optional): When a non-ASCII character
                is found, an attempt is made to convert it to an
                associated ASCII character. If a character cannot be
                converted, it is replaced with a ``'?'``.
                Defaults to True.

        Returns:
            list: A list containing the text as extracted from the
            document, with one page per tuple element.

        """
        # pylint: disable=unnecessary-dunder-call
        if self._doc.text:
            # Reinitialise the doc object and reopen the document.
            self.__init__(path=self._path)
        if ignore_tags is None:
            ignore_tags = (None, 'Artifact')
        elif ignore_tags == 'na':
            ignore_tags = tuple()
        # Test is tags are found in the first 10 pages.
        # If tags are found, these are used for text extraction. If tags
        # are not found, a bounding box is used to remove the header and
        # footer, if instructed.
        tags = set(c['tag'] for p in self._doc._pdf.pages[:10] for c in p.chars)
        if tags != {None}:
            self._extract_text_using_tags(ignore_tags=ignore_tags)
        else:
            bbox = self._get_crop_coordinates(skip_header=remove_header, skip_footer=remove_footer)
            self._extract_text_using_bbox(bbox=bbox, remove_newlines=remove_newlines)
        if convert_to_ascii:
            for page in self._doc.text:
                page['content'] = unidecode(string=page['content'],
                                            errors='replace',
                                            replace_str='?')

    def _extract_text_using_bbox(self, **kwargs):
        """Extract text using a bbox for finding the header and footer.

       :Keyword Arguments:
            Those passed by the caller, :meth:`~extract_text`.

        """
        for page in self._doc._pdf.pages:
            text_ = page.within_bbox(bbox=kwargs['bbox']).extract_text().strip()
            if kwargs['remove_newlines']:
                text_ = text_.replace('\n', ' ')
            self._doc._text.append({'pageno': page.page_number, 'content': ''.join(text_).strip()})

    def _extract_text_using_tags(self, **kwargs):
        """Extract text using tags.

        The tags defined by the ``ignore_tags`` are skipped.

        :Keyword Arguments:
            Those passed by the caller, :meth:`~extract_text`.

        """
        for page in self._doc._pdf.pages:
            text_ = (c['text'] for c in page.chars if c['tag'] not in kwargs['ignore_tags'])
            # The removal of newlines is not an option with this read method.
            self._doc._text.append({'pageno': page.page_number, 'content': ''.join(text_).strip()})
