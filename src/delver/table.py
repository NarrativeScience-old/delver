"""Module containing TablePrinter class for creating and formatting tables"""
from textwrap import fill

import colorful
from terminaltables import AsciiTable

colorful.use_style("solarized")


MAX_COLUMN_WIDTH = 80

DEFAULT_COLUMN_COLORS = [colorful.yellow, colorful.blue, colorful.green]


class TablePrinter(object):
    """Wrapper class around the terminaltables' :py:class:`AsciiTable`"""

    def __init__(self, use_colors=True):
        """Initialize an empty table"""
        self.table = AsciiTable([])
        self.use_colors = use_colors

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
        for row in table_info["rows"]:
            new_row = []
            for column_index, cell in enumerate(row):
                new_cell = fill(cell, MAX_COLUMN_WIDTH)
                if self.use_colors:
                    new_cell = _style_cell(new_cell, column_index)
                new_row.append(new_cell)
            final_rows.append(new_row)
        headers = table_info["columns"]
        if self.use_colors:
            headers = _style_headers(headers)
        self.table = AsciiTable([headers] + final_rows)


def _style_headers(headers):
    """Apply styles to the headers of a table.

    :param headers: list of header strings for styling
    :type headers: ``list`` of ``str``

    :returns: list of header strings that have been styled
    :rtype: ``list`` of ``str``
    """
    return [
        colorful.bold & DEFAULT_COLUMN_COLORS[i] | header
        for i, header in enumerate(headers)
    ]


def _style_cell(cell, column_index):
    """Apply styles to a cell of a table, taking care to account for newlines.

    :param cell: the cell string contents to style
    :type cell: ``str``
    :param column_index: the index of the column the cell belongs to
    :type column_index: ``int``

    :returns: a styled cell string
    :rtype: ``str``
    """
    segments = cell.split("\n")
    if len(segments) == 1:
        return DEFAULT_COLUMN_COLORS[column_index] | cell

    # Need to apply the coloring to each segment separately to prevent
    # terminaltables from incorrectly coloring the table border characters
    segments = [DEFAULT_COLUMN_COLORS[column_index] | segment for segment in segments]

    # Concat the segments back together (colorful objects don't support `join`)
    new_cell = ""
    for segment in segments:
        new_cell += segment
    return new_cell
