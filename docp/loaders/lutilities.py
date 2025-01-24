#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides loader-specific utility functions for
            the project.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  This module is here (in the ``docp/loaders``) directory
            rather than merged with the ``docp/parsers/putilities.py``
            module as the loaders' dependencies are *heavy*. Keeping the
            loader functionality separate helps to ease the dependency
            requirements for parser-only projects.

"""

# locals
try:
    from .libs.utilities import utilities
    from .loaders.chromapdfloader import ChromaPDFLoader
    from .loaders.chromapptxloader import ChromaPPTXLoader
except ImportError:
    from libs.utilities import utilities
    from loaders.chromapdfloader import ChromaPDFLoader
    from loaders.chromapptxloader import ChromaPPTXLoader


class LoaderUtilities:
    """Loader-based (cross-project) utility functions."""

    def get_loader(self, path: str) -> ChromaPDFLoader | ChromaPPTXLoader:
        """Return the appropriate loader for the file type.

        Args:
            path (str): Full path to the file to be tested.

        Returns:
            ChromaPDFLoader | ChromaPPTXLoader: The appropriate loader
            for the file, given the *file signature*; this test is not
            file extension based.

        """
        if utilities.ispdf(path=path):
            return ChromaPDFLoader
        if utilities.iszip(path=path):
            return ChromaPPTXLoader
        raise NotImplementedError('A loader is not available for: os.path.basename(path)')


lutilities = LoaderUtilities()
