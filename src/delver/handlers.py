"""Module containing object handler classes used by :py:class:`.Delver`"""

import hashlib

import six

from delver.exceptions import ObjectHandlerInputValidationError


class BaseObjectHandler(object):
    """Base Object Handler class from which other handlers should inherit"""
    #: The object type associated with this handler
    handle_type = None

    #: The description of the input identifier integer, e.g. 'Key Index'
    index_descriptor = None

    #: The format string to wrap the object's path for display in the Delver
    path_modifier = '{}'

    def __init__(self, verbose=False):
        """Instantiate the necessary instance arguments"""
        self._encountered_pointer_map = {}
        self.verbose = verbose

    def check_applies(self, obj):
        """"Determine whether or not this object handler applies to this object
        based on it's type matching :py:attr:`.handle_type`.

        :returns: if the object is applicable to this handler
        :rtype: ``bool``
        """
        return isinstance(obj, self.handle_type)

    def build_table_info(self, obj):
        """Create a table of information describing the contents of *obj*. Must
        be implemented by child classes.

        :param obj: the object to build the table information for

        :returns: a dictionary of information about *obj* to be printed in a
            table
        :rtype: ``dict`` containing keys `columns`, `rows`, and optionally
            `description`
        """
        raise NotImplementedError(
            'Child object handlers must overwrite this method')

    def handle_input(self, obj, inp):
        """Validate the input and retrieve the relevant attribute of *obj*
        based on the *inp*.

        :param obj: the object to access
        :param inp: the user input
        :type inp: ``str``

        :returns: the appropriate attribute of *obj*

        :raises :py:class:`.ObjectHandlerInputValidationError`: if the input
            is invalid for the given handler
        """
        inp = self._validate_input_for_obj(obj, inp)
        return self._object_accessor(obj, inp)

    def _object_accessor(self, obj, inp):
        """The method called to actually perform the attribute accessing,
        which varies based on :py:attr:`.handle_type`. Must be implemented
        by child classes.

        :returns: the relevant attribute of *obj*
        """
        raise NotImplementedError(
            'Child object handlers must overwrite this method')

    def _add_property_map(self, obj, index_prop_map):
        """Add an entry to this handler's encountered property map. This
        is used to keep track of the attributes associated with the object
        as well as their corresponding accesor indices.

        This mechanism relies on the fact that the id of the obj remains
        the same, as do its attributes.

        :param obj: the object to add the property map of
        :param index_prop_map: a mapping of the integers associated with
            *obj*'s attributes to the respective attribute
        :type index_prop_map: ``dict``
        """
        self._encountered_pointer_map[id(obj)] = index_prop_map

    def _validate_input_for_obj(self, obj, inp):
        """Determine whether or not the given raw *inp* is valid for *obj* as
        well as adjust *inp*'s type according to what is appropriate for this
        handler. This method can be overridden for more granular control.

        :returns: the input to be used for accessing the object's properties

        :raises :py:class:`.ObjectHandlerInputValidationError`: if the input
            is invalid for the given handler
        """
        inp = int(inp)
        if inp not in self._encountered_pointer_map[id(obj)].keys():
            raise ObjectHandlerInputValidationError('Invalid Index')
        return inp


class ListHandler(BaseObjectHandler):
    """Object handler for lists"""
    handle_type = list
    index_descriptor = 'int'
    path_modifier = '[{}]'

    def build_table_info(self, obj):
        """Create the table info for the given list

        :param obj: the list to build the table information for

        :returns: a dictionary of information detailing the elements in *obj*
            and a high-level description
        :rtype: ``dict``
        """
        rows = []
        if len(obj) == 0:
            column_names = ['Data']
            index_descriptor = None
            rows.append([six.text_type('')])
        else:
            column_names = ['Idx', 'Data']
            index_descriptor = self.index_descriptor
            for i, value in enumerate(obj):
                description = _get_object_description(value)
                rows.append([six.text_type(i), six.text_type(description)])
        table_info = {
            'columns': column_names,
            'rows': rows,
            'description': 'List (length {})'.format(len(obj)),
            'index_descriptor': index_descriptor
        }
        return table_info

    def _object_accessor(self, obj, inp):
        """Get the *inp*-th element of *obj* and the path accessor string"""
        return obj[inp], self.path_modifier.format(inp)

    def _validate_input_for_obj(self, obj, inp):
        """Make sure the *inp* is not greater than the length of *obj*"""
        msg = None
        inp = int(inp)
        if inp >= len(obj):
            msg = 'Invalid index `{}`'.format(inp)
            raise ObjectHandlerInputValidationError(msg)
        return inp


