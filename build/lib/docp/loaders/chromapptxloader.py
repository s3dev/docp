#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the entry point for loading PPTX files
            into a Chroma database.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

:Examples:

    Parse and load a *single* PPTX file into a Chroma database
    collection::

        >>> from docp.loaders import ChromaPPTXLoader

        >>> l = ChromaPPTXLoader(dbpath='/path/to/chroma',
                                 collection='spam',
                                 split_text=False)
        >>> l.load(path='/path/to/directory/myfile.pptx')


    Parse and load a *directory* of PPTX files into a Chroma database
    collection::

        >>> from docp.loaders import ChromaPPTXLoader

        >>> l = ChromaPPTXLoader(dbpath='/path/to/chroma',
                                 collection='spam',
                                 split_text=False)
        >>> l.load(path='/path/to/directory', ext='pptx')


    For further example code use, please refer to the
    :class:`ChromaPPTXLoader` class docstring.

"""

import os
# locals
try:
    from .libs.utilities import utilities
    from .loaders._chromabasepptxloader import _ChromaBasePPTXLoader
except ImportError:
    from libs.utilities import utilities
    from loaders._chromabasepptxloader import _ChromaBasePPTXLoader


class ChromaPPTXLoader(_ChromaBasePPTXLoader):
    """Chroma database PPTX-specific document loader.

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

    .. important::

        The *deriving and loading of keywords* is only recommended for
        **GPU-bound processing**, as the LLM is invoked to infer the
        keywords for each given document.

        If called on a 'standard' PC, this will take a *long* time to
        complete, if it completes at all.

    .. tip::

        It is recommended to pass ``split_text=False`` into the
        :class:`ChromaPPTXLoader` constructor.

        Often, PowerPoint presentations are structured such that related
        text is found in the same 'shape' (textbox) on a slide.
        Splitting the text in these shapes may have undesired results.

    :Examples:

        Parse and load a *single* PPTX file into a Chroma database
        collection::

            >>> from docp.loaders import ChromaPPTXLoader

            >>> l = ChromaPPTXLoader(dbpath='/path/to/chroma',
                                     collection='spam',
                                     split_text=False)  # <-- Note this
            >>> l.load(path='/path/to/directory/myfile.pptx')


        Parse and load a *directory* of PPTX files into a Chroma database
        collection::

            >>> from docp.loaders import ChromaPPTXLoader

            >>> l = ChromaPPTXLoader(dbpath='/path/to/chroma',
                                     collection='spam',
                                     split_text=False)  # <-- Note this
            >>> l.load(path='/path/to/directory', ext='pptx')

    """
    def load(self,
             path: str,
             *,
             ext: str='**',
             recursive: bool=True,
             remove_newlines: bool=True,
             convert_to_ascii: bool=True,
             **unused) -> None:
        """Load a PDF file (or files) into a Chroma database.

        Args:
            path (str): Full path to the file (or *directory*) to be
                parsed and loaded. Note: If this is a directory, a
                specific file extension can be passed into the
                :meth:`load` method using the ``ext`` argument.
            ext (str, optional): If the ``path`` argument refers to a
                *directory*, a specific file extension can be specified
                here. For example: ``ext = 'pptx'``.

                If anything other than ``'**'`` is provided, all
                alpha-characters are parsed from the string, and prefixed
                with ``*.``. Meaning, if ``'.pptx'`` is passed, the
                characters ``'pptx'`` are parsed and prefixed with ``*.``
                to create ``'*.pptx'``. However, if ``'things.foo'`` is
                passed, the derived extension will be ``'*.thingsfoo'``.
                Defaults to '**', for a recursive search.

            recursive (bool, optional): If True, subdirectories are
                searched. Defaults to True.
            remove_newlines (bool, optional): Replace newline characters
                with a space. Defaults to True, as this helps with
                document chunk splitting.
            convert_to_ascii (bool, optional): Convert all characters to
                ASCII. Defaults to True.

        :Keyword Args:
            unused (dict): This enables keywords such as ``remove_header``
                and ``remove_footer`` (for example) to be passed into a
                loader-agnostic ``.load()`` function without raising a
                'unexpected keyword argument` ``TypeError``.

        """
        # pylint: disable=unused-argument  # They are 'used' via locals().
        # Prepare the arguments being sent to the doc parser.
        kwargs = self._set_kwargs(locals_=locals())
        # Load multi
        if os.path.isdir(path):
            files = utilities.collect_files(path=path, ext=ext, recursive=recursive)
            count = len(files)
            for idx, f in enumerate(files, 1):
                print(f'\nProcessing {idx} of {count}: {os.path.basename(f)}')
                self._load(path=f, **kwargs)
        # Load single
        else:
            print(f'Processing: {os.path.basename(path)} ...')
            self._load(path=path, **kwargs)

    @staticmethod
    def _set_kwargs(locals_: dict) -> dict:
        r"""Prepare the arguments which are sent to the doc parser.

        As :func:`locals()` is used to capture the :meth:`load` method's
        arguments for passing into the doc parser, some argument must be
        removed first.

        Args:
            locals\_ (dict): The return value from a :func:`locals` call.

        Returns:
            dict: A *copy* of the provided dictionary with specific
            key/value pairs removed.

        """
        # ^^^ The backslash in locals\_ is required for documentation to render correctly.
        kwargs = locals_.copy()
        for k in ['self', 'path']:
            kwargs.pop(k)
        return kwargs
