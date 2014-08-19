import collections
import threading


class PubSubChannel:
    """
    Publish/Subscribe channel used for distribution of events.

    The operations on this channel are thread-safe, but subscribers
    are executed by the publishing thread. Use a queue to decouple the
    publishing thread from the consuming thread.
    """

    def __init__(self):
        self.lock = threading.RLock()
        self.subscriptions = collections.defaultdict(list)

    def subscribe(self, target, event='message'):
        """
        Subscribe to an event.

        The optional event name can be used to subscribe selectively.
        """
        with self.lock:
            self.subscriptions[event].append(target)

    def unsubscribe(self, target, event='message'):
        """
        Unsubscribe from an event.

        The optional event name can be used to unsubscribe from another event.
        """
        with self.lock:
            self.subscriptions[event].remove(target)

    def publish(self, event='message', data=None, delay=None):
        """
        Publishes an event.

        The event can be accompanied by optional data. A delay can be set to
        delay the publish action by the given amount of seconds.
        """
        if delay is None:
            with self.lock:
                for target in self.subscriptions[event]:
                    target(event, data)
        else:
            def task():
                self.publish(event, data)
            threading.Timer(delay, task).start()
