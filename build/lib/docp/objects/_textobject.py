#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the implementation for the
            ``TextObject`` object.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

"""


class TextObject:
    """This class provides the implementation for the ``TextObject``.

    For each page (or slide) in a document, an instance of this class is
    created, populated and appended into the page's ``texts`` list
    attribute.

    Args:
        content (str): Page content as a single string.

    Note:
        No string cleaning is performed by this class. The string
        contained in the :attr:`contents` attribute is stored exactly as
        extracted from the page or slide's text object.

    """

    __slots__ = ('_content', '_hastext')

    def __init__(self, content: str):
        """Text object class initialiser."""
        self._content = content
        self._hastext = bool(content)

    def __str__(self) -> str:
        """When printing this object, display the text contents."""
        return self._content

    @property
    def content(self) -> str:
        """Accessor to the textual content."""
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
