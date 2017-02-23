"""Module containing the core :py:class:`Delver` object."""
import six
from six.moves import input as six_input

from delver.table import TablePrinter
from delver.handlers import (
    ListHandler, DictHandler, GenericClassHandler, ValueHandler)
from delver.exceptions import (
    ObjectHandlerInputValidationError, DelverInputError)


DEFAULT_DIVIDER = '-' * 79


class Delver(object):
    """Object used for exploring arbitrary python objects.

    This class creates the runtime, manages state/user input, and coordinates
    the various object handler classes.

    The primary method is :py:meth:`run`, which starts the runtime.
    """

    object_handler_classes = [
        ListHandler, DictHandler, GenericClassHandler, ValueHandler
    ]

    def __init__(self, obj, verbose=False):
        """Initialize the relevant instance variables.

        This includes the object handlers as well as those variables
        representing the runtime state.

        :param obj: the object to delve into
        :param verbose: whether or not to allow object handlers to be verbose
        :type verbose: ``bool``
        """
        # The initial object which is set to enable returning to original state
        self._root_object = obj

        # The list of object accessor strings for each level in the path, e.g.
        # ['root', '[0]', "['foo']"]
        self._path = ['root']

        # The last object, used to jump back up the hierarchy
        self._prev_obj = []

        # The indicator for whether or not to continue program flow
        self._continue_running = False

        # A mapping of possible user input commands to a tuple of
        # the function to use if that input is selected and the
        # index indicating that command's order in the list of possible inputs
        self._basic_input_map = {
            'u': (self._navigate_up, 0), 'q': (self._quit, 1)}

        # The list of raw user input commands sorted according to their index
        # in the above mapping
        self._basic_inputs = sorted(
            self._basic_input_map.keys(),
            key=lambda x: self._basic_input_map[x][1])

        # Whether or not to allow object handlers to be verbose
        self._verbose = verbose

        # The instantiated object handler classes from the class attribute
        # :py:attr:`.object_handler_classes`
        self._object_handlers = self._initialize_handlers()

    def _build_prompt(self, index_descriptor=None):
        """Create the user input prompt based on the possible commands.

        Builds the prompt from the :py:attr:`._basic_inputs`, taking into
        account the need for an index, as given by *index_descriptor*. An
        example would be '[<Key Index>, u, q] --> ' if *index_descriptor* was
        'Key Index'. If *index_descriptor is `None`, then the prompt would
        simply be '[u, q] --> '.

        :param index_descriptor: the description to use for the index input,
            e.g. 'Key Index'
        :type index_descriptor: ``str``

        :returns: the prompt to be given to the user for input
        :rtype: ``str``
        """
        basic_inputs = ', '.join(self._basic_inputs)
        if index_descriptor is not None:
            prompt = '[<{}>, {}] --> '.format(index_descriptor, basic_inputs)
        else:
            prompt = '[{}] --> '.format(basic_inputs)
        return prompt

    def run(self):
        """Initialize the delver runtime.

        Handle initiating tables, coordinating the control of the currently
        in-scope object, and handle user input.

        The control flow will continue until :py:attr:`._continue_running` is
        set to ``False`` or a keyboard interrupt is detected.
        """
        obj = self._root_object
        self._continue_running = True
        try:
            while self._continue_running:
                table = TablePrinter()
                _print(DEFAULT_DIVIDER)
                if len(self._path) > 0:
                    _print(('At path: {}'.format(''.join(self._path))))
                for object_handler in self._object_handlers:
                    if object_handler.check_applies(obj):
                        table_info = object_handler.build_table_info(obj)
                        if table_info.get('description') is not None:
                            _print(table_info['description'])
                        table.build_from_info(table_info)
                        prompt = self._build_prompt(
                            index_descriptor=table_info.get('index_descriptor'))
                        break

                _print((six.text_type(table)))
                inp = six_input(str(prompt))
                obj = self._handle_input(inp, obj, object_handler)
        except (KeyboardInterrupt, EOFError):
            _print('\nBye.')

    def _initialize_handlers(self):
        """Initialize handlers based on :py:attr:`._object_handler_classes`.

        :returns: list of object handler instances
        :rtype: ``list`` of :py:class:`.BaseObjectHandler`-derivced instances
        """
        instantiated_object_handlers = []
        for handler_class in self.object_handler_classes:
            instantiated_object_handlers.append(
                handler_class(verbose=self._verbose))
        return instantiated_object_handlers

    def _navigate_up(self, obj):
        """Move to the previous parent object, making use of :py:attr:`._path`.

        :param obj: the object representing the current location

        :returns: the parent object based on :py:attr:`._path`
        """
        if len(self._prev_obj) == 0:
            _print("Can't go up a level; we're at the top")
        else:
            obj = self._prev_obj.pop()
            self._path = self._path[:-1]
        return obj

    def _quit(self, obj):
        """End the primary program flow."""
        _print('Bye.')
        self._continue_running = False

    def _handle_input(self, inp, obj, object_handler):
        """Coordinate performing actions based on the user input.

        Checks the *inp* against the basic functions first, then attempts to use
        the *object_handler*'s own input handler.

        :param inp: the user-given input
        :type inp: ``str``
        :param obj: the current object
        :param object_handler: the object handler which was applied to *obj*
            for delving
        :type object_handler: :py:class:`.BaseObjectHandler`

        :returns: a (potentially) new obj based on how the input is handled
        """
        if self._basic_input_map.get(inp) is not None:
            # Run the associated basic input handler function
            obj = self._basic_input_map[inp][0](obj)
        else:
            new_path = None
            try:
                old_obj = obj
                obj, new_path = object_handler.handle_input(obj, inp)
            except ObjectHandlerInputValidationError as err:
                _print(err.msg)
            except ValueError as err:
                msg = (
                    "Invalid command; please specify one of ['<{}>', {}]".format(
                        object_handler.index_descriptor,
                        ', '.join(self._basic_inputs)))
                _print(msg)
            if new_path is not None:
                self._prev_obj.append(old_obj)
                self._path.append(six.text_type(new_path))
        return obj


def _print(string):
    """Wrapper function used to enable testing of printed output strings."""
    print(string)
