"""Module containing TablePrinter class for creating and formatting tables"""
from textwrap import fill

from terminaltables import AsciiTable


MAX_COLUMN_WIDTH = 80


class TablePrinter(object):
    """Wrapper class around the terminaltables' :py:class:`AsciiTable`"""
    def __init__(self):
        """Initialize an empty table"""
        self.table = AsciiTable([])

    def __str__(self):
        """Overwrite in order to enable direct printing of the object"""
        return self.table.table

    def build_from_info(self, table_info):
        """Given a dictionary of information about a table describing an object,
        overwrite :py:attr:`.table` with the new content. An example
        `table_info` would look like this:

        .. code-block:: json

            {
                "rows": [
                    ["0", "foo"],
                    ["1", "bar"]
                ],
                "columns": ["Index", "Data"]
            }

        :param table_info: a dictionary of information including the column
            names and rows
        :type table_info: ``dict``
        """
        final_rows = []
        for row in table_info['rows']:
            new_row = []
            for cell in row:
                new_row.append(fill(cell, MAX_COLUMN_WIDTH))
            final_rows.append(new_row)
        self.table = AsciiTable([table_info['columns']] + final_rows)
