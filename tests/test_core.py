"""Module containing tests for the core module"""
import unittest

from context import core as mod_ut
from context import handlers


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



if __name__ == '__main__':
    unittest.main()
