import six
from six.moves import input as six_input

from delver.table import TablePrinter
from delver.handlers import (ListHandler, DictHandler, GenericValueHandler)


DEFAULT_DIVIDER = '-' * 79


class Delver(object):
    """Object for delving"""
    object_handlers = [
        ListHandler(), DictHandler(), GenericValueHandler()
    ]
    def __init__(self, obj):
        self.table = TablePrinter()
        self.root_object = obj
        self.path = []
        self.prev_obj = []
        self.running = False

    def run(self):
        obj = self.root_object
        self.running = True
        try:
            while self.running:
                table = TablePrinter()
                print(DEFAULT_DIVIDER)
                if len(self.path) > 0:
                    print(('At path {}'.format("->".join(self.path))))
                for object_handler in self.object_handlers:
                    if object_handler.check_applies(obj):
                        prompt = object_handler.build_table_and_prompt(
                            obj, table)
                        break

                print((six.text_type(table)))
                obj = self._handle_input(prompt, obj, object_handler)
        except (KeyboardInterrupt, EOFError):
            print('\nBye.')

    def _handle_input(self, prompt, obj, object_handler):
        inp = six_input(str(prompt))
        if inp == 'u':
            if len(self.prev_obj) == 0:
                print("Can't go up a level; we're at the top")
            else:
                obj = self.prev_obj.pop()
                self.path = self.path[:-1]
        elif inp == 'q':
            print('Bye.')
            self.running = False
        else:
            try:
                inp = int(inp)
                self._validate_input_for_obj(inp, obj)
                self.prev_obj.append(obj)
                obj, path = object_handler.object_accessor(obj, inp)
                self.path.append(six.text_type(path))
            except ValueError:
                print(
                    "Invalid command; please specify one of '<key index>'"
                    ", 'u', 'q'")
        return obj

    def _validate_input_for_obj(self, inp, obj):
        try:
            if inp >= len(obj):
                print("Invalid index")
        except TypeError:
            pass


if __name__ == '__main__':
    class Bar(object):
        pass

    class Foo(object):
        def __init__(self):
            self.attr1 = 1
            self.attr2 = 'b'
            self.deep_struct = {
                'bar': Bar(),
                'other': [
                    {3: 1, 4: 2},
                    [['a', 'blah', 3.122]]
                ],
                'self': self
            }

        def my_method(self, a):
            return a + 1

    my_foo = Foo()
    obj = {'foo': my_foo, 'a': True, 100: 1000,
           ('my', 'tuple'): None, 'empty': []}
    delver = Delver(obj)
    delver.run()
