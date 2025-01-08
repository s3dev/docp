#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the logic for parsing text from a PDF
            document.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

Note:       This module is *not* designed to be interacted with
            directly, only via the appropriate interface class(es).

            Rather, please create an instance of a PDF document parsing
            object using the following:

                - :class:`pdfparser.PDFParser`

Note:       **Multi-processing:**
            Text extraction through multi-processing has been tested and
            is not feesible due to an error indicating
            the ``pdfplumber.page.Page`` object can not be pickled. This
            object was being passed into the extraction method as the
            object contains the :func:`extract_text` function.

            Additionally, multi-threading has also been tested and
            it was determined to be too complex and inefficient. This was
            tested using the ``concurrent.futures.ThreadPoolExecutor``
            class and two documents, 14 and 92 pages; the timings are
            shown below. The multi-threaded approach took longer to
            process and added unnecessary complexity to the code base.
            As a side-effect, the pages are processed and stored out of
            order which would require a re-order, adding more complexity.

            It has therefore been determined that this module will remain
            single-threaded.

           **Multi-Thread Timings**

           **Single-threaded:**

                - 14 page document: ~2 seconds
                - 92 page document: ~32 seconds

           **Multi-threaded:**

                - 14 page document: ~2 seconds
                - 92 page document: ~35 seconds

