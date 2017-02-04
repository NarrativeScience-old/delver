import hashlib

import six

BUILTIN_TYPES = (int, float, bool, str)


class BaseObjectHandler(object):
    handle_type = None

    def __init__(self):
        self.encountered_pointer_map = {}

    def check_applies(self, obj):
        if isinstance(obj, self.handle_type):
            return True
        else:
            return False

    def build_table_and_prompt(self, obj, table):
        pass

    def object_accessor(self, obj, inp):
        pass

    def add_property_map(self, obj, index_prop_map):
        self.encountered_pointer_map[id(obj)] = index_prop_map


class ListHandler(BaseObjectHandler):
    handle_type = list
    def build_table_and_prompt(self, obj, table):
        print(('List (length {})'.format(len(obj))))
        prompt = '[<int>, u, q] --> '
        table.add_row(('Idx', 'Data'), header=True)
        for i, value in enumerate(obj):
            description = get_object_description(value)
            table.add_row((six.text_type(i), six.text_type(description)))
        return prompt

    def object_accessor(self, obj, inp):
        return obj[inp], inp


class DictHandler(BaseObjectHandler):
    handle_type = dict
    def build_table_and_prompt(self, obj, table):
        print(('Dict (length {})'.format(len(obj))))
        prompt = '[<key index>, u, q] --> '
        keys = sorted([(str(k), k) for k in obj.keys()], key=lambda x: x[0])
        index_prop_map = {i: k for i, k in enumerate(keys)}
        self.add_property_map(obj, index_prop_map)
        table.add_row(('Idx', 'Key', 'Data'), header=True)
        for i, key_pair in enumerate(keys):
            value = obj[key_pair[1]]
            description = get_object_description(value)
            table.add_row(
                (six.text_type(i), six.text_type(key_pair[0]),
                 six.text_type(description)))
        return prompt

    def object_accessor(self, obj, inp):
        accessor_pair = self.encountered_pointer_map[id(obj)][inp]
        return obj[accessor_pair[1]], accessor_pair[0]


class GenericValueHandler(BaseObjectHandler):
    def check_applies(self, obj):
        return True

    def build_table_and_prompt(self, obj, table):
        if isinstance(obj, BUILTIN_TYPES):
            table.add_row(('Value',), header=True)
            table.add_row((six.text_type(obj),))
            prompt = '[u, q] --> '
        else:
            table.add_row(('Idx', 'Attribute', 'Data'), header=True)
            public_props = [
                prop for prop in dir(obj) if not prop.startswith('__')]
            index_prop_map = {i: k for i, k in enumerate(public_props)}
            self.add_property_map(obj, index_prop_map)
            for i, prop in enumerate(public_props):
                attr = getattr(obj, prop)
                description = get_object_description(attr)
                table.add_row(
                    (six.text_type(i), six.text_type(prop),
                     six.text_type(description)))
            prompt = '[<attr index>, u, q] --> '
        return prompt

    def object_accessor(self, obj, inp):
        attr_name = self.encountered_pointer_map[id(obj)][inp]
        return getattr(obj, attr_name), attr_name


def get_object_description(obj):
    if isinstance(obj, list):
        data = '<list, length {}>'.format(len(obj))
    elif isinstance(obj, dict):
        data = '<dict, length {}>'.format(len(obj))
    else:
        data = obj
    return data
