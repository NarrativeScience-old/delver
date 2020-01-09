"""Module containing object handler classes used by :py:class:`.Delver`"""

import six

from delver.exceptions import DelverInputError, ObjectHandlerInputValidationError


class BaseObjectHandler(object):
    """Base Object Handler class from which other handlers should inherit"""

    #: The object type associated with this handler
    handle_type = None

    #: The description of the input identifier integer, e.g. 'Key Index'
    index_descriptor = None

    #: The format string to wrap the object's path for display in the Delver
    path_modifier = "{}"

    def __init__(self, verbose=False):
        """Instantiate the necessary instance arguments"""
        self._encountered_pointer_map = {}
        self.verbose = verbose

    def check_applies(self, target):
        """Determine whether or not this object handler applies to this object
        based on it's type matching :py:attr:`.handle_type`.

        :returns: if the object is applicable to this handler
        :rtype: ``bool``
        """
        return isinstance(target, self.handle_type)

    def describe(self, target):
        """Create a table of information describing the contents of *target*.
        Must be implemented by child classes.

        :param target: the object to build the table information for

        :returns: a dictionary of information about *target* to be printed in a
            table
        :rtype: ``dict`` containing keys `columns`, `rows`, and optionally
            `description`
        """
        raise NotImplementedError("Child object handlers must overwrite this method")

    def handle_input(self, target, inp):
        """Validate the input and retrieve the relevant attribute of *target*
        based on the *inp*.

        :param target: the object to access
        :param inp: the user input
        :type inp: ``str``

        :returns: the appropriate attribute of *target*

        :raises :py:class:`.ObjectHandlerInputValidationError`: if the input
            is invalid for the given handler
        """
        inp = self._validate_input_for_obj(target, inp)
        return self._object_accessor(target, inp)

    def _object_accessor(self, target, inp):
        """The method called to actually perform the attribute accessing,
        which varies based on :py:attr:`.handle_type`. Must be implemented
        by child classes.

        :returns: the relevant attribute of *target*
        """
        raise NotImplementedError("Child object handlers must overwrite this method")

    def _add_property_map(self, target, index_prop_map):
        """Add an entry to this handler's encountered property map. This
        is used to keep track of the attributes associated with the object
        as well as their corresponding accesor indices.

        This mechanism relies on the fact that the id of the target
        remains the same, as do its attributes.

        :param target: the object to add the property map of
        :param index_prop_map: a mapping of the integers associated with
            *target*'s attributes to the respective attribute
        :type index_prop_map: ``dict``
        """
        self._encountered_pointer_map[id(target)] = index_prop_map

    def _validate_input_for_obj(self, target, inp):
        """Determine whether or not the given raw *inp* is valid for *target*
        as well as adjust *inp*'s type according to what is appropriate for
        this handler. This method can be overridden for more granular control.

        :returns: the input to be used for accessing the object's properties

        :raises :py:class:`.ObjectHandlerInputValidationError`: if the input
            is invalid for the given handler
        """
        try:
            inp = int(inp)
        except ValueError:
            raise DelverInputError("Invalid command")
        if inp not in self._encountered_pointer_map[id(target)].keys():
            raise ObjectHandlerInputValidationError("Invalid Index")
        return inp


class ListHandler(BaseObjectHandler):
    """Object handler for lists"""

    handle_type = list
    index_descriptor = "int"
    path_modifier = "[{}]"

    def describe(self, target):
        """Create the table info for the given list

        :param target: the list to build the table information for

        :returns: a dictionary of information detailing the elements in
            *target* and a high-level description
        :rtype: ``dict``
        """
        rows = []
        if len(target) == 0:
            column_names = ["Data"]
            index_descriptor = None
            rows.append([six.text_type("")])
        else:
            column_names = ["Idx", "Data"]
            index_descriptor = self.index_descriptor
            for i, value in enumerate(target):
                description = _get_object_description(value)
                rows.append([six.text_type(i), six.text_type(description)])
        object_info = {
            "columns": column_names,
            "rows": rows,
            "description": "List (length {})".format(len(target)),
            "index_descriptor": index_descriptor,
        }
        return object_info

    def _object_accessor(self, target, inp):
        """Get the *inp*-th element of *target* and the path accessor string"""
        return target[inp], self.path_modifier.format(inp)

    def _validate_input_for_obj(self, target, inp):
        """Make sure the *inp* is not greater than the length of *target*"""
        msg = None
        inp = int(inp)
        if inp >= len(target):
            msg = "Invalid index `{}`".format(inp)
            raise ObjectHandlerInputValidationError(msg)
        return inp


