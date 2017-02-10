import six
from six.moves import input as six_input

from delver.table import TablePrinter
from delver.handlers import (
    ListHandler, DictHandler, GenericClassHandler, ValueHandler)
from delver.exceptions import (
    ObjectHandlerInputValidationError, DelverInputError)


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
        self.continue_running = False
        self._basic_input_map = {
            'u': (self._navigate_up, 0), 'q': (self._quit, 1)}
        self.basic_inputs = sorted(
            self._basic_input_map.keys(),
            key=lambda x: self._basic_input_map[x][1])
        self.verbose = verbose
        self.object_handlers = self._initialize_handlers()

    def build_prompt(self, index_descriptor=None):
        """Create the input prompt based on the basic inputs and
        the need for an index, as given by *index_descriptor*.

        :param index_descriptor: the description to use for the index input,
            e.g. 'Key Index'
        :type index_descriptor: ``str``

        :returns: the prompt to be given to the user for input
        :rtype: ``str``
        """
        basic_inputs = ', '.join(self.basic_inputs)
        if index_descriptor is not None:
            prompt = '[<{}>, {}] --> '.format(index_descriptor, basic_inputs)
        else:
            prompt = '[{}] --> '.format(basic_inputs)
        return prompt

    def run(self):
        """Initializes the delver runtime which initiates tables, coordinates
        the control of the currently in-scope object, and handles user input.

        The control flow will continue until :py:attr:`.continue_running` is set
        to ``False`` or a keyboard interrupt is detected.
        """
        obj = self.root_object
        self.continue_running = True
        try:
            while self.continue_running:
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
                inp = six_input(str(prompt))
                obj = self._handle_input(inp, obj, object_handler)
        except (KeyboardInterrupt, EOFError):
            _print('\nBye.')

    def _initialize_handlers(self):
        """Initialize object handler classes based on
        :py:attr:`.object_handler_classes`.

        :returns: list of object handler instances
        :rtype: ``list`` of :py:class:`.BaseObjectHandler`-derivced instances
        """
        instantiated_object_handlers = []
        for handler_class in self.object_handler_classes:
            instantiated_object_handlers.append(
                handler_class(verbose=self.verbose))
        return instantiated_object_handlers

    def _navigate_up(self, obj):
        if len(self.prev_obj) == 0:
            _print("Can't go up a level; we're at the top")
        else:
            obj = self.prev_obj.pop()
            self.path = self.path[:-1]
        return obj

    def _quit(self, obj):
        _print('Bye.')
        self.continue_running = False

    def _handle_input(self, inp, obj, object_handler):
        if self._basic_input_map.get(inp) is not None:
            # Run the associated basic input handler function
            obj = self._basic_input_map[inp][0](obj)
        else:
            try:
                old_obj = obj
                obj, path = object_handler.handle_input(obj, inp)
                self.prev_obj.append(old_obj)
                self.path.append(six.text_type(path))
            except ObjectHandlerInputValidationError as err:
                _print(err.msg)
            except ValueError as err:
                _print("Invalid command; please specify one of "
                        "['<{}>', {}]".format(
                            object_handler.index_descriptor,
                            ', '.join(self.basic_inputs)))
        return obj


def _print(string):
    """Wrapper function used to enable testing of printed output strings"""
    print(string)
