#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the implementation for the
            ``PageObject`` object.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

"""

from __future__ import annotations


class PageObject:
    """This class provides the implementation for the ``PageObject``.

    For each page in a document, an instance of this class is created,
    populated and appended into the document's ``pages`` list attribute.

    Args:
        content (str, optional): Page content as a single string.
            Defaults to ''.
        pageno (int, optional): Page number. Defaults to 0.
        parser (object, optional): The underlying document parser object.
            Defaults to None.

    """

    __slots__ = ('_content', '_hastext', '_pageno', '_parser', '_tables')

    def __init__(self, content: str='', pageno: int=0, parser: object=None):
        """Page object class initialiser."""
        self._content = content
        self._pageno = pageno
        self._parser = parser
        self._hastext = bool(content)
        self._tables = []

    def __repr__(self) -> str:
        """Formatted representation of this object."""
        if self._pageno == 0:
            return f'<Page: {self._pageno}; <index offset>>'
        return f'<Page: {self._pageno}; Chars: {len(self._content)}>'

    def __str__(self) -> str:
        """Formatted string displayed when printing this object."""
        c = self._content[:25].replace('\n', ' ') + ' ...' if self._content else ''
        fmt = (f'Page no: {self._pageno}; '
               f'Content: "{c}"; '
               f'Chars: {len(self._content)}; '
               f'nTables: {len(self._tables)}; '
               f'Parser avail: {bool(self._parser)}')
        return fmt

    @property
    def content(self) -> str:
        """Accessor to the page's textual content."""
        return self._content

    @content.setter
    def content(self, value: str) -> None:
        """Setter for the ``content`` attribute.

        If the ``value`` argument is populated, the content is set and
        the ``hastext`` attribute is set to ``True``.

        """
        if value:
            self._content = value
            self._hastext = True

    @property
    def hastext(self) -> bool:
        """Flag indicating if the ``content`` attribute is populated."""
        return self._hastext

    @property
    def pageno(self) -> int:
        """Accessor to the page number.

        Note:
            This is the page number with regard to the page's *sequence
            in the overall document*. This is *not* guaranteed to be the
            page's number per the document's page labeling scheme.

        """
        return self._pageno

    @property
    def parser(self) -> object:
        """Accessor to the document parser's internal functionality.

        Note:
            The population of this property is determined by the
            document-type-specific ``docp`` parser. If the underlying
            parsing library has functionality worth preserving and making
            available to the user, it is stored to this property.
            Otherwise, this property will remain as ``None``.

        """
        return self._parser

    @property
    def tables(self) -> list:
        """Accessor to the page's tables, if parsed."""
        return self._tables

    def show(self) -> pdfplumber.display.PageImage:  # pylint: disable=undefined-variable  # noqa
        """Display the page as an image.

        Additionally, the return value exposes access to the underlying
        ``pdfplumber`` debugging visualisation methods such as:

            - :func:`img.debug_tablefinder`
            - :func:`img.draw_*`
            - :func:`img.outline_chars`
            - :func:`img.outline_words`
            - :func:`img.reset`
            - etc.


        """
        return self.parser.to_image()
