#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the base functionality for parsing and
            storing a document's data into a Chroma vector database.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

.. attention::

            This module is *not* designed to be interacted with
            directly, only via the appropriate interface class(es).

            Rather, please create an instance of a Chroma
            document-type-specific loader object using one of the
            following classes:

                - :class:`~docp.loaders.chromapdfloader.ChromaPDFLoader`
                - :class:`~docp.loaders.chromapptxloader.ChromaPPTXLoader`

"""
# pylint: disable=no-name-in-module  # langchain.chains.RetrievalQA

import contextlib
import os
from chromadb.api.types import errors as chromadberrors
from langchain.chains import RetrievalQA
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils4.reporterror import reporterror
from utils4.user_interface import ui
# locals
try:
    from .dbs.chroma import ChromaDB
    from .libs.utilities import utilities
except ImportError:
    from dbs.chroma import ChromaDB
    from libs.utilities import utilities


class _ChromaBaseLoader:
    """Base class for loading documents into a Chroma vector database.

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
    # pylint: disable=assignment-from-no-return  # These are stub methods.

    _PFX_ERR = '\n[ERROR]:'
    _PFX_WARN = '\n[WARNING]:'

    def __init__(self,
                 dbpath: str | ChromaDB,
                 collection: str=None,
                 *,
                 split_text: bool=True,
                 load_keywords: bool=False,
                 llm: object=None,
                 offline: bool=False):
        """Chroma database class initialiser."""
        self._dbpath = dbpath
        self._cname = collection
        self._split_text = split_text
        self._load_keywords = load_keywords
        self._llm = llm
        self._offline = offline
        self._dbo = None            # Database object.
        self._docs = []             # List of 'Document' objects.
        self._docss = []            # List of 'Document' objects *with splits*.
        self._fbase = None          # Basename of the document currently being loaded.
        self._fpath = None          # Full path to the document currently being loaded.
        self._p = None              # Document parser object.
        self._splitter = None       # Text splitter.
        self._set_db_client()
        self._check_parameters()

    @property
    def chroma(self):
        """Accessor to the database client object."""
        return self._dbo

    @property
    def parser(self):
        """Accessor to the document parser object."""
        return self._p

    def _already_loaded(self) -> bool:
        """Test if the file has already been loaded into the collection.

        :Logic:
            This test is performed by querying the collection for a
            metadata 'source' which equals the filename. As this uses
            a chromadb 'filter' (i.e. ``$eq``), testing for partial
            matches is not possible at this time.

            If the filename is different (in any way) from the source's
            filename in the database, the file will be loaded again.

        Returns:
            bool: True is the *exact* filename was found in the
            collection's metadata, otherwise False.

        """
        if self._dbo.collection.get(where={'source': {'$eq': self._fbase}})['ids']:
            print(f'-- File already loaded: {self._fbase} - skipping')
            return True
        return False

    def _check_parameters(self) -> None:
        """Verify the class parameters are viable.

        Raises:
            ValueError: If the ``load_keywords`` argument is True and the
                ``llm`` argument is None, or the inverse. Both arguments
                must either sum to 0, or 2.

        """
        if sum((self._load_keywords, self._llm is not None)) not in (0, 2):
            raise ValueError('For keyword loading, the load_keywords argument '
                             'must be True and a model instance must be provided.')

    def _create_documents(self) -> bool:
        """Stub method; overridden by the child class."""

    def _get_keywords(self) -> str:
        """Query the document (using the LLM) to extract the keywords."""
        # pylint: disable=line-too-long
        print('- Extracting keywords ...')
        qry = ('List the important keywords which can be used to summarize this '
               f'document: "{self._fbase}". Use only phrases which are found in the document.')
        # Suppress stdout.
        with contextlib.redirect_stdout(None):
            nids = len(self._dbo.get(where={'source': self._fbase})['ids'])
            # Max of 50, min n records; prefer n records or 10%.
            filter_ = {'k': min(nids, max(25, min(nids//10, 50))),
                       'filter': {'source': {'$eq': self._fbase}}}
            # TODO: Replace this with the module.cless.method once created.
            qa = RetrievalQA.from_chain_type(llm=self._llm,
                                             chain_type="stuff",
                                             retriever=self._dbo.as_retriever(search_kwargs=filter_),
                                             return_source_documents=True,
                                             verbose=True)
            resp = qa.invoke(qry)
        kwds = utilities.parse_to_keywords(resp=resp['result'])
        return kwds

    def _load(self, path: str, **kwargs):
        """Load the provided file into the vector store.

        Args:
            path (str): Full path to the file to be loaded.

        :Keyword Arguments:
            Those passed from the document-type-specific loader's
            :func:`load` method.

        """
        # pylint: disable=multiple-statements
        self._fpath = path
        self._fbase = os.path.basename(path)
        if self._already_loaded():
            return
        self._set_parser()
        s = self._set_text_splitter()
        if s: s = self._parse_text(**kwargs)
        if s: s = self._create_documents()
        if s: s = self._split_texts()
        if s: s = self._load_worker()
        if s and self._load_keywords and self._llm:
            kwds = self._get_keywords()
            s = self._store_keywords(kwds=kwds)
        self._print_summary(success=s)

    def _load_worker(self) -> bool:
        """Load the split documents into the database collection.

        Returns:
            bool: True if loaded successfully, otherwise False. Success
            is based on the number of records after the load being
            greater than the number of records before the load, or not
            exceptions being raised.

        """
        # pylint: disable=line-too-long
        try:
            print('- Loading the document into the database ...')
            nrecs_b = self._dbo.collection.count()  # Count records before.
            self._dbo.add_documents(self._docss)
            nrecs_a = self._dbo.collection.count()  # Count records after.
            return self._test_load(nrecs_b=nrecs_b, nrecs_a=nrecs_a)
        except chromadberrors.DuplicateIDError:
            print('  -- Document *chunk* already loaded, duplication detected. File may be corrupt.')
            return False  # Prevent from loading keywords.
        except Exception as err:
            reporterror(err)
        return False

    def _parse_text(self, **kwargs) -> bool:
        """Stub method, overridden by the child class."""

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
            if isinstance(self._dbpath, str):
                self._dbo = ChromaDB(path=self._dbpath,
                                     collection=self._cname,
                                     offline=self._offline)
            else:
                self._dbo = self._dbpath
        except Exception as err:
            reporterror(err)
            return False
        return True

    def _set_parser(self):
        """Stub method, overridden by the child class."""

    # TODO: Add these to a config file.
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

        Note:
            If the ``split_text`` parameter was passed as ``False`` on
            instantiation, the texts will not be split. Rather, the
            :attr:`_docs` list is simply *copied* to the :attr:`_docss`
            attribute.

        Returns:
            bool: True if the text was split (or copied) successfully,
            otherwise False.

        """
        if self._split_text:
            self._docss = self._splitter.split_documents(self._docs)
        else:
            self._docss = self._docs[:]
        if not self._docss:
            msg = (f'{self._PFX_ERR} An error occurred while splitting the documents for '
                   f'{self._fbase}.')
            ui.print_warning(msg)
            return False
        return True

    def _store_keywords(self, kwds: str) -> bool:
        """Store the extracted keywords into the keywords collection.

        Args:
            kwds (str): A string containing the keywords extracted from
                the document.

        Returns:
            bool: True if loaded successfully, otherwise False.

        """
        print('- Storing keywords ...')
        db = ChromaDB(path=self._dbo.path, collection=f'{self._cname}-kwds', offline=self._offline)
        nrecs_b = db.collection.count()  # Count records before.
        docs = [Document(page_content=kwds, metadata={'source': self._fbase})]
        db.add_documents(docs)
        nrecs_a = db.collection.count()  # Count records after.
        return 1 == nrecs_a - nrecs_b

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
            ui.print_warning(f'{self._PFX_WARN} No new documents added. Possibly already loaded?')
        return nrecs_a == nrecs_b + len(self._docss)
