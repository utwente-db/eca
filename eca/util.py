import os.path


class NamespaceError(KeyError):
    """Exception raised for errors in the NamespaceDict."""
    pass


class NamespaceDict(dict):
    """
    A dictionary that also allows access through attributes.

    See http://docs.python.org/3.3/reference/datamodel.html#customizing-attribute-access
    """

    def __getattr__(self, name):
        if name not in self:
            raise NamespaceError(name)
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        del self[name]


def describe_function(fn):
    """
    Generates a human readable reference to the given function.
    
    This function is most useful when used on function defined in actual files.
    """
    parts = []
    parts.append(fn.__name__)

    parts.append(" ({}:{})".format(os.path.relpath(fn.__code__.co_filename), fn.__code__.co_firstlineno))

    return ''.join(parts)
