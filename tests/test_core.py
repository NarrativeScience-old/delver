"""Module containing tests for the core module"""
import unittest

import mock

from context import core as mod_ut
from context import handlers
from context import exceptions


class TestDelver(unittest.TestCase):
    """Tests for the Delver class"""
    def setUp(self):
        """Create any useful features for use in each test"""
        self.obj = {'foo': 'bar'}

    def test_initialization(self):
        """Ensure correct instance args are created"""
        obj_ut = mod_ut.Delver(self.obj)
        self.assertIsInstance(obj_ut, mod_ut.Delver)
        self.assertFalse(obj_ut.verbose)

        # Instance args correctly persisted
        obj_ut = mod_ut.Delver(self.obj, verbose=True)
        self.assertTrue(obj_ut.verbose)

        # Object handlers instantiated
        self.assertTrue(len(obj_ut.object_handlers) > 0)
        for handler in obj_ut.object_handlers:
            self.assertIsInstance(handler, handlers.BaseObjectHandler)

    def test_build_prompt(self):
        """Test the prompt either appropriately contains the index descriptor"""
        obj_ut = mod_ut.Delver(self.obj)
        prompt = obj_ut.build_prompt()
        self.assertEqual(prompt, '[u, q] --> ')

        with_index_prompt = obj_ut.build_prompt(index_descriptor='Key Index')
        self.assertEqual(with_index_prompt, '[<Key Index>, u, q] --> ')

    def test__handle_input__basic_input(self):
        """Ensure we try to handle basic inputs first"""
        fake_obj_handler = mock.Mock()
        fake_handle_input = mock.Mock()
        fake_obj_handler.handle_input = fake_handle_input

        fake_do_thing = mock.Mock()
        new_basic_input_map = {
            'do-the-thing': (fake_do_thing, 0)
        }
        obj_ut = mod_ut.Delver(self.obj)
        obj_ut._basic_input_map = new_basic_input_map

        obj_ut._handle_input('do-the-thing', self.obj, fake_obj_handler)
        fake_do_thing.assert_called_once()
        fake_handle_input.assert_not_called()

    def test__handle_input__obj_handler_normal(self):
        """Ensure we fall back to trying the object handler"""
        fake_obj_handler = mock.Mock()
        fake_handle_input = mock.Mock()
        fake_handle_input.side_effect = lambda obj, inp: (obj['foo'], 'blah')
        fake_obj_handler.handle_input = fake_handle_input

        fake_do_thing = mock.Mock()
        new_basic_input_map = {
            'basic-doer': (fake_do_thing, 0)
        }
        obj_ut = mod_ut.Delver(self.obj)
        obj_ut._basic_input_map = new_basic_input_map

        result = obj_ut._handle_input(
            'custom-thing', {'foo': 'bar'}, fake_obj_handler)
        fake_do_thing.assert_not_called()
        fake_handle_input.assert_called()
        self.assertEqual(result, 'bar')

    @mock.patch('delver.core._print')
    def test__handle_input__obj_handler_catch_exceptiosn(self, fake_print):
        """Make sure we catch errors from object handler"""
        obj_ut = mod_ut.Delver(self.obj)

        def raise_handler_error(obj, inp):
            raise exceptions.ObjectHandlerInputValidationError('nope nope')
        fake_handle_input = mock.Mock()
        fake_handle_input.side_effect = raise_handler_error
        fake_obj_handler = mock.Mock()
        fake_obj_handler.handle_input = fake_handle_input

        input_obj = {'foo': 'bar'}
        result = obj_ut._handle_input(
            'custom-thing', input_obj, fake_obj_handler)
        fake_handle_input.assert_called()
        self.assertEqual(fake_print.call_args_list[0][0][0], 'nope nope')
        self.assertEqual(result, input_obj)

        # Check value error handling
        def raise_value_error(obj, inp):
            raise ValueError('no can do')
        fake_handle_input.side_effect = raise_value_error
        fake_obj_handler.index_descriptor = 'Mock Index'
        result = obj_ut._handle_input(
            'custom-thing', input_obj, fake_obj_handler)
        fake_handle_input.assert_called()
        self.assertEqual(
            fake_print.call_args_list[1][0][0],
            "Invalid command; please specify one of ['<Mock Index>', u, q]")
        self.assertEqual(result, input_obj)


if __name__ == '__main__':
    unittest.main()
