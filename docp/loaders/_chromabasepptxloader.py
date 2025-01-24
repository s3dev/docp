#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides functionality to parse and store
            document data into a Chroma vector database.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

.. attention::

            This module is *not* designed to be interacted with
            directly, only via the appropriate interface class(es).

            Rather, please create an instance of a Chroma PPTX document
            loading object using the following class:

                - :class:`~docp.loaders.chromapptxloader.ChromaPPTXLoader`

"""

from langchain.docstore.document import Document
from utils4.user_interface import ui
# locals
try:
    from .loaders._chromabaseloader import _ChromaBaseLoader
    from .parsers.pptxparser import PPTXParser
except ImportError:
    from loaders._chromabaseloader import _ChromaBaseLoader
    from parsers.pptxparser import PPTXParser


class _ChromaBasePPTXLoader(_ChromaBaseLoader):
    """Base class for loading PPTX files into a Chroma vector database.

    This class is a specialised version of the
    :class:`~docp.loaders._chromabaseloader._ChromaBaseLoader` class,
    designed to handle PPTX presentations.

    Args:
        dbpath (str | ChromaDB): Either the full path to the Chroma
            database *directory*, or an instance of a
            :class:`~docp.dbs.chroma.ChromaDB` class. If the instance is
            passed, the ``collection`` argument is ignored.
        collection (str, optional): Name of the Chroma database
            collection. Only required if the ``db`` parameter is a path.
            Defaults to None.
        split_text (bool, optional): Split the document into chunks,
            before loading it into the database. Defaults to True.
        load_keywords (bool, optional): Derive keywords from the document
            and load these into the sister keywords collection.
            Defaults to False.
        llm (object, optional): If deriving keywords, this is the LLM
            which will do the derivation. Defaults to None.
        offline (bool, optional): Remain offline and use the locally
            cached embedding function model. Defaults to False.

    """
    # pylint: disable=attribute-defined-outside-init  #  These are defined in the base class.

    #
    # No __init__ method here to ensure the ultimate base class'
    # signature is used and to save passing loads of stuff around, if we
    # don't have to.
    #

    def _create_documents(self) -> bool:
        """Convert each extracted slide into a ``Document`` object.

        Returns:
            bool: True of the slides are loaded as ``Document`` objects
            successfully. Otherwise False.

        """
        self._docs = []
        for slide in self._p.doc.slides:
            for txtobj in slide.texts:
                if txtobj and txtobj.hastext:
                    doc = Document(page_content=txtobj.content,
                                   metadata={'source': self._p.doc.basename,
                                             'pageno': slide.pageno})
                    # Prevent duplicates which cause chroma to fall over on load.
                    if doc not in self._docs:
                        self._docs.append(doc)
        if not self._docs:
            msg = f'{self._PFX_WARN} Text could not be parsed from {self._p.doc.basename}.'
            ui.print_warning(msg)
            return False
        return True

    def _parse_text(self, **kwargs) -> bool:
        """Parse text from the presentation.

        :Keyword Arguments:
            Those to be passed into the text extraction method.

        Returns:
            bool: True if the parser's 'text' object is populated,
            otherwise False.

        """
        print('- Extracting text ...')
        self._p.extract_text(**kwargs)
        if len(self._p.doc.slides) < 2:
            ui.print_warning(f'No text extracted from {self._p.doc.basename}')
            return False
        return True

    def _set_parser(self):
        """Set the appropriate document parser.

        Setting the parser creates a parser instance as an attribute of
        this class. When the parser instance is created, various file
        verification checks are made. For detail, refer to the following
        parser method:

            - :meth:`docp.parsers._pptxbaseparser._PPTXBaseParser._open`

        """
        self._p = PPTXParser(path=self._fpath)
