# Copyright (c) 2016, Narrative Science
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#!/usr/bin/env python
"""This is a helpful utility for stepping though nested objects (dictionaries
and lists).
"""
from __future__ import absolute_import
from __future__ import print_function
import argparse
import importlib
import json
import logging
import sys
import six
from six.moves import zip
from six.moves import input


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
            zip(self._col_widths, [len(cell) for cell in row])]


def delve(obj):
    """Run the event loop which actually explores objects by printing to the
    console and handling key events.

    :param obj: the object to explore
    :type obj: ``dict``
    """
    inp = "start"
    path = []
    prev_obj = []
    try:
        while inp != "q":
            table = TablePrinter()
            print(('-' * 79))
            if len(path) > 0:
                print(('At path %s' % "->".join(path)))

            if isinstance(obj, list):
                print(('List (length %s)' % len(obj)))
                prompt = '[<int>, u, q] --> '
                table.add_row(('Idx', 'Data'), header=True)
                for i, value in enumerate(obj):
                    if isinstance(value, list):
                        data = '<list, length %s>' % len(value)
                    elif isinstance(value, dict):
                        data = '<dict, length %s>' % len(value)
                    else:
                        data = value
                    table.add_row((six.text_type(i), six.text_type(data)))
            elif isinstance(obj, dict):
                print(('Dict (length %s)' % len(obj)))
                prompt = '[<key index>, u, q] --> '
                keys = sorted(obj.keys())
                table.add_row(('Idx', 'Key', 'Data'), header=True)
                for i, key in enumerate(keys):
                    value = obj[key]
                    if isinstance(value, list):
                        data = '<list, length %s>' % len(value)
                    elif isinstance(value, dict):
                        data = '<dict, length %s>' % len(value)
                    else:
                        data = value
                    table.add_row(
                        (six.text_type(i), six.text_type(key),
                         six.text_type(data)))
            else:
                table.add_row(('Value',), header=True)
                table.add_row((six.text_type(obj),))
                prompt = '[u, q] --> '

            print((six.text_type(table)))

            inp = input(str(prompt))
            if inp == 'u':
                if len(prev_obj) == 0:
                    print("Can't go up a level; we're at the top")
                else:
                    obj = prev_obj.pop()
                    path = path[:-1]
            elif inp == 'q':
                print('Bye.')
            else:
                try:
                    inp = int(inp)
                    if inp >= len(obj):
                        print("Invalid index")
                        continue
                    if isinstance(obj, list):
                        path.append(six.text_type(inp))
                    else:
                        inp = keys[inp]
                        path.append(six.text_type(inp))
                    prev_obj.append(obj)
                    obj = obj[inp]
                except ValueError:
                    print(
                        "Invalid command; please specify one of '<key index>'"
                        ", 'u', 'q'")

    except (KeyboardInterrupt, EOFError):
        print('\nBye.')

def _get_cli_args():
    """Parses and returns arguments passed from CLI.

    :return: parsed command line arguments
    :rtype: :py:class:`argparse.Namespace`
    """
    parser = argparse.ArgumentParser(
        description='Delve into JSON payloads from the command line.')
    parser.add_argument(
        'payload', type=argparse.FileType('r'), help='payload file to load')
    parser.add_argument(
        '--transform-func', type=six.text_type,
        help=(
            'the module containing the optional json transform function, '
            'formatted like: "transform_module:transform_func". Note that the '
            'transform_func should take only a json-loaded dictionary as input '
            'and should return just the transformed dictionary.'))
    return parser.parse_args()


def main():
    """System entry point."""
    my_args = _get_cli_args()

    payload_str = my_args.payload.read()
    try:
        payload = json.loads(payload_str)
    except ValueError:
        sys.exit(
            '"{}" does not contain valid JSON.'.format(my_args.payload.name))

    if my_args.transform_func is not None:
        # We need to try and import the transform func and use that to convert
        # the payload before exploring
        transform_module_str, transform_func_str = my_args.transform_func.split(
            ":")
        transform_module = importlib.import_module(transform_module_str)
        transform_func = getattr(transform_module, transform_func_str)
        try:
            payload = transform_func(payload)
        except Exception:
            logging.debug(
                'transform function failed, attempting to delve '
                'without the transform')

    del payload_str
    my_args.payload.close()
    delve(payload)


if __name__ == '__main__':
    main()
