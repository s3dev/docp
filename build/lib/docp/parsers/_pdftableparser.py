#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the logic for parsing tables from a PDF
            document.

:Platform:  Linux
:Developer: J Berendt
:Email:     jeremy.berendt@rolls-royce.com

.. attention::

            This module is *not* designed to be interacted with
            directly, only via the appropriate interface class(es).

            Rather, please create an instance of a PDF document parsing
            object using the following:

                - :class:`~docp.parsers.pdfparser.PDFParser`

"""
# pylint: disable=import-error
# pylint: disable=protected-access
# pylint: disable=wrong-import-order

import io
import os
import pandas as pd
import shutil
# locals
from parsers._pdfbaseparser import _PDFBaseParser

# TODO: Move to a config file/class.  (TOML?)
_SETTINGS = {'vertical_strategy': 'lines',
             'horizontal_strategy':'lines',
             'snap_x_tolerance': 12}


class _PDFTableParser(_PDFBaseParser):
    """Private PDF document table parser intermediate class.

    Args:
        path (str): Full path to the PDF document.

    :Example:

        Extract tables from a PDF file::

            >>> from docp import PDFParser

            >>> pdf = PDFParser(path='/path/to/myfile.pdf')
            >>> pdf.extract_tables()

            >>> tables = pdf.doc.tables

    """

    def extract_tables(self,
                       table_settings: dict=None,
                       as_dataframe: bool=False,
                       to_csv: bool=True,
                       verbose: bool=False):
        """Extract tables from the document.

        Before a table is extracted, a number of validation tests are
        performed to verify what has been identified as a 'table' is
        actually a table which might be useful to the user.

        Each 'valid' table is written as a CSV file on the user's
        desktop.

        Additionally, the extracted table data is stored to the class'
        :attr:`self.tables` attribute.

        Args:
            table_settings (dict, optional): Table settings to be used
                for the table extraction. Defaults to None, which is
                replaced by the value in the config.
            as_dataframe (bool, optional): By default, the extracted
                tables are returned as a list of (lists of lists), for
                example: all_tables[table[rows[data]]]. However, if this
                argument is ``True``, the table data is returned as a
                list of ``pandas.DataFrame`` objects. In this case, the
                first row of the table is used as the header, and all
                remaining rows are treated as data. **Note:** This will
                *not* work properly for all tables. Defaults to False.
            to_csv (bool, optional): Dump extracted table data to a CSV
                file, one per table. Defaults to True.
            verbose (bool, optional): Display how many tables were
                extracted, and the path to their location.

        """
        # pylint: disable=invalid-name
        # pylint: disable=too-many-nested-blocks
        # pylint: disable=unnecessary-dunder-call
        if self._doc.tables:
            # Reinitialise the doc object and reopen the document.
            self.__init__(path=self._path)
        c = 0
        if to_csv:
            self._create_table_directory_path()
        if table_settings is None:
            table_settings = _SETTINGS
        for p in self._doc._pdf.pages:
            tblno = 1
            tables = self._filter_tables(tables=p.find_tables(), threshold=5000)
            for table in tables:
                pc = p.crop(table.bbox)
                data = pc.extract_table(table_settings=table_settings)
                if all(len(row) > 1 for row in data) and len(data) > 1:
                    # Verify no table rows are found in the most common rows (header/footer).
                    if not self._table_header_footer(table=data):
                        if not as_dataframe:
                            self._doc._tables.append(data)
                        if to_csv or as_dataframe:
                            buffer = self._to_buffer(data=data)
                            if to_csv:
                                c += self._to_csv(buffer=buffer,
                                                  pageno=p.page_number,
                                                  tableno=tblno)
                            if as_dataframe:
                                self._to_df(buffer=buffer)
                            buffer.close()
                        tblno += 1
        if verbose and to_csv:
            print('',
                  'Complete.',
                  f'{c} tables were extracted and stored at the path below.',
                  f'Path: {self._tbl_opath}',
                  sep='\n')

    def _create_table_directory_path(self):
        """Create the output directory for table data.

        If the directory does not exist, it is created.

        """
        # Defined in parent class.
        # pylint: disable=attribute-defined-outside-init
        trans = {32: '_', 45: '_'}
        path = (os.path.join(os.path.join(os.environ['HOME'], 'Desktop'),
                             'docutils',
                             'pdf_tables',
                             (os.path.splitext(os.path.basename(self._path))[0]
                              .lower()
                              .translate(trans))))
        self._tbl_opath = path
        if not os.path.exists(path):
            os.makedirs(path)

    def _create_table_file_path(self, pageno: int, tblno: int) -> str:
        """Create the filename for the table.

        Args:
            pageno (int): Page from which the table was extracted.
            tblno (int): Number of the table on the page, starting at 1.

        Returns:
            str: Explicit path to the file to be written.

        """
        path = os.path.join(self._tbl_opath,
                            f'pg{str(pageno).zfill(3)}_tb{str(tblno).zfill(3)}.csv')
        return path

    @staticmethod
    def _filter_tables(tables: list, threshold: int=5000) -> list:
        """Remove tables from the passed list which are deemed invalid.

        Args:
            tables (list): A list of tables as detected by the
                :meth:`Page.find_table()` method.
            threshold (int, optional): Minimum pixel area for a detected
                table to be returned. Defaults to 5000.

        :Rationale:
            An 'invalid' table is determined by the number of pixels
            which the table covered. Any table which is less than (N)
            pixels is likely a block of text which has been categorised
            as a 'table', but is not.

        Returns:
            list: A list of tables whose pixel area is greater than
            ``threshold``.

        """
        # pylint: disable=invalid-name
        t = []
        for table in tables:
            x0, y0, x1, y1 = table.bbox
            if (x1-x0) * (y1-y0) > threshold:
                t.append(table)
        return t

    def _table_header_footer(self, table: list[list]) -> bool:
        """Verify a table is not a header or footer.

        Args:
            table (list[list]): Table (a list of lists) be a analysed.

        :Rationale:
            A table is determined to be a header or footer if any of the
            line contained in the 'common lines list' are found in the
            table.

            If any of these lines are found, the table is determined to
            be a header/footer, True is returned.

        Returns:
            bool: False if the table is *not* a header/footer, otherwise
            True.

        """
        lines = self._scan_common()  # Only re-runs if not already run.
        # r: row; c: cell; l: line
        return any(l in c for l in lines for r in table for c in r if c)

    def _to_buffer(self, data: list[list]) -> io.StringIO:
        """Write the table data into a string buffer.

        Args:
            data (list[list]): The table data as a list of lists to be
                written to a buffer.

        Returns:
            io.StringIO: A string buffer as an ``io.StringIO`` object.

        """
        b = io.StringIO()
        for row in data:
            line = self._prepare_row(row=row)
            b.write(line)
            b.write('\n')
        b.seek(0)
        return b

    def _to_csv(self, buffer: io.StringIO, pageno: int, tableno: int) -> int:
        """Write a table (from the buffer) to CSV.

        Args:
            buffer (io.StringIO): A pre-processed ``StringIO`` object
                containing table data to be written.
            pageno (int): Page number from the ``Page`` object.
            tableno (int): Number of the table on the page, based at 1.

        Returns:
            int: 1 if the file was written, otherwise 0. This is used by
            the caller to track the number of CSV files written.

        """
        if buffer.seek(0, os.SEEK_END):  # Test buffer is populated.
            path = self._create_table_file_path(pageno=pageno, tblno=tableno)
            with open(path, 'w', encoding='utf-8') as f:
                buffer.seek(0)
                shutil.copyfileobj(buffer, f)
                return 1
        return 0

    def _to_df(self, buffer: io.StringIO):
        """Write a table (from the buffer) to a DataFrame.

        Once written, the DataFrame is appended to
        :attr:`self._doc._tables` list of tables.

        Args:
            buffer (io.StringIO): A pre-processed ``StringIO`` object
                containing table data to be written.

        """
        if buffer.seek(0, os.SEEK_END):
            buffer.seek(0)
            self._doc._tables.append(pd.read_csv(buffer))
