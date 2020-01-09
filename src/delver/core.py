"""Module containing the core :py:class:`Delver` object."""
from collections import namedtuple, OrderedDict

import six
from six.moves import input as six_input

from delver.exceptions import DelverInputError, ObjectHandlerInputValidationError
from delver.handlers import DictHandler, GenericClassHandler, ListHandler, ValueHandler
from delver.table import TablePrinter

DEFAULT_DIVIDER = "-" * 79


class Delver(object):
    """Object used for exploring arbitrary python objects.

    This class creates the runtime, manages state/user input, and coordinates
    the various object handler classes.

    The primary method is :py:meth:`run`, which starts the runtime.
    """

    object_handler_classes = [
        ListHandler,
        DictHandler,
        GenericClassHandler,
        ValueHandler,
    ]

    def __init__(self, target, verbose=False, use_colors=False):
        """Initialize the relevant instance variables.

        This includes the object handlers as well as those variables
        representing the runtime state.

        :param target: the object to delve into
        :param verbose: whether or not to allow object handlers to be verbose
        :type verbose: ``bool``
        """
        # The initial object which is set to enable returning to original state
        self._root_object = target

        # A named tuple to store information about the path, including
        # a 'path' attribute which is a list of object accessor strings
        # (like '["foo"]', '[0]'), and a 'previous' attribute which is just
        # a pointer to the previous object
        self._path = namedtuple("path", ["path", "previous"])
        self._path.path = ["root"]
        self._path.previous = []

        # The indicator for whether or not to continue program flow
        self._continue_running = False

        # An ordered mapping of possible user input commands to the function to
        # use if that input is selected
        self._basic_input_map = OrderedDict()
        self._basic_input_map["u"] = self._navigate_up
        self._basic_input_map["q"] = self._quit

        # Whether or not to allow object handlers to be verbose
        self._verbose = verbose

        self._use_colors = use_colors

        # The instantiated object handler classes from the class attribute
        # :py:attr:`.object_handler_classes`
        self._object_handlers = self._initialize_handlers()

    def _build_prompt(self, index_descriptor=None):
        """Create the user input prompt based on the possible commands.

        Builds the prompt from the :py:attr:`._basic_input_map`, taking into
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
        basic_inputs = ", ".join(self._basic_input_map.keys())
        if index_descriptor is not None:
            prompt = "[<{}>, {}] --> ".format(index_descriptor, basic_inputs)
        else:
            prompt = "[{}] --> ".format(basic_inputs)
        return prompt

    def run(self):
        """Initialize the delver runtime.

        Handle initiating tables, coordinating the control of the currently
        in-scope object, and handle user input.

        The control flow will continue until :py:attr:`._continue_running` is
        set to ``False`` or a keyboard interrupt is detected.
        """
        target = self._root_object
        self._continue_running = True
        try:
            while self._continue_running:
                table = TablePrinter(use_colors=self._use_colors)
                for object_handler in self._object_handlers:
                    if object_handler.check_applies(target):
                        object_info = object_handler.describe(target)
                        table.build_from_info(object_info)
                        prompt = self._build_prompt(
                            index_descriptor=object_info.get("index_descriptor")
                        )
                        break

                self.print_table(table, description=object_info.get("description"))
                inp = six_input(str(prompt))
                target = self._handle_input(inp, target, object_handler)
        except (KeyboardInterrupt, EOFError):
            self.print_message("\nBye.")

    def print_table(self, table, description=None):
        """Prints the table and other supporting information for the view.

        This includes the divider to separate the view from other the previous
        one, the current path in the object, and a description of the current
        object.

        :param table: the table instance which contains the ascii table and
            cells
        :type table: :py:class:`.TablePrinter`
        :param description: an optional object description
        :type description: ``str``
        """
        view = []
        view.append(DEFAULT_DIVIDER)
        if len(self._path.path) > 0:
            view.append("At path: {}".format("".join(self._path.path)))
        if description is not None:
            view.append(description)
        view.append(str(table))
        six.print_("\n".join(view))

    def print_message(self, message):
        """Prints a generic message, generally either a warning or error"""
        six.print_(message)

    def _initialize_handlers(self):
        """Initialize handlers based on :py:attr:`._object_handler_classes`.

        :returns: list of object handler instances
        :rtype: ``list`` of :py:class:`.BaseObjectHandler`-derivced instances
        """
        instantiated_object_handlers = []
        for handler_class in self.object_handler_classes:
            instantiated_object_handlers.append(handler_class(verbose=self._verbose))
        return instantiated_object_handlers

    def _navigate_up(self, target):
        """Move to the previous parent object, making use of :py:attr:`._path`.

        :param target: the object representing the current location

        :returns: the parent object based on :py:attr:`._path`
        """
        if len(self._path.previous) == 0:
            self.print_message("Can't go up a level; we're at the top")
        else:
            target = self._path.previous.pop()
            self._path.path = self._path.path[:-1]
        return target

    def _quit(self, target):
        """End the primary program flow."""
        self.print_message("Bye.")
        self._continue_running = False

    def _handle_input(self, inp, target, object_handler):
        """Coordinate performing actions based on the user input.

        Checks the *inp* against the basic functions first, then attempts to
        use the *object_handler*'s own input handler.

        :param inp: the user-given input
        :type inp: ``str``
        :param target: the current object
        :param object_handler: the object handler which was applied to *target*
            for delving
        :type object_handler: :py:class:`.BaseObjectHandler`

        :returns: a (potentially) new object based on how the input is handled
        """
        if self._basic_input_map.get(inp) is not None:
            # Run the associated basic input handler function
            target = self._basic_input_map[inp](target)
        else:
            new_path = None
            try:
                old_target = target
                target, new_path = object_handler.handle_input(target, inp)
            except ObjectHandlerInputValidationError as err:
                self.print_message(err.msg)
            except DelverInputError:
                msg = ("Invalid command; please specify" " one of ['<{}>', {}]").format(
                    object_handler.index_descriptor,
                    ", ".join(self._basic_input_map.keys()),
                )
                self.print_message(msg)
            if new_path is not None:
                self._path.previous.append(old_target)
                self._path.path.append(six.text_type(new_path))
        return target


def run(target, **kwargs):
    """Initialize and begin execution of a :py:class:`Delver` object"""
    delver = Delver(target, **kwargs)
    delver.run()
