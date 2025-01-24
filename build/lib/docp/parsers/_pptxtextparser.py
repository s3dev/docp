#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the logic for parsing text from a PPTX
            document.

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

from unidecode import unidecode
# locals
try:
    from .objects._slideobject import SlideObject
    from .objects._textobject import TextObject
    from .parsers._pptxbaseparser import _PPTXBaseParser
except ImportError:
    from objects._slideobject import SlideObject
    from objects._textobject import TextObject
    from parsers._pptxbaseparser import _PPTXBaseParser


class _PPTXTextParser(_PPTXBaseParser):
    """Private PPTX document text parser intermediate class.

    Args:
        path (str): Full path to the PPTX document.

    :Example:

        Extract text from a PPTX file::

            >>> from docp import PPTXParser

            >>> pptx = PPTXParser(path='/path/to/myfile.pptx')
            >>> pptx.extract_text()

            # Access the text on slide 1.
            >>> pg1 = pptx.doc.slides[1].content

    """

    def extract_text(self,
                     *,
                     remove_newlines: bool=False,
                     convert_to_ascii: bool=True,
                     **kwargs) -> None:
        """Extract text from the document.

        A list of slides, with extracted content can be accessed using
        the :attr:`self.doc.slides` attribute.

        Args:
            remove_newlines (bool, optional): If True, the newline
                characters are replaced with a space. Defaults to False.
            convert_to_ascii (bool, optional): When a non-ASCII character
                is found, an attempt is made to convert it to an
                associated ASCII character. If a character cannot be
                converted, it is replaced with a ``'?'``.
                Defaults to True.

        :Keyword Args:
            - None

        Returns:
            None.

        """
        # pylint: disable=unused-argument  # **kwargs
        # pylint: disable=unnecessary-dunder-call
        if len(self.doc.slides) > 1:
            # Reinitialise the doc object and reopen the document.
            self.__init__(path=self._path)
        self._extract_text(remove_newlines=remove_newlines, convert_to_ascii=convert_to_ascii)

    def _extract_text(self, remove_newlines: bool, convert_to_ascii: bool) -> None:
        """Extract the text from all shapes on all slides.

        Args:
            remove_newlines (bool): Replace the newline characters with
                a space.
            convert_to_ascii (bool): Attempt to convert any non-ASCII
                characters to their ASCII equivalent.

        The text extracted from each slide is stored as a ``TextObject``
        which is appended to the slide's ``texts`` attribute.

        """
        for idx, slide in enumerate(self.doc.parser.slides, 1):
            _slideobj = SlideObject(pageno=idx, parser=slide)
            for shape in slide.shapes:
                if hasattr(shape, 'text'):
                    if shape.text:
                        text = shape.text
                        if remove_newlines:
                            text = text.replace('\n', ' ')
                        if convert_to_ascii:
                            text = unidecode(string=text,
                                             errors='replace',
                                             replace_str='?')
                        _textobj = TextObject(content=text)
                        _slideobj.texts.append(_textobj)
            self.doc.slides.append(_slideobj)
