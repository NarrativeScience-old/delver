"""Module containing tests for the delver tool"""
import unittest

import mock

from .context import delve as mod_ut


class TestDelveFunctional(unittest.TestCase):
    """Functional tests for the delver tool"""
    def setUp(self):
        """Initialize frequently used test objects"""
        self.test_obj = {'foo': ['bar', {'baz': 3}]}
        print_patch = mock.patch('src.delver.delve._print')
        input_patch = mock.patch('src.delver.delve.six_input')
        self.fake_print = print_patch.start()
        self.fake_input = input_patch.start()
        self.addCleanup(print_patch.stop)
        self.addCleanup(input_patch.stop)

    def _extract_print_strings(self, call_args):
        """Extract the actual strings that make up the calls to the patched
        print function.

        :param call_args: the list of arguments passed to the patched function
        :type call_args: ``list``

        :return: list of strings that were arguments to the patched print
            function
        :rtype: ``list`` of ``str``
        """
        return [x[0][0] for x in call_args]

    def test_single_navigate(self):
        """Test a single navigation and exit"""
        self.fake_input.side_effect = [
            '0',
            'q'
        ]
        target_print_args = [
            mod_ut.DEFAULT_DIVIDER,
            'Dict (length 1)',
            ('+-----+-----+------------------+\n'
             '| Idx | Key | Data             |\n'
             '+-----+-----+------------------+\n'
             '| 0   | foo | <list, length 2> |\n'
             '+-----+-----+------------------+'),
            mod_ut.DEFAULT_DIVIDER,
            'At path foo',
            'List (length 2)',
            ('+-----+------------------+\n'
             '| Idx | Data             |\n'
             '+-----+------------------+\n'
             '| 0   | bar              |\n'
             '| 1   | <dict, length 1> |\n'
             '+-----+------------------+'),
            'Bye.'
        ]
        mod_ut.delve(self.test_obj)
        result_print_args = self._extract_print_strings(
            self.fake_print.call_args_list)
        self.assertListEqual(result_print_args, target_print_args)

    def test_invalid_key_index(self):
        """Test an invalid index message is displayed"""
        self.fake_input.side_effect = [
            '1',
            'q'
        ]
        target_print_args = [
            mod_ut.DEFAULT_DIVIDER,
            'Dict (length 1)',
            ('+-----+-----+------------------+\n'
             '| Idx | Key | Data             |\n'
             '+-----+-----+------------------+\n'
             '| 0   | foo | <list, length 2> |\n'
             '+-----+-----+------------------+'),
            'Invalid index',
            mod_ut.DEFAULT_DIVIDER,
            'Dict (length 1)',
            ('+-----+-----+------------------+\n'
             '| Idx | Key | Data             |\n'
             '+-----+-----+------------------+\n'
             '| 0   | foo | <list, length 2> |\n'
             '+-----+-----+------------------+'),
            'Bye.'
        ]

        mod_ut.delve(self.test_obj)
        result_print_args = self._extract_print_strings(
            self.fake_print.call_args_list)
        self.assertEqual(result_print_args, target_print_args)

    def test_invalid_command(self):
        """Test an invalid command message is displayed"""
        self.fake_input.side_effect = [
            'blah',
            'q'
        ]
        mod_ut.delve(self.test_obj)
        target_print_args = [
            mod_ut.DEFAULT_DIVIDER,
            'Dict (length 1)',
            ('+-----+-----+------------------+\n'
             '| Idx | Key | Data             |\n'
             '+-----+-----+------------------+\n'
             '| 0   | foo | <list, length 2> |\n'
             '+-----+-----+------------------+'),
            "Invalid command; please specify one of '<key index>', 'u', 'q'",
            mod_ut.DEFAULT_DIVIDER,
            'Dict (length 1)',
            ('+-----+-----+------------------+\n'
             '| Idx | Key | Data             |\n'
             '+-----+-----+------------------+\n'
             '| 0   | foo | <list, length 2> |\n'
             '+-----+-----+------------------+'),
            'Bye.'
        ]
        result_print_args = self._extract_print_strings(
            self.fake_print.call_args_list)
        self.assertEqual(result_print_args, target_print_args)

    def test_advanced_navigation(self):
        """Test navigating deeper into a data structure and back out"""
        self.fake_input.side_effect = [
            '0',
            '1',
            '0',
            'u',
            '0',
            'q'
        ]
        mod_ut.delve(self.test_obj)
        target_print_args = [
            mod_ut.DEFAULT_DIVIDER,
            'Dict (length 1)',
            ('+-----+-----+------------------+\n'
             '| Idx | Key | Data             |\n'
             '+-----+-----+------------------+\n'
             '| 0   | foo | <list, length 2> |\n'
             '+-----+-----+------------------+'),
            mod_ut.DEFAULT_DIVIDER,
            'At path foo',
            'List (length 2)',
            ('+-----+------------------+\n'
             '| Idx | Data             |\n'
             '+-----+------------------+\n'
             '| 0   | bar              |\n'
             '| 1   | <dict, length 1> |\n'
             '+-----+------------------+'),
            mod_ut.DEFAULT_DIVIDER,
            'At path foo->1',
            'Dict (length 1)',
            ('+-----+-----+------+\n'
             '| Idx | Key | Data |\n'
             '+-----+-----+------+\n'
             '| 0   | baz | 3    |\n'
             '+-----+-----+------+'),
            mod_ut.DEFAULT_DIVIDER,
            'At path foo->1->baz',
            ('+-------+\n'
             '| Value |\n'
             '+-------+\n'
             '| 3     |\n'
             '+-------+'),
            mod_ut.DEFAULT_DIVIDER,
            'At path foo->1',
            'Dict (length 1)',
            ('+-----+-----+------+\n'
             '| Idx | Key | Data |\n'
             '+-----+-----+------+\n'
             '| 0   | baz | 3    |\n'
             '+-----+-----+------+'),
            mod_ut.DEFAULT_DIVIDER,
            'At path foo->1->baz',
            ('+-------+\n'
             '| Value |\n'
             '+-------+\n'
             '| 3     |\n'
             '+-------+'),
            'Bye.'
        ]
        result_print_args = self._extract_print_strings(
            self.fake_print.call_args_list)
        self.assertEqual(result_print_args, target_print_args)


if __name__ == '__main__':
    unittest.main()
