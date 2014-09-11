import queue
import collections
import threading
import logging
import sys
import json

from contextlib import contextmanager
from . import util
from . import pubsub

logger = logging.getLogger(__name__)

# all exported names
__all__ = [
    'event',
    'condition',
    'rules',
    'Rules',
    'Context',
    'Event',
    'fire',
    'fire_global',
    'emit',
    'get_context',
    'spawn_context',
    'context_activate',
    'context_switch',
    'auxiliary',
    'register_auxiliary',
    'shutdown'
]

# The global event channel
global_channel = pubsub.PubSubChannel()

# The thread local storage used to create a 'current context' with regards
# to the executing thread.
# (See https://docs.python.org/3/library/threading.html#thread-local-data)
thread_local = threading.local()


class Rules:
    def __init__(self):
        self.rules = set()

    def prepare_action(self, fn):
        """
        Prepares a function to be usable as an action.
    
        This function assigns an empty list of the 'conditions' attribute if it is
        not yet available. This function also registers the action with the action
        library.
        """
        if not hasattr(fn, 'conditions'):
            logger.info("Defined action '{}'".format(fn.__name__))
        fn.conditions = getattr(fn, 'conditions', [])
        fn.events = getattr(fn, 'events', set())
        self.rules.add(fn)
    
    
    def condition(self, c):
        """
        Adds a condition callable to the action.
    
        The condition must be callable. The condition will receive a context and
        an event, and must return True or False.
    
        This function returns a decorator so we can pass an argument to the
        decorator itself. This is why we define a new function and return it
        without calling it.
    
        (See http://docs.python.org/3/glossary.html#term-decorator)
    
        """
        def condition_decorator(fn):
            self.prepare_action(fn)
            logger.debug("With condition: {}".format(util.describe_function(c)))
            fn.conditions.append(c)
            return fn
        return condition_decorator
    
    
    def event(self, eventname):
        """
        Attaches the action to an event.
    
        This is effectively the same as adding the 'event.name == eventname'
        condition. Adding multiple event names will prevent the rule from
        triggering.
    
        As condition, this function generates a decorator.
        """
        def event_decorator(fn):
            self.prepare_action(fn)
            logger.debug("Attached to event: {}".format(eventname))
            fn.events.add(eventname)
            return fn
        return event_decorator


# The 'global' rules set
rules = Rules()

event = rules.event
condition = rules.condition

class Event:
    """Abstract event with a name and attributes."""
    def __init__(self, name, data=None):
        """Constructs an event.

        Attributes are optional.

        """
        self.name = name
        self.data = data

    def get(self, *args, **kwargs):
        return self.data.get(*args, **kwargs)

    def __str__(self):
        data_strings = []
        if isinstance(self.data, collections.Mapping):
            for k, v in self.data.items():
                data_strings.append("{}={}".format(k, v))
        else:
            data_strings.append(str(self.data))
        return "'{}' with {{{}}}".format(self.name, ', '.join(data_strings))