"""
# pylint: disable=import-error

from __future__ import annotations
from unidecode import unidecode
# locals
from objects._pageobject import PageObject
from parsers._pdfbaseparser import _PDFBaseParser


class _PDFTextParser(_PDFBaseParser):
    """Private PDF document text parser intermediate class.

    Args:
        path (str): Full path to the PDF document.

    :Example:

        Extract text from a PDF file::

            >>> from docp import PDFParser

            >>> pdf = PDFParser(path='/path/to/myfile.pdf')
            >>> pdf.extract_text()

            # Access the content of page 1.
            >>> pg1 = pdf.doc.pages[1].content

    """

    def extract_text(self,
                     *,
                     remove_header: bool=False,
                     remove_footer: bool=False,
                     remove_newlines: bool=False,
                     ignore_tags: set=None,
                     convert_to_ascii: bool=True):
        """Extract text from the document.

        If the PDF document contains 'marked content' tags, these tags
        are used to extract the text as this is a more accurate approach
        and respects the structure of the page(s). Otherwise, a bounding
        box method is used to extract the text. If instructed, the
        header and/or footer regions can be excluded.

        .. tip:
            If a tag-based extract is used, the header/footer should be
            automatically excluded as these will often have an 'Artifact'
            tag, which is excluded by default, by passing
            ``ignore_tags=None``.

            To *keep* the header and footer, pass ``ignore_tags='na'``.

        A list of pages, with extracted content can be accessed using
        the :attr:`self.doc.pages` attribute.

        Args:
            remove_header (bool, optional): If True, the header is
                cropped (skipped) from text extraction. This only applies
                to the bounding box extraction method. Defaults to False.
            remove_footer (bool, optional): If True, the footer is
                cropped (skipped) from text extraction. This only applies
                to the bounding box extraction method. Defaults to False.
            remove_newlines (bool, optional): If True, the newline
                characters are replaced with a space. Defaults to False.
            ignore_tags (set, optional): If provided, these are the
                PDF 'marked content' tags which will be ignored. Note
                that the PDF document must contain tags, otherwise the
                bounding box method is used and this argument is ignored.
                Defaults to ``{'Artifact'}``, as these generally
                relate to a header and/or footer. To include all tags,
                (not skip any) pass this argument as ``'na'``.
            convert_to_ascii (bool, optional): When a non-ASCII character
                is found, an attempt is made to convert it to an
                associated ASCII character. If a character cannot be
                converted, it is replaced with a ``'?'``.
                Defaults to True.

        Returns:
            None.

        """
        # pylint: disable=unnecessary-dunder-call
        if len(self.doc.pages) > 1:
            # Reinitialise the doc object and reopen the document.
            self.__init__(path=self._path)
        # If tags are found, these are used for text extraction. If tags
        # are not found, a bounding box is used to remove the header and
        # footer, if instructed.
        if self._uses_marked_content():
            match ignore_tags:
                case None: ignore_tags = {'Artifact'}
                case 'na': ignore_tags = set()
            # Involves more processing, but also more accurate.
            self._extract_text_using_tags(ignore_tags=ignore_tags, remove_newlines=remove_newlines)
        else:
            bbox = self._get_crop_coordinates(skip_header=remove_header, skip_footer=remove_footer)
            self._extract_text_using_bbox(bbox=bbox, remove_newlines=remove_newlines)
        if convert_to_ascii:
            for page in self.doc.pages:
                page.content = unidecode(string=page.content,
                                         errors='replace',
                                         replace_str='?')

    def _extract_text_using_bbox(self, **kwargs):
        """Extract text using a bbox for finding the header and footer.

       :Keyword Arguments:
            Those passed by the caller, :meth:`~extract_text`.

        """
        for page in self.doc.parser.pages:
            text = page.within_bbox(bbox=kwargs['bbox']).extract_text().strip()
            if kwargs['remove_newlines']:
                text = text.replace('\n', ' ')
            self.doc.pages.append(PageObject(content=text, pageno=page.page_number, parser=page))

    def _extract_text_using_tags(self, **kwargs):
        """Extract text using tags.

        The tags defined by the ``ignore_tags`` are skipped.

        :Keyword Arguments:
            Those passed by the caller, :meth:`~extract_text`.

        """
        # pylint: disable=protected-access
        ignored = kwargs['ignore_tags']
        self.doc._tags = True  # Set the doc's 'parsed_using_tags' flag.
        for page in self.doc.parser.pages:
            text = ''.join(self._text_from_tags(page=page, ignored=ignored))
            if kwargs['remove_newlines']:
                text = text.replace('\n', ' ')
            self.doc.pages.append(PageObject(content=text, pageno=page.page_number, parser=page))

    @staticmethod
    def _text_from_tags(page: pdfplumber.page.Page, ignored: set) -> str:  # pylint: disable=undefined-variable  # noqa
        """Generate a page of text extracted from tags.

        When extracting text from tags, newlines are not encoded and must
        be derived. For each character on the page, the top and bottom
        coordinates are compared to determine when a newline should be
        inserted. If both the top and bottom of the current character
        are greater than the previous character, a newline is inserted
        into the text stream.

        Args:
            page (pdfplumber.page.Page): Page to be parsed.
            ignored (set): A set containing the tags to be ignored.

        Yields:
            str: Each character on the page, providing its tag is not to
            be ignored. Or, a newline character if the current
            character's coordinates are greater than (lower on the page)
            than the previous character.

        """
        if page.chars:
            # Micro-optimisation: Push tag filtering down to the C-level.
            chars = filter(lambda x: x['tag'] not in ignored, page.chars)
            top, btm = 999, 999
            for c in chars:
                if top < c['top'] and btm < c['bottom']:
                    yield '\n'
                yield c['text']
                top, btm = c['top'], c['bottom']
        yield ''

    def _uses_marked_content(self) -> bool:
        """Test wether the document can be parsed using tags.

        Marked content allows us to parse the PDF using tags (rather than
        OCR) which is more accurate not only in terms of character
        recognition, but also with regard to the structure of the text on
        a page.

        :Logic:
            If the document's catalog shows ``Marked: True``, then
            ``True`` is returned immediately.

            Otherwise, a second attempt is made which detects marked
            content tags on the first three pages. If no tags are found,
            a third attempt is made by searching the first 10 pages. If
            tags are found during either of these attempts, ``True`` is
            returned immediately.

            Finally, if no marked content or tags were found, ``False``
            is returned.

        Returns:
            bool: Returns True if the document can be parsed using marked
            content tags, otherwise False.

        """
        # Use pdfminer.six to get the document's catalog.
        if self.doc.parser.doc.catalog.get('MarkInfo', {}).get('Marked', False):
            return True
        # Check only first three pages for tags first, if found, get out.
        # If not, retry with the first 10 pages.
        for i in [3, 10]:
            tags = set(c['tag'] for p in self.doc.parser.pages[:i] for c in p.chars)
            if tags != {None}:
                return True
        return False
