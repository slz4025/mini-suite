# Errors that arise due to general bad user input/action.
class UserError(Exception):
    pass


class InputError(Exception):
    pass


class OutOfBoundsError(Exception):
    pass


class NotSupportedError(Exception):
    pass


class UnknownOptionError(Exception):
    pass


class DoesNotExistError(Exception):
    pass
