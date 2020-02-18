"""Module containing tests for the handlers module"""
import unittest
from unittest import mock

from context import exceptions, handlers as mod_ut


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
            obj_ut.describe("")
        with self.assertRaises(NotImplementedError):
            obj_ut._object_accessor("", "")

    def test_check_applies(self):
        """Ensure the handle type is checked"""
        obj_ut = mod_ut.BaseObjectHandler()
        obj_ut.handle_type = str
        self.assertTrue(obj_ut.check_applies("hello"))

    def test_describe(self):
        """Ensure a not implemented error is raised"""
        obj_ut = mod_ut.BaseObjectHandler()
        with self.assertRaises(NotImplementedError):
            obj_ut.describe({"foo": "bar"})

    def test__object_accessor(self):
        """Ensure a not implemented error is raised"""
        obj_ut = mod_ut.BaseObjectHandler()
        with self.assertRaises(NotImplementedError):
            obj_ut._object_accessor({"foo": "bar"}, "inp")


class TestListHandler(unittest.TestCase):
    """Tests for the ListHandler class"""

    def test_describe(self):
        """Test we return accurate information for a list"""
        obj_ut = mod_ut.ListHandler()
        input_list = [{"foo": "bar"}, True, (0.3, 100)]

        target = {
            "columns": ["Idx", "Data"],
            "description": "Listz (length 3)",
            "index_descriptor": "int",
            "rows": [["0", "<dict, length 1>"], ["1", "True"], ["2", "(0.3, 100)"]],
        }
        result = obj_ut.describe(input_list)
        self.assertDictEqual(result, target)

        # Empty list
        target = {
            "columns": ["Data"],
            "index_descriptor": None,
            "description": "List (length 0)",
            "rows": [[""]],
        }
        result = obj_ut.describe([])
        self.assertDictEqual(result, target)

    def test__object_accessor(self):
        """Test we retrieve an element and return the string accessor"""
        obj_ut = mod_ut.ListHandler()
        target_obj = {"hello": "there"}
        input_list = [0, target_obj, 2]
        result_obj, result_accessor = obj_ut._object_accessor(input_list, 1)
        self.assertDictEqual(result_obj, target_obj)
        self.assertEqual(result_accessor, "[1]")

    def test__validate_input_for_obj(self):
        """Test we validation error is raised if the input is too great"""
        with self.assertRaises(exceptions.ObjectHandlerInputValidationError):
            obj_ut = mod_ut.ListHandler()
            obj_ut._validate_input_for_obj([], 1)


class TestDictHandler(unittest.TestCase):
    """Tests for the DictHandler class"""

    def test_describe(self):
        """Test we return accurate information for a dict"""
        obj_ut = mod_ut.DictHandler()
        input_dict = {"foo": "bar", (1, 3): False, 100: 20.01}

        target = {
            "columns": ["Idx", "Key", "Data"],
            "description": "Dict (length 3)",
            "index_descriptor": "key index",
            "rows": [
                ["0", "(1, 3)", "False"],
                ["1", "100", "20.01"],
                ["2", "foo", "bar"],
            ],
        }
        result = obj_ut.describe(input_dict)
        self.assertDictEqual(result, target)

        # Empty dict
        target = {
            "columns": ["Data"],
            "index_descriptor": None,
            "description": "Dict (length 0)",
            "rows": [[""]],
        }
        result = obj_ut.describe({})
        self.assertDictEqual(result, target)

    def test__object_accessor(self):
        """Test we retrieve an element and return the string accessor"""
        target_obj = {"input_key": "hello there"}
        obj_ut = mod_ut.DictHandler()

        # Make sure this would have been an object already encountered
        obj_ut.describe(target_obj)

        result_obj, result_accessor = obj_ut._object_accessor(target_obj, 0)
        self.assertEqual(result_obj, "hello there")
        self.assertEqual(result_accessor, '["input_key"]')

        # Handle non-string keys
        non_string_dict = {(0, True, None): "foo"}
        obj_ut.describe(non_string_dict)

        result_obj, result_accessor = obj_ut._object_accessor(non_string_dict, 0)
        self.assertEqual(result_obj, "foo")
        self.assertEqual(result_accessor, "[(0, True, None)]")


