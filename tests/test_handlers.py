"""Module containing tests for the handlers module"""
import unittest

from context import handlers as mod_ut


class TestBaseObjectHandlerr(unittest.TestCase):
    """Tests for the BaseObjectHandler class"""
    def test_initialization(self):
        """Ensure correct instance args are created"""
        obj_ut = mod_ut.BaseObjectHandler()
        self.assertIsInstance(obj_ut, mod_ut.BaseObjectHandler)
        self.assertFalse(obj_ut.verbose)

        # Instance args correctly persisted
        obj_ut = mod_ut.BaseObjectHandler(verbose=True)
        self.assertTrue(obj_ut.verbose)

    def test_raises_not_implemented(self):
        """Test the required methods raise not implemented errors"""
        obj_ut = mod_ut.BaseObjectHandler()
        with self.assertRaises(NotImplementedError):
            obj_ut.build_table_info('')
        with self.assertRaises(NotImplementedError):
            obj_ut._object_accessor('', '')

    def test_check_applies(self):
        """Ensure the handle type is checked"""
        obj_ut = mod_ut.BaseObjectHandler()
        obj_ut.handle_type = str
        self.assertTrue(obj_ut.check_applies('hello'))


if __name__ == '__main__':
    unittest.main()