class DictHandler(BaseObjectHandler):
    """Object handler for dicts"""

    handle_type = dict
    index_descriptor = "key index"
    path_modifier = "[{}]"

    def describe(self, target):
        """Create the table info for the given dict

        :param target: the dict to describe

        :returns: dictionary of information about the keys and values in
            *target*
        :rtype: ``dict``
        """
        keys = sorted([(str(k), k) for k in target.keys()], key=lambda x: x[0])
        index_prop_map = {i: k for i, k in enumerate(keys)}
        self._add_property_map(target, index_prop_map)
        rows = []
        if len(keys) == 0:
            column_names = ["Data"]
            index_descriptor = None
            rows.append([six.text_type("")])
        else:
            column_names = ["Idx", "Key", "Data"]
            index_descriptor = self.index_descriptor
            for i, key_pair in enumerate(keys):
                value = target[key_pair[1]]
                description = _get_object_description(value)
                rows.append(
                    [
                        six.text_type(i),
                        six.text_type(key_pair[0]),
                        six.text_type(description),
                    ]
                )
        object_info = {
            "columns": column_names,
            "rows": rows,
            "index_descriptor": index_descriptor,
            "description": "Dict (length {})".format(len(target)),
        }
        return object_info

    def _object_accessor(self, target, inp):
        """Access the field in *target* associated with the key *inp* according
        to the :py:attr:`._encountered_pointer_map`.

        :param target: the dictionary to access
        :type target: ``dict``
        :param inp: the user-inputted key index associated with the desired
            field to access
        :type inp: ``int``

        :return: a ``tuple`` containing the desired field from *target* and the
            string accessor to describe the key needed to access that field
            directly
        """
        accessor_pair = self._encountered_pointer_map[id(target)][inp]
        if isinstance(accessor_pair[1], six.string_types):
            path_addition = '"{}"'.format(accessor_pair[1])
        else:
            path_addition = "{}".format(accessor_pair[1])
        return (target[accessor_pair[1]], self.path_modifier.format(path_addition))


class GenericClassHandler(BaseObjectHandler):
    """Object handler for any generic object, with functionality for
    optionally delving into the private methods/attributes of objects.
    """

    index_descriptor = "attr index"
    path_modifier = ".{}"
    _builtin_types = (int, float, bool, str, type(None))

    def check_applies(self, target):
        """Use this handler if *target* is not one of the basic built-ins"""
        return not isinstance(target, self._builtin_types)

    def describe(self, target):
        """Find the properties and methods of *target* and return information
        that will be used to build a table. Uses :py:attr:`.verbose` to
        determine whether or not to include private attributes/methods.

        :param target: the targetect to build information for

        :returns: a dictionary of information about *target*'s properties and
            methods
        :rtype: ``dict``
        """
        object_info = {}
        props = [prop for prop in _dir(target)]
        if not self.verbose:
            props = [prop for prop in props if not prop.startswith("_")]
        index_prop_map = {i: k for i, k in enumerate(props)}
        self._add_property_map(target, index_prop_map)
        if len(props) == 0:
            object_info["columns"] = ["Attribute"]
            rows = [[six.text_type(target)]]
            object_info["has_children"] = False
            object_info["index_descriptor"] = None
        else:
            object_info["columns"] = ["Idx", "Attribute", "Data"]
            object_info["index_descriptor"] = self.index_descriptor
            rows = []
            for i, prop in enumerate(props):
                attr = getattr(target, prop)
                description = _get_object_description(attr)
                rows.append(
                    [six.text_type(i), six.text_type(prop), six.text_type(description)]
                )
        object_info["rows"] = rows
        return object_info

    def _object_accessor(self, target, inp):
        """Retrieve the relevant property from *target* based on the property
        index *inp*.

        :param target: the object to retrieve the property from
        :param inp: the integer corresponding to the desired property from the
            :py:attr:`._encountered_pointer_map`
        :type inp: ``int``

        :returns: the desired property
        """
        attr_name = self._encountered_pointer_map[id(target)][inp]
        return getattr(target, attr_name), self.path_modifier.format(attr_name)


class ValueHandler(BaseObjectHandler):
    """Basic handler for single values"""

    has_children = False

    def check_applies(self, target):
        """Since this handler is always valid, simply return `True`"""
        return True

    def describe(self, target):
        """Build simple table info for a single value

        :param target: the value to describe

        :returns: a dictionary of information about the value
        :rtype: ``dict``
        """
        object_info = {}
        object_info["columns"] = ["Value"]
        if target is None:
            description = six.text_type("None")
        else:
            description = six.text_type(target)
        object_info["rows"] = [[description]]
        return object_info


def _get_object_description(target):
    """Return a string describing the *target*"""
    if isinstance(target, list):
        data = "<list, length {}>".format(len(target))
    elif isinstance(target, dict):
        data = "<dict, length {}>".format(len(target))
    else:
        data = target
    return data


def _dir(target):
    """Wrapper function to enable testing of builtin functions"""
    return dir(target)
