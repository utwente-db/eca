import collections
import threading
import eca


class PubSubChannel:
    """Publish/Subscribe channel used for distribution of events.

    The operations on this channel are thread-safe, but subscribers
    are executed by the publishing thread. Use a queue to decouple the
    publishing thread from the consuming thread.

    """

    def __init__(self):
        self.lock = threading.RLock()
        self.subscriptions = collections.defaultdict(list)

    def subscribe(self, target, event='message'):
        """Subscribe to an event.

        The optional event name can be used to subscribe selectively.

        """
        with self.lock:
            self.subscriptions[event].append(target)

    def unsubscribe(self, target, event='message'):
        """Unsubscribe from an event.

        The optional event name can be used to unsubscribe from another event.

        """
        with self.lock:
            self.subscriptions[event].remove(target)

    def publish(self, event='message', data=None):
        """Publishes an event.

        The event can be named and accompanied by optional data.

        """
        with self.lock:
            for target in self.subscriptions[event]:
                target(event, data)



class NamespaceError(KeyError):
    """Exception raised for errors in the NamespaceDict."""
    pass

class NamespaceDict(dict):
    """A dictionary that also allows access through attributes.

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
    """Generates a human readable reference to the given function."""
    parts = []
    parts.append(fn.__name__)

    parts.append(" ({}:{})".format(os.path.relpath(fn.__code__.co_filename), fn.__code__.co_firstlineno))
    
    return ''.join(parts)
