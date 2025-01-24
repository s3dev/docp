#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides a localised wrapper and specialised
            functionality around the
            ``langchain_community.vectorstores.Chroma`` class, for
            interacting with a Chroma database.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  This module uses the
            ``langchain_community.vectorstores.Chroma`` wrapper class,
            rather than the base ``chromadb`` library  as it provides the
            ``add_texts`` method which supports GPU processing and
            parallelisation; which is implemented by this module's
            :meth:`~ChromaDB.add_documents` method.

"""
# pylint: disable=import-error
# pylint: disable=wrong-import-order

from __future__ import annotations
import chromadb
import os
import torch
from glob import glob
from hashlib import md5
from langchain_huggingface import HuggingFaceEmbeddings
# langchain's Chroma is used rather than the base chromadb as it provides
# the add_texts method which support GPU processing and parallelisation.
from langchain_community.vectorstores import Chroma as _Chroma


class ChromaDB(_Chroma):
    """Wrapper class around the ``chromadb`` library.

    Args:
        path (str): Path to the chroma database's *directory*.
        collection (str): Collection name.
        offline (bool, optional): Remain offline, used the cached
            embedding function model rather than obtaining one online.
            Defaults to False.
    """
    # pylint: disable=line-too-long

    _MODEL_CACHE = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), '.cache')
    # Installing torch is a huge overhead, just for this. However, torch
    # will already be installed as part of the sentence-transformers library,
    # so we'll use it here.
    _MODEL_KWARGS = {'device': 'cuda' if torch.cuda.is_available() else 'cpu'}
    # TODO: Add this to a config file.
    _MODEL_NAME = 'all-MiniLM-L6-v2'

    def __init__(self, path: str, collection: str, offline: bool=False):
        """Chroma database class initialiser."""
        self._path = os.path.realpath(path)
        self._cname = collection
        self._offline = offline
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

    @property
    def path(self) -> str:
        """Accessor to the database's path."""
        return self._path

    def add_documents(self, docs: list[langchain_core.documents.base.Document]):  # noqa  # pylint: disable=undefined-variable
        """Add multiple documents to the collection.

        This method overrides the base class' ``add_documents`` method
        to enable local ID derivation. Knowing *how* the IDs are derived
        gives us greater understanding and querying ability of the
        documents in the database. Each ID is derived locally by the
        :meth:`_preproc` method from the file's basename, page number
        and page content.

        Additionally, this method wraps the
        :func:`langchain_community.vectorstores.Chroma.add_texts`
        method which supports GPU processing and parallelisation.

        Args:
            docs (list): A list of ``langchain_core.documents.base.Document``
                document objects.

        """
        # pylint: disable=arguments-differ
        # pylint: disable=arguments-renamed
        if not isinstance(docs, list):
            docs = [docs]
        ids_, docs_, meta_ = self._preproc(docs=docs)
        self.add_texts(ids=ids_, texts=docs_, metadatas=meta_)

    def show_all(self):
        """Return the entire contents of the collection.

        This is an alias around ``.collection.get()``.

        """
        return self._dbc.get()

    def _get_embedding_function_model(self) -> str:
        """Derive the path to the embedding function model.

        :Note:
            If ``offline=True`` was passed into the class constructor,
            the model cache is used, if available - otherwise the user
            is warned.

            If online usage is allowed, the model is obtained by the
            means defined by the embedding function constructor.

        Returns:
            str: The name of the model. Or, if offline, the path to the
            model's cache to be passed into the embedding function
            constructor is returned.

        """
        if self._offline:
            if not os.path.exists(self._MODEL_CACHE):
                os.makedirs(self._MODEL_CACHE)
                msg = ('Offline mode has been chosen, yet the embedding function model cache does not exist. '
                       'Therefore, a model must be downloaded. Please enable online usage for the first run '
                       'so a model can be downloaded and stored into the cache for future (offline) use.')
                raise FileNotFoundError(msg)
            # Find the cache directory containing the named model, this enables offline use.
            model_loc = os.path.commonpath(filter(lambda x: 'config.json' in x,
                                                  glob(os.path.join(self._MODEL_CACHE,
                                                                    f'*{self._MODEL_NAME}*',
                                                                    '**'),
                                                        recursive=True)))
            return model_loc
        return self._MODEL_NAME

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
            pg_ = str(m.get('pageno', 0)).zfill(4)
            id_ = f'id_{md5(src_).hexdigest()}_{pg_}_{md5(pc_).hexdigest()}'
            ids.append(id_)
            txts.append(pc)
            metas.append(m)
        return ids, txts, metas

    def _set_client(self):
        """Set the database client object."""
        settings = chromadb.Settings(anonymized_telemetry=False)
        self._client = chromadb.PersistentClient(path=self._path,
                                                 settings=settings)

    def _set_collection(self):
        """Set the database collection object."""
        self._dbc = self._client.get_or_create_collection(self._cname,
                                                          metadata={'hnsw:space': 'cosine'})

    def _set_embedding_fn(self):
        """Set the embeddings function object."""
        model_name = self._get_embedding_function_model()
        self._embfn = HuggingFaceEmbeddings(model_name=model_name,
                                            model_kwargs=self._MODEL_KWARGS,
                                            cache_folder=self._MODEL_CACHE)