class DictHandler(BaseObjectHandler):
    """Object handler for dicts"""
    handle_type = dict
    index_descriptor = 'key index'
    path_modifier = '[{}]'

    def build_table_info(self, obj):
        """Create the table info for the given dict

        :param obj: the dict to describe

        :returns: dictionary of information about the keys and values in *obj*
        :rtype: ``dict``
        """
        keys = sorted([(str(k), k) for k in obj.keys()], key=lambda x: x[0])
        index_prop_map = {i: k for i, k in enumerate(keys)}
        self._add_property_map(obj, index_prop_map)
        rows = []
        if len(keys) == 0:
            column_names = ['Data']
            index_descriptor = None
            rows.append([six.text_type('')])
        else:
            column_names = ['Idx', 'Key', 'Data']
            index_descriptor = self.index_descriptor
            for i, key_pair in enumerate(keys):
                value = obj[key_pair[1]]
                description = _get_object_description(value)
                rows.append(
                    [six.text_type(i), six.text_type(key_pair[0]),
                     six.text_type(description)])
        table_info = {
            'columns': column_names,
            'rows': rows,
            'index_descriptor': index_descriptor,
            'description': 'Dict (length {})'.format(len(obj))
        }
        return table_info

    def _object_accessor(self, obj, inp):
        """Access the field in *obj* associated with the key *inp* according
        to the :py:attr:`._encountered_pointer_map`.

        :param obj: the dictionary to access
        :type obj: ``dict``
        :param inp: the user-inputted key index associated with the desired
            field to access
        :type inp: ``int``

        :return: a ``tuple`` containing the desired field from *obj* and the
            string accessor to describe the key needed to access that field
            directly
        """
        accessor_pair = self._encountered_pointer_map[id(obj)][inp]
        if isinstance(accessor_pair[1], six.string_types):
            path_addition = '"{}"'.format(accessor_pair[1])
        else:
            path_addition = '{}'.format(accessor_pair[1])
        return (
            obj[accessor_pair[1]], self.path_modifier.format(path_addition))


class GenericClassHandler(BaseObjectHandler):
    """Object handler for any generic object, with functionality for
    optionally delving into the private methods/attributes of objects.
    """
    index_descriptor = 'attr index'
    path_modifier = '.{}'
    _builtin_types = (int, float, bool, str, type(None))

    def check_applies(self, obj):
        """Only use this handler if *obj* is not one of the basic built-ins"""
        return not isinstance(obj, self._builtin_types)

    def build_table_info(self, obj):
        """Find the properties and methods of *obj* and return information that
        will be used to build a table. Uses :py:attr:`.verbose` to determine
        whether or not to include private attributes/methods.

        :param obj: the object to build information for

        :returns: a dictionary of information about *obj*'s properties and
            methods
        :rtype: ``dict``
        """
        table_info = {}
        props = [prop for prop in _dir(obj)]
        if not self.verbose:
            props = [prop for prop in props if not prop.startswith('_')]
        index_prop_map = {i: k for i, k in enumerate(props)}
        self._add_property_map(obj, index_prop_map)
        if len(props) == 0:
            table_info['columns'] = ['Attribute']
            rows = [[six.text_type(obj)]]
            table_info['has_children'] = False
            table_info['index_descriptor'] = None
        else:
            table_info['columns'] = ['Idx', 'Attribute', 'Data']
            table_info['index_descriptor'] = self.index_descriptor
            rows = []
            for i, prop in enumerate(props):
                attr = getattr(obj, prop)
                description = _get_object_description(attr)
                rows.append(
                    [six.text_type(i), six.text_type(prop),
                     six.text_type(description)])
        table_info['rows'] = rows
        return table_info

    def _object_accessor(self, obj, inp):
        """Retrieve the relevant property from *obj* based on the property index
        *inp*.

        :param obj: the object to retrieve the property from
        :param inp: the integer corresponding to the desired property from the
            :py:attr:`._encountered_pointer_map`
        :type inp: ``int``

        :returns: the desired property
        """
        attr_name = self._encountered_pointer_map[id(obj)][inp]
        return getattr(obj, attr_name), self.path_modifier.format(attr_name)


class ValueHandler(BaseObjectHandler):
    has_children = False

    def check_applies(self, obj):
        """Since this handler is always valid, simply return `True`"""
        return True

    def build_table_info(self, obj):
        """Build simple table info for a single value

        :param obj: the value to describe

        :returns: a dictionary of information about the value
        :rtype: ``dict``
        """
        table_info = {}
        table_info['columns'] = ['Value']
        if obj is None:
            description = six.text_type('None')
        else:
            description = six.text_type(obj)
        table_info['rows'] = [[description]]
        return table_info


def _get_object_description(obj):
    """Return a string describing the *obj*"""
    if isinstance(obj, list):
        data = '<list, length {}>'.format(len(obj))
    elif isinstance(obj, dict):
        data = '<dict, length {}>'.format(len(obj))
    else:
        data = obj
    return data


def _dir(obj):
    """Wrapper function to enable testing of builtin functions"""
    return dir(obj)
