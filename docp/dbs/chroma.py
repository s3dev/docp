#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides a localised wrapper and specialised
            functionality around the ``langchain.vectorstores.Chroma``
            class, for interacting (storing data to) a Chroma database.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     jeremy.berendt@rolls-royce.com

:Comments:  n/a

"""
# pylint: disable=no-name-in-module
# pylint: disable=wrong-import-order

import chromadb
import torch
from hashlib import md5
from langchain.embeddings import HuggingFaceEmbeddings
# langchain's Chroma is used rather than the base chromadb as it provides
# the add_texts method which support GPU processing and parallelisation.
from langchain.vectorstores import Chroma as _Chroma


class Chroma(_Chroma):
    """Wrapper class around the ``chromadb`` library.

    Args:
        path (str): Path to the chroma database's *directory*.
        collection (str): Collection name.

    """

    _MODEL_NAME = 'all-MiniLM-L6-v2'
    _MODEL_KWARGS = {'device': 'cuda' if torch.cuda.is_available() else 'cpu'}

    def __init__(self, path: str, collection: str):
        """Chroma database class initialiser."""
        self._path = path
        self._cname = collection
        self._client = None         # Database 'client' object
        self._dbc = None            # Database 'collection' object.
        self._set_client()
        self._set_embedding_fn()
        super().__init__(client=self._client,
                         collection_name=self._cname,
                         embedding_function=self._embfn,
                         persist_directory=self._path)
        self._set_collection()

    @property
    def client(self):
        """Accessor to the :class:`chromadb.PersistentClient` class."""
        return self._client

    @property
    def collection(self):
        """Accessor to the chromadb client's collection object."""
        return self._dbc

    @property
    def embedding_function(self):
        """Accessor to the embedding function used."""
        return self._embfn

    def add_documents(self, docs: list):
        """Add multiple documents to the collection.

        This method wraps ``Chroma.add_texts`` method which supports GPU
        processing and parallelisation. The ID is derived locally from
        the file's basename, page number and page content.

        Args:
            docs (list): A list of ``langchain_core.documents.base.Document``
                document objects.

        """
        if not isinstance(docs, list):
            docs = [docs]
        ids_, docs_, meta_ = self._preproc(docs=docs)
        self.add_texts(ids=ids_, texts=docs_, metadatas=meta_)

    def show_all(self):
        """Return the entire contents of the collection.

        This is an alias around ``.collection.get()``.

        """
        return self._dbc.get()

    @staticmethod
    def _preproc(docs: list):
        """Pre-process the document objects to create the IDs.

        Parse the ``Document`` object into its parts for storage.
        Additionally, create the ID as a hash of the source document's
        basename, page number and content.

        """
        ids = []
        txts = []
        metas = []
        for doc in docs:
            pc = doc.page_content
            m = doc.metadata
            pc_, src_ = map(str.encode, (pc, m['source']))
            pg_ = str(m['pageno']).zfill(4)
            id_ = f'id_{md5(src_).hexdigest()}_{pg_}_{md5(pc_).hexdigest()}'
            ids.append(id_)
            txts.append(pc)
            metas.append(m)
        return ids, txts, metas

    def _set_client(self):
        """Set the database client object."""
        self._client = chromadb.PersistentClient(path=self._path)

    def _set_collection(self):
        """Set the database collection object."""
        self._dbc = self._client.get_or_create_collection(self._cname,
                                                          metadata={'hnsw:space': 'cosine'})

    def _set_embedding_fn(self):
        """Set the embeddings function object."""
        self._embfn = HuggingFaceEmbeddings(model_name=self._MODEL_NAME,
                                            model_kwargs=self._MODEL_KWARGS)
