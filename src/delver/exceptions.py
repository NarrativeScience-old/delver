"""General use exceptions for the delver"""


class ObjectHandlerInputValidationError(Exception):
    """Used when an object handler invalidates input"""

    def __init__(self, msg):
        self.msg = msg


class DelverInputError(Exception):
    """Used when an invalid argument is given to the delver"""

    def __init__(self, msg):
        self.msg = msg
