
# A basic document parsing and loading utility.

[![PyPI - Version](https://img.shields.io/pypi/v/docp?style=flat-square)](https://pypi.org/project/docp)
[![PyPI - Implementation](https://img.shields.io/pypi/implementation/docp?style=flat-square)](https://pypi.org/project/docp)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/docp?style=flat-square)](https://pypi.org/project/docp)
[![PyPI - Status](https://img.shields.io/pypi/status/docp?style=flat-square)](https://pypi.org/project/docp)
[![Static Badge](https://img.shields.io/badge/tests-pending-orange?style=flat-square)](https://pypi.org/project/docp)
[![Static Badge](https://img.shields.io/badge/code_coverage-pending-orange?style=flat-square)](https://pypi.org/project/docp)
[![Static Badge](https://img.shields.io/badge/pylint_analysis-100%25-brightgreen?style=flat-square)](https://pypi.org/project/docp)
[![Documentation Status](https://readthedocs.org/projects/docp/badge/?version=latest&style=flat-square)](https://docp.readthedocs.io/en/latest/)
[![PyPI - License](https://img.shields.io/pypi/l/docp?style=flat-square)](https://opensource.org/license/gpl-3-0)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/docp?style=flat-square)](https://pypi.org/project/docp)

In its simplest form, the ``docp`` project is a (doc)ument \(p\)arsing library.

Written in CPython, the project wraps various lower-level libraries, helping to consolidate binary document structure parsing functionality into a single library. Additional functionality includes [document loaders](#loaders) which load a parsed document's embeddings into a Chroma vector database, for RAG-enabled LLM use.


## Installation
The easiest way to install ``docp`` is using ``pip`` *after* activating your virtual environment::
    
    pip install docp

Additional (older) releases can be found either at [PyPI](https://pypi.org/project/docp/#history) or in [GitHub Releases](https://github.com/s3dev/docp/releases).

### A note on the installation of dependencies:
To keep the installation dependencies to a minimum, only core libraries are required for installation. Meaning, the parser-specific and loader libraries are *not* installed automatically, as part of the ``pip install`` command.

If a parser is imported and a library is required but not installed, you'll be notified with an easy-to-read message, listing the required dependenc(y|ies).

The rationale behind this design decision is that not all users will need the document *loading* capability, so ``torch``, ``langchain``,  etc. should not be installed automatically. For example, if your project requires a simple PDF parser, you don't need to (and likely don't want to) 'clutter' your environment with something as heavy as ``torch``, nor make your project dependent on it.


## The Toolset

### Parsers
As of this release, parsers for the following binary document types are supported:

- PDF
- MS PowerPoint (PPTX)
- (more coming soon)

### Loaders
In addition to document parsing, document *loading* functionality is built-in as well. Specifically, loading documents into a [Chroma](https://www.trychroma.com) vector database for RAG-enabled LLM ingestion.

For example, you may wish to load a series of PDF files into a vector database which serves as the backend for a RAG-enabled LLM chatbot. The ``ChromaLoader`` class is specifically designed for this. A single call to the class' loader method results in file retrieval, parsing, splitting, embedding and storage.

For further detail and usage examples, please refer to the project's [documentation](https://docp.readthedocs.io/).


## Using the Library
The documentation suite contains detailed explanation and example usage for each of the library's importable modules. For detailed documentation, usage examples and links the source code itself, please refer to the 
[Library API](https://docp.readthedocs.io/en/latest/library.html) page in the documentation.

### Quickstart
For convenience, here are a couple examples for how to parse the supported document types.

**Extract text from a PDF file:**

    >>> from docp import PDFParser

    >>> pdf = PDFParser(path='/path/to/myfile.pdf')
    >>> pdf.extract_text()

    # Access the content of page 1.
    >>> pg1 = pdf.doc.pages[1].content

**Extract text from a PowerPoint presentation:**

    >>> from docp import PPTXParser

    >>> pptx = PPTXParser(path='/path/to/myfile.pptx')
    >>> pptx.extract_text()

    # Access the text on slide 1.
    >>> pg1 = pptx.doc.slides[1].content

