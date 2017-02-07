import six
from six.moves import input as six_input

from delver.table import TablePrinter
from delver.handlers import (
    ListHandler, DictHandler, GenericClassHandler, ValueHandler)


DEFAULT_DIVIDER = '-' * 79


class Delver(object):
    """Object for delving"""
    object_handler_classes = [
        ListHandler, DictHandler, GenericClassHandler, ValueHandler
    ]
    def __init__(self, obj, verbose=False):
        self.root_object = obj
        self.path = ['root']
        self.prev_obj = []
        self.running = False
        self.basic_inputs = ['u', 'q']
        self.verbose = verbose
        self.object_handlers = self._initialize_handlers()

    def _initialize_handlers(self):
        instantiated_object_handlers = []
        for handler_class in self.object_handler_classes:
            instantiated_object_handlers.append(
                handler_class(verbose=self.verbose))
        return instantiated_object_handlers

    def build_prompt(self, index_descriptor=None):
        basic_inputs = ', '.join(self.basic_inputs)
        if index_descriptor is not None:
            prompt = '[<{}>, {}] --> '.format(
                index_descriptor, basic_inputs)
        else:
            prompt = '[{}] --> '.format(basic_inputs)
        return prompt

    def run(self):
        obj = self.root_object
        self.running = True
        try:
            while self.running:
                table = TablePrinter()
                _print(DEFAULT_DIVIDER)
                if len(self.path) > 0:
                    _print(('At path: {}'.format(''.join(self.path))))
                for object_handler in self.object_handlers:
                    if object_handler.check_applies(obj):
                        table_info = object_handler.build_table_info(obj)
                        if table_info.get('description') is not None:
                            _print(table_info['description'])
                        table.build_from_info(table_info)
                        prompt = self.build_prompt(
                            index_descriptor=table_info.get('index_descriptor'))
                        break

                _print((six.text_type(table)))
                obj = self._handle_input(prompt, obj, object_handler)
        except (KeyboardInterrupt, EOFError):
            _print('\nBye.')

    def _handle_input(self, prompt, obj, object_handler):
        inp = six_input(str(prompt))
        if inp == 'u':
            if len(self.prev_obj) == 0:
                _print("Can't go up a level; we're at the top")
            else:
                obj = self.prev_obj.pop()
                self.path = self.path[:-1]
        elif inp == 'q':
            _print('Bye.')
            self.running = False
        else:
            if not object_handler.has_children:
                _print('Invalid command; please specify one of [{}]'.format(
                    ', '.join(self.basic_inputs)))
            else:
                try:
                    inp = int(inp)
                    is_valid, error_msg = object_handler.validate_input_for_obj(
                        obj, inp)
                    if not is_valid:
                        _print(error_msg)
                    else:
                        self.prev_obj.append(obj)
                        obj, path = object_handler.object_accessor(obj, inp)
                        self.path.append(six.text_type(path))
                except ValueError:
                    _print(
                        "Invalid command; please specify one of "
                        "['<{}>', {}".format(
                            object_handler.index_descriptor,
                            ', '.join(self.basic_inputs)))
        return obj


def _print(string):
    """Wrapper function used to enable testing of printed output strings"""
    print(string)
