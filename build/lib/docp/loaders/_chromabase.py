#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides functionality to parse and store
            document data into a Chroma vector database.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

"""
# pylint: disable=import-error
# pylint: disable=wrong-import-position

import os
import sys
# Set sys.path for relative imports.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from chromadb.api.types import errors as chromadberrors
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils4.reporterror import reporterror
from utils4.user_interface import ui
# locals
from dbs.chroma import Chroma
from parsers.pdfparser import PDFParser

_PRE_ERR = '\n[ERROR]:'
_PRE_WARN = '\n[WARNING]:'


class _LoadChromaBase:
    """Base class for loading documents into a Chroma vector database.

    Args:
        path (str): Full path to the file to be parsed and loaded.
        db (str | Chroma): Either the full path to the Chroma database
            *directory*, or an instance of a :class:`~dbs.chroma.Chroma`
            database. If the instance is passed, the ``collection``
            argument is ignored.
        collection (str, optional): Name of the Chroma database
            collection. Only required if the ``db`` parameter is a path.
            Defaults to None.

    """

    _PARSERS = {'.pdf': PDFParser}

    def __init__(self, db: str | Chroma, collection: str=None):
        """Chroma database class initialiser."""
        self._db = db
        self._cname = collection
        self._docs = []             # List of 'Document' objects.
        self._docss = []            # List of 'Document' objects *with splits*.
        self._p = None              # Document parser object.
        self._path = None           # Full path to the document being loaded.
        self._splitter = None       # Text splitter.
        self._set_db_client()

    @property
    def chroma(self):
        """Accessor to the database client object."""
        return self._db

    @property
    def parser(self):
        """Accessor to the document parser object."""
        return self._p

    def _create_documents(self) -> bool:
        """Convert each extracted page into a ``Document`` object.

        Returns:
            bool: True of the pages are loaded as ``Document`` objects
            successfully. Otherwise False.

        """
        self._docs = [Document(page_content=page.content,
                               metadata={'source': self._p.doc.basename,
                                         'pageno': page.pageno})
                      for page in self._p.doc.pages if page.hastext]
        if not self._docs:
            msg = f'{_PRE_WARN} Text could not be parsed from {self._p.doc.basename}.'
            ui.print_warning(msg)
            return False
        return True

    def _load(self, path: str, **kwargs):
        """Load the selected files into the vector store.

        Args:
            path (str): Full path to the file to be loaded.

        :Keyword Arguments:
            Those passed from the loader-specific ``load`` method.

        """
        # pylint: disable=multiple-statements
        self._path = path
        s = self._set_parser()
        if s: s = self._set_text_splitter()
        if s: s = self._parse_text(**kwargs)
        if s: s = self._create_documents()
        if s: s = self._split_texts()
        if s: s = self._load_worker()
        self._print_summary(success=s)

    def _load_worker(self) -> bool:
        """Load the split documents into the database collection.

        Returns:
            bool: True if loaded successfully, otherwise False. Success
            is based on the number of records after the load being
            greater than the number of records before the load, or not
            exceptions being raised.

        """
        try:
            print('- Loading the document into the database ...')
            nrecs_b = self._db.collection.count()  # Count records before.
            self._db.add_documents(self._docss)
            nrecs_a = self._db.collection.count()  # Count records after.
            return self._test_load(nrecs_b=nrecs_b, nrecs_a=nrecs_a)
        except chromadberrors.DuplicateIDError:
            print('-- Document already loaded; duplicate detected.')
            return True  # Allow to pass
        except Exception as err:
            reporterror(err)
        return False

    def _parse_text(self, **kwargs) -> bool:
        """Parse text from the document.

        :Keyword Arguments:
            Those to be passed into the text extraction method.

        Returns:
            bool: True if the parser's 'text' object is populated,
            otherwise False.

        """
        print('- Extracting text ...')
        self._p.extract_text(**kwargs)
        if len(self._p.doc.pages) < 2:
            ui.print_warning(f'No text extracted from {self._p.doc.basename}')
            return False
        return True

    @staticmethod
    def _print_summary(success: bool):
        """Print an end of processing summary.

        Args:
            success (bool): Success flag from the processor.

        """
        if success:
            print('Processing complete. Success.')
        else:
            print('Processing aborted due to error. Failure.')

    def _set_db_client(self) -> bool:
        """Set the database client object.

        If the ``_db`` object is a string, this is inferred as the *path*
        to the database. Otherwise, it is inferred as the database object
        itself.

        Returns:
            bool: True if the database object is set without error.
            Otherwise False.

        """
        try:
            if isinstance(self._db, str):
                self._db = Chroma(path=self._db, collection=self._cname)
        except Exception as err:
            reporterror(err)
            return False
        return True

    def _set_parser(self) -> bool:
        """Set the appropriate document parser.

        :Rationale:
            The parser is set by the file extension. For example, a file
            extension ``.pdf`` will set the
            :class:`parsers.pdfparser.PDFParser` class.

        Returns:
            bool: True if a file extension appropriate parser was found.
            Otherwise, False.

        """
        # pylint: disable=invalid-name
        ext = os.path.splitext(self._path)[1]
        Parser = self._PARSERS.get(ext)
        if not Parser:
            msg = f'{_PRE_WARN} Document parser not set for {os.path.basename(self._path)}.'
            ui.print_warning(msg)
            return False
        self._p = Parser(path=self._path)
        return True

    # TODO: Add these to a config.
    def _set_text_splitter(self) -> bool:
        """Define the text splitter to be used.

        Returns:
            bool: True, always.

        """
        self._splitter = RecursiveCharacterTextSplitter(chunk_size=256,
                                                        chunk_overlap=25,
                                                        separators=['\n\n\n', '\n\n', '\n', ' '])
        return True

    def _split_texts(self) -> bool:
        """Split the document text using a recursive text splitter.

        Returns:
            bool: True if the text was split successfully, otherwise
            False.

        """
        self._docss = self._splitter.split_documents(self._docs)
        if not self._docss:
            msg = (f'{_PRE_ERR} An error occurred while splitting the documents for '
                   f'{self._p.doc.basename}.')
            ui.print_warning(msg)
            return False
        return True

    def _test_load(self, nrecs_b: int, nrecs_a: int) -> bool:
        """Test the document was loaded successfully.

        :Test:
            - Given a count of records before the load, verify the number
              of records after the load is equal to the number of records
              before, plus the number of split documents.

        Args:
            nrecs_b (int): Number of records *before* the load.
            nrecs_a (int): Number of records *after* the load.

        Returns:
            bool: True if the number of records before the load plus the
            number is splits is equal to the number of records after the
            load.

        """
        if nrecs_a == nrecs_b:
            ui.print_warning(f'{_PRE_WARN} No new documents added. Possibly already loaded?')
        return nrecs_a == nrecs_b + len(self._docss)
