import hashlib

import six

BUILTIN_TYPES = (int, float, bool, str, type(None))


class BaseObjectHandler(object):
    handle_type = None
    index_descriptor = None
    has_children = True
    path_modifier = '{}'

    def __init__(self, verbose=False):
        self.encountered_pointer_map = {}
        self.verbose = verbose

    def check_applies(self, obj):
        if isinstance(obj, self.handle_type):
            return True
        else:
            return False

    def build_table_info(self, obj):
        pass

    def object_accessor(self, obj, inp):
        pass

    def add_property_map(self, obj, index_prop_map):
        self.encountered_pointer_map[id(obj)] = index_prop_map

    def validate_input_for_obj(self, obj, inp):
        if inp in self.encountered_pointer_map[id(obj)].keys():
            return True, None
        else:
            return False, 'Invalid Index'

class ListHandler(BaseObjectHandler):
    handle_type = list
    index_descriptor = 'int'
    path_modifier = '[{}]'

    def build_table_info(self, obj):
        rows = []
        if len(obj) == 0:
            column_names = ['Data']
            index_descriptor = None
            rows.append([six.text_type('')])
        else:
            column_names = ['Idx', 'Data']
            index_descriptor = self.index_descriptor
            for i, value in enumerate(obj):
                description = get_object_description(value)
                rows.append([six.text_type(i), six.text_type(description)])
        table_info = {
            'columns': column_names,
            'rows': rows,
            'description': 'List (length {})'.format(len(obj)),
            'index_descriptor': index_descriptor
        }
        return table_info

    def object_accessor(self, obj, inp):
        return obj[inp], self.path_modifier.format(inp)

    def validate_input_for_obj(self, obj, inp):
        msg = None
        if inp >= len(obj):
            msg = 'Invalid index `{}`'.format(inp)
            return False, msg
        return True, msg


class DictHandler(BaseObjectHandler):
    handle_type = dict
    index_descriptor = 'key index'
    path_modifier = '[{}]'

    def build_table_info(self, obj):
        keys = sorted([(str(k), k) for k in obj.keys()], key=lambda x: x[0])
        index_prop_map = {i: k for i, k in enumerate(keys)}
        self.add_property_map(obj, index_prop_map)
        rows = []
        for i, key_pair in enumerate(keys):
            value = obj[key_pair[1]]
            description = get_object_description(value)
            rows.append(
                [six.text_type(i), six.text_type(key_pair[0]),
                 six.text_type(description)])
        table_info = {
            'columns': ['Idx', 'Key', 'Data'],
            'rows': rows,
            'index_descriptor': self.index_descriptor,
            'description': 'Dict (length {})'.format(len(obj))
        }
        return table_info

    def object_accessor(self, obj, inp):
        accessor_pair = self.encountered_pointer_map[id(obj)][inp]
        if isinstance(accessor_pair[1], str):
            path_addition = '"{}"'.format(accessor_pair[1])
        else:
            path_addition = '{}'.format(accessor_pair[1])
        return (
            obj[accessor_pair[1]], self.path_modifier.format(path_addition))


class GenericClassHandler(BaseObjectHandler):
    index_descriptor = 'attr index'
    path_modifier = '.{}'

    def check_applies(self, obj):
        return not isinstance(obj, BUILTIN_TYPES)

    def build_table_info(self, obj):
        table_info = {}
        props = [prop for prop in dir(obj)] #  if not prop.startswith('_')
        if not self.verbose:
            props = [prop for prop in props if not prop.startswith('_')]
        index_prop_map = {i: k for i, k in enumerate(props)}
        self.add_property_map(obj, index_prop_map)
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
                description = get_object_description(attr)
                rows.append(
                    [six.text_type(i), six.text_type(prop),
                     six.text_type(description)])
        table_info['rows'] = rows
        return table_info

    def object_accessor(self, obj, inp):
        attr_name = self.encountered_pointer_map[id(obj)][inp]
        return getattr(obj, attr_name), self.path_modifier.format(attr_name)


class ValueHandler(BaseObjectHandler):
    has_children = False

    def check_applies(self, obj):
        return True

    def build_table_info(self, obj):
        table_info = {}
        table_info['columns'] = ['Value']
        if obj is None:
            description = six.text_type('None')
        else:
            description = six.text_type(obj)
        table_info['rows'] = [[description]]
        return table_info


def get_object_description(obj):
    if isinstance(obj, list):
        data = '<list, length {}>'.format(len(obj))
    elif isinstance(obj, dict):
        data = '<dict, length {}>'.format(len(obj))
    else:
        data = obj
    return data