class Context:
    """
    ECA Execution context to track scope and events.

    Each context maintains both a variables namespace and an event queue. The
    context itself provides a run method to allow threaded execution through
    starting a new thread targetted at the run method.

    Every context also contains a dictionary of auxiliaries which contains
    objects to support the context and its rule execution.
    """
    def __init__(self, init_data=None, name='<unnamed context>', rules=rules):
        self.event_queue = queue.Queue()
        self.scope = util.NamespaceDict()
        self.channel = pubsub.PubSubChannel()
        self.auxiliaries = {}
        self.name = name
        self.done = False
        self.daemon = True
        self.rules = rules

        # subscribe to own pubsub channel to receive events
        self.channel.subscribe(self._pubsub_receiver, 'event')
        self.receive_event(Event('init', init_data))

        # subscribe to global pubsub channel to receive global eca events
        global_channel.subscribe(self._pubsub_receiver, 'event')

    def _trace(self, message):
        """Prints tracing statements if trace is enabled."""
        logging.getLogger('trace').info(message)

    def _pubsub_receiver(self, name, data):
        """Pubsub channel connector."""
        self.receive_event(data)

    def receive_event(self, event):
        """Receives an Event to handle."""
        self._trace("Received event: {}".format(event))
        self.event_queue.put(event)

    def auxiliary(self, name):
        return self.auxiliaries[name]

    def run(self):
        """Main event loop."""
        # switch context to this one and start working
        with context_switch(self):
            while not self.done:
                self._handle_event()

    def start(self, daemon=True):
        thread = threading.Thread(target=self.run)
        self.daemon = daemon
        thread.daemon = self.daemon
        thread.start()

    def stop(self):
        global_channel.unsubscribe(self._pubsub_receiver, 'event')
        if not self.daemon:
            self.done = True
        else:
            logger.warning("Can't shutdown daemon context. The context is used in a server.")

    def _handle_event(self):
        """Handles a single event, or times out after receiving nothing."""
        try:
            # wait until we have an upcoming event
            # (but don't wait too long -- self.done could have been set to
            #  true while we were waiting for an event)
            event = self.event_queue.get(timeout=1.0)

            self._trace("Working on event: {}".format(event))

            # Determine candidate rules and execute matches:
            # 1) Only rules that match the event name as one of the events
            candidates = [r for r in self.rules.rules if event.name in r.events]

            # 2) Only rules for which all conditions hold
            for r in candidates:
                if not [c(self.scope, event) for c in r.conditions].count(False):
                    self._trace("Rule: {}".format(util.describe_function(r)))
                    result = r(self.scope, event)

        except queue.Empty:
            # Timeout on waiting
            pass


@contextmanager
def context_switch(context):
    """
    Context manager to allow ad-hoc context switches. (The Python 'context' is
    different from the eca Context.)

    This function can be written without any regard for locking as the
    thread_local object will take care of that. Since everything here is done
    in the same thread, this effectively allows nesting of context switches.
    """
    # activate new context and store old
    old_context = context_activate(context)

    yield

    # restore old context
    context_activate(old_context)


def context_activate(context):
    """
    Activate an eca Context. If None is passed, this function should
    disable the context.
    """
    # stash old context
    old_context = getattr(thread_local, 'context', None)

    # switch to new context
    thread_local.context = context

    return old_context


def get_context():
    """Returns the current context."""
    return getattr(thread_local, 'context', None)


def auxiliary(name):
    """
    Returns an auxiliary for this context.
    """
    context = get_context()
    if context is None:
        raise NotImplementedError("Can not get an auxiliary without a current context.")
    return context.auxiliaries[name]


def register_auxiliary(name, aux):
    """
    Registers an auxiliary object for this context.
    """
    context = get_context()
    if context is None:
        raise NotImplementedError("Can not get an auxiliary without a current context.")
    context.auxiliaries[name] = aux


def shutdown():
    context = get_context()
    if context is None:
        raise NotImplementedError("Can not invoke shutdown without a current context.")
    context.stop()

def fire(eventname, data=None, delay=None):
    """
    Fires an event.

    This is the fire-and-forget method to create new events.
    """
    e = Event(eventname, data)
    context = get_context()
    if context is None:
        raise NotImplementedError("Can't invoke fire without a current context.")
    context.channel.publish('event', e, delay)


def fire_global(eventname, data=None, delay=None):
    """
    Fires a global event.
    """
    e = Event(eventname, data)
    global_channel.publish('event', e, delay)


def emit(name, data, id=None):
    """
    Emits an event to whomever is listening (mostly HTTP clients).
    """
    e = Event(name, {
        'json': json.dumps(data),
        'id': id
    })

    context = get_context()
    if context is None:
        raise NotImplementedError("Can't invoke emit without a current context.")
    context.channel.publish('emit', e)


def spawn_context(init_data=None, name='<unnamed context>', rules=rules, daemon=False):
    """
    Spawns a new context and starts it.
    """
    context = Context(init_data, name, rules)
    context.start(daemon)