class TestGenericClassHandler(unittest.TestCase):
    """Tests for the GenericClassHandler object"""

    def row_descriptions_almost_equal(self, result_rows, target_rows):
        """Convenience function for testing attribute description equality"""
        for row_index, row in enumerate(result_rows):
            self.assertEqual(row[:1], target_rows[row_index][:1])
            # For the description cell we check that the result contains the
            # target because by default the memory address is shown in the
            # description, which changes for each run
            self.assertTrue(target_rows[row_index][2] in row[2])

    def test_check_applies__false(self):
        """Make sure we ignore some of the common builtins"""
        obj_ut = mod_ut.GenericClassHandler()
        builtins = [0, 3.0, False, "foo", None]
        for builtin in builtins:
            self.assertFalse(obj_ut.check_applies(builtin))

    def test_check_applies__true(self):
        """Make sure we would handler generic classes"""

        class Foo(object):
            pass

        def some_func(inp):
            return inp + 1

        obj_ut = mod_ut.GenericClassHandler()
        objects = [Foo(), Foo, {}, set(), some_func]
        for generic_object in objects:
            self.assertTrue(obj_ut.check_applies(generic_object))

    def test_describe__normal(self):
        """Test we correctly describe the public attributes of classes"""

        class TestObject(object):
            """A test object for testing"""

            class_attr = "FOO!"

            def __init__(self, inp):
                """Initialize instance args"""
                self.inst_attr_1 = inp
                self.inst_attr_2 = {"blah": True}

            def test_method(self, arg):
                """Do a test thing"""
                return arg + 1

        obj_ut = mod_ut.GenericClassHandler()
        target_columns = ["Idx", "Attribute", "Data"]
        target_rows = [
            ["0", "class_attr", "FOO!"],
            ["1", "inst_attr_1", "woohoo"],
            ["2", "inst_attr_2", "<dict, length 1>"],
            ["3", "test_method", "<bound method Test"],
        ]
        result = obj_ut.describe(TestObject("woohoo"))
        self.assertListEqual(result["columns"], target_columns)
        self.assertEqual(result["index_descriptor"], "attr index")
        self.row_descriptions_almost_equal(result["rows"], target_rows)

    def test_describe__empty(self):
        """Test we correctly describe an empty object"""
        test_obj_description = "test object description!"

        class TestObject(object):
            def __repr__(self):
                return test_obj_description

        obj_ut = mod_ut.GenericClassHandler()
        target = {
            "columns": ["Attribute"],
            "has_children": False,
            "index_descriptor": None,
            "rows": [[test_obj_description]],
        }

        result = obj_ut.describe(TestObject())
        self.assertDictEqual(result, target)

    @mock.patch("delver.handlers._dir")
    def test_describe__verbose(self, fake_dir):
        """Test we correctly describe an generic object verbosely"""
        private_attr = "private attr!"

        class Foo(object):
            def __init__(self):
                self._private_attr = private_attr

        fake_dir.return_value = {"_private_attr": "private attr!"}

        obj_ut = mod_ut.GenericClassHandler(verbose=True)

        target = {
            "columns": ["Idx", "Attribute", "Data"],
            "index_descriptor": "attr index",
            "rows": [["0", "_private_attr", private_attr]],
        }
        result = obj_ut.describe(Foo())
        self.assertDictEqual(result, target)

    def test__object_accessor(self):
        """Test we correctly get the appropriate attribute"""

        class Foo(object):
            def __init__(self):
                self.attr = "foo attr"

        obj_ut = mod_ut.GenericClassHandler()

        # Make sure it's already been encountered
        test = Foo()
        obj_ut.describe(test)

        result_obj, result_accessor = obj_ut._object_accessor(test, 0)
        self.assertEqual(result_obj, "foo attr")
        self.assertEqual(result_accessor, ".attr")


class TestValueHandler(unittest.TestCase):
    """Tests for the ValueHandler class"""

    def test_describe(self):
        """Test we correctly describe a single value"""
        obj_ut = mod_ut.ValueHandler()

        target = {"columns": ["Value"], "rows": [["9001"]]}
        result = obj_ut.describe(9001)
        self.assertDictEqual(result, target)


class TestHandlersFunctions(unittest.TestCase):
    """Tests for the various functions in the handlers module"""

    def test__get_object_description(self):
        """Make sure the string describes different types of objects"""

        class Foo(object):
            def __repr__(self):
                return "Foo object description!"

        self.assertEqual(
            mod_ut._get_object_description(["Foo", "Barr"]), "<list, length 2>"
        )
        self.assertEqual(
            mod_ut._get_object_description({"Foo": "Barr"}), "<dict, length 1>"
        )
        self.assertEqual(
            str(mod_ut._get_object_description(Foo())), "Foo object description!"
        )


if __name__ == "__main__":
    unittest.main()
