#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the implementation for the
            ``SlideObject`` object.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

"""


class SlideObject:
    r"""This class provides the implementation for the ``SlideObject``.

    For each slide in a document (e.g. PowerPoint), an instance of this
    class is created, populated and appended into the PPTX document's
    ``slides`` list attribute.

    Args:
        pageno (int, optional): Page number. Defaults to 0.
        parser (object, optional): The underlying document parser object.
            Defaults to None.

    .. tip::
        To display the textual contents of a slide, simply call the
        following, where 42 is the slide to be displayed::

            >>> print(*pptx.doc.slides[42].texts, sep='\n\n')

    """

    __slots__ = ('_imgs', '_tables', '_texts', '_pageno', '_parser')

    def __init__(self, pageno: int=0, parser: object=None):
        """Slide object class initialiser."""
        self._imgs = []
        self._tables = []
        self._texts = []
        self._pageno = pageno
        self._parser = parser

    def __repr__(self) -> str:
        """Formatted representation of this object."""
        return f'<Slide: {self._pageno}>'

    def __str__(self) -> str:
        """Formatted representation of this object, when printed."""
        if self._pageno == 0:
            return f'<Slide: {self._pageno}; <index offset>>'
        return (f'<Slide: {self._pageno}; '
                f'Text blocks: {len(self._texts)}; '
                f'Tables: {len(self._tables)}; '
                f'Images: {len(self._imgs)}; '
                f'Parser: {bool(self._parser)}>')

    @property
    def content(self) -> str:
        """Accessor to the textual content of a slide.

        Returns:
            str: A concatenated string for all text objects found on the
            slide; each object separated by a double-newline.

        """
        return '\n\n'.join(i.content for i in self._texts)

    @property
    def images(self) -> list:
        """Accessor to a slide's image objects."""
        return self._imgs

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
        """Accessor to a slide's table objects."""
        return self._tables

    @property
    def texts(self) -> list:
        """Accessor to a slide's text objects."""
        return self._texts
