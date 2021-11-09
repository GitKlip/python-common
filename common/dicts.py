

class Objectview:
    """ Takes a data on initialization and allows values to be accessed by attribute.

    A lighter weight and simpler (read-only) version of Munch.

    Example
        view = Objectview({'dog': 1, 'cat': 2})
        view.dog  # => 1
        view.cat # => 2
    """
    def __init__(self, data):
        self.__dict__ = data
