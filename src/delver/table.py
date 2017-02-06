"""Module containing TablePrinter class for creating and formatting tables"""
from textwrap import wrap

from terminaltables import AsciiTable


MAX_COLUMN_WIDTH = 80


class TablePrinter(object):
    def __init__(self):
        self.table = AsciiTable([])

    def __str__(self):
        return self.table.table

    def build_from_info(self, table_info):
        final_rows = []
        for row in table_info['rows']:
            new_row = []
            for cell in row:
                new_cell = cell
                if len(cell) > MAX_COLUMN_WIDTH:
                    new_cell = '\n'.join(wrap(new_cell, MAX_COLUMN_WIDTH))
                new_row.append(new_cell)
            final_rows.append(new_row)
        self.table = AsciiTable([table_info['columns']] + final_rows)
