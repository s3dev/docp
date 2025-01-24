===============================
docp Library Documentation
===============================

.. contents:: Page Contents
    :local:
    :depth: 1


Overview
========
In its simplest form, the ``docp`` project is a (doc)ument (p)arsing library.

Written in CPython, the project wraps various lower-level libraries, 
helping to consolidate binary document structure parsing functionality
into a single library. Additional functionality includes 
:ref:`document loaders <loaders>` which load a parsed document's embeddings
into a Chroma vector database, for RAG-enabled LLM use.


The Toolset
===========

Parsers
-------
As of this release, parsers for the following binary document types are
supported:

- PDF
- MS PowerPoint (PPTX)
- more coming soon ...


.. _loaders:

Loaders
-------
In addition to document parsing, document *loading* functionality is
built-in as well. Specifically, loading documents into a `Chroma`_ vector
database for RAG-enabled LLM ingestion.

For example, you may wish to load a series of PDF files into a vector
database which serves as the backend for a RAG-enabled LLM chatbot. The
``ChromaPDFLoader`` and ``ChromaPPTXLoader`` classes have been specifically
designed for this. A single call to the class' loader method results in 
file retrieval, parsing, splitting, embedding and storage.

For further detail and usage examples, please refer to the documentation
for the following modules:

- :ref:`loaders/chromapdfloader <module-loaders-chromapdfloader>` 
- :ref:`loaders/chromapptxloader <module-loaders-chromapptxloader>` 


Installation
============
The easiest way to install ``docp`` is using ``pip`` *after* activating
your virtual environment::
    
    pip install docp

Additional (older) releases can be found either at `PyPI`_ or in 
`GitHub Releases`_.

.. note::

    To keep the installation dependencies to a minimum, only core libraries
    are required for installation. Meaning, the parser-specific and loader
    libraries are *not* installed automatically.

    If a parser is imported and a library is required but not installed,
    you'll be notified with an easy-to-read message, listing the required
    dependenc(y|ies).

    The rationale behind this design decision is that not all users will 
    need the document *loading* capability, so ``torch``, ``langchain``, 
    etc. should not be installed automatically. For example, if your project
    requires a simple PDF parser, you don't need to (and likely don't want to)
    'clutter' your environment with something as heavy as ``torch``.


.. _using-the-library:

Using the Library
=================
This documentation suite contains detailed explanation and example usage 
for each of the library's importable modules. For detailed documentation, 
usage examples and links the source code itself, please refer to the 
:ref:`library-api` page.

If there is a specific module or method which you cannot find, a 
**search** field is built into the navigation bar to the left.


Quickstart
----------
For convenience, here are a couple examples for how to parse the supported
document types.

Extract text from a PDF file:

.. code-block:: python


    >>> from docp import PDFParser

    >>> pdf = PDFParser(path='/path/to/myfile.pdf')
    >>> pdf.extract_text()

    # Access the content of page 1.
    >>> pg1 = pdf.doc.pages[1].content

Extracting text from a PowerPoint presentation is very similar:

.. code-block:: python

    >>> from docp import PPTXParser

    >>> pptx = PPTXParser(path='/path/to/myfile.pptx')
    >>> pptx.extract_text()

    # Access the text on slide 1.
    >>> pg1 = pptx.doc.slides[1].content


.. _troubleshooting:

Troubleshooting
===============
No guidance at this time.

If you have any questions that are not covered by this documentation, or
if you spot any bugs, issues or have any recommendations, please feel free
to :ref:`contact us <contact-us>` or raise an issue on `GitHub`_.


Documentation Contents
======================
.. toctree::
    :maxdepth: 1

    library
    changelog
    contact


Indices and Tables
==================
* :ref:`genindex`
* :ref:`modindex`


.. rubric:: Footnotes

.. _Chroma: https://www.trychroma.com
.. _GitHub Releases: https://github.com/s3dev/docp/releases
.. _GitHub: https://github.com/s3dev/docp
.. _PyPI: https://pypi.org/project/docp/#history

|lastupdated|

