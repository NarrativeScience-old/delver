import six
from six.moves import zip as six_zip


class TablePrinter(object):
    """Helper object for printing tables"""
    def __init__(self):
        """Initialize the necessary attributes"""
        self._rows = []
        self._col_widths = []
        self._has_header = False

    def __str__(self):
        """Render the table"""
        col_sep = ' | '
        out_rows = []
        out_rows.append(self._sep_row())
        for i, row in enumerate(self._rows):
            out_row = []
            if self._has_header is True and i == 1:
                out_rows.append(self._sep_row())
            for j, cell in enumerate(row):
                out_row.append(cell.ljust(self._col_widths[j]))
            out_row = [six.text_type(x) for x in out_row]
            out_rows.append(
                six.text_type('| {} |').format(col_sep.join(out_row)))
        out_rows.append(self._sep_row())
        return '\n'.join(out_rows)

    def _sep_row(self):
        """Control the separations between rows"""
        return '+-{}-+'.format('-+-'.join('-' * cw for cw in self._col_widths))

    def add_row(self, row, header=False):
        """Create a new row.

        :param row: the row to add to the table
        :type row: ``str``
        :param header: whether or not the row to add is a header
        :type header: ``bool``
        """
        self._has_header = self._has_header or header
        if header is True:
            self._rows.insert(0, row)
        else:
            self._rows.append(row)

        if len(self._col_widths) < len(row):
            # case: we don't have enough col_widths; add requisite counts
            self._col_widths = (
                self._col_widths + [0] * (len(row) - len(self._col_widths)))

        self._col_widths = [
            max(*lengths) for lengths in
            six_zip(self._col_widths, [len(cell) for cell in row])]
