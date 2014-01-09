import queue
import util
import sys
import os.path

__all__ = [
    'event',
    'condition',
    'rules',
    'Context',
    'Event'
]


class Event:
    """Abstract event with a name and attributes."""
    def __init__(self, name, data=None):
        """Constructs an event.

        Attributes are optional.

        """
        self.name = name
        self.data = data or {}

    def __getattr__(self, name):
        return self.data[name]

    def __str__(self):
        data_strings = []
        for k,v in self.data.items():
            data_strings.append("{}={}".format(k,v))
        return "'{}' with {{{}}}".format(self.name, ', '.join(data_strings))


class Context:
    """ECA Execution context.

    Each context maintains both a variables namespace and an event queue. The
    context itself provides a run method to allow threaded execution.

    """
    def __init__(self, trace=False):
        self.event_queue = queue.Queue()
        self.scope = util.NamespaceDict()
        self.done = False
        self.trace = trace

    def receive_event(self, event):
        self.event_queue.put(event)

    def _trace(self, message):
        if self.trace:
            print("({})".format(message), file=sys.stderr)

    def run(self):
        while not self.done:
            try:
                # wait until we have an upcoming event
                # (but don't wait too long -- self.done could have been set to
                #  true while we were waiting for an event)
                event = self.event_queue.get(timeout=1.0)

                self._trace("Event: {}".format(event))

                # Determine candidate rules and execute matches:
                # 1) Only rules that match the event name as one of the events
                candidates = [r for r in rules if event.name in r.events]

                # 2) Only rules for which all conditions hold
                for r in candidates:
                    if [c(self.scope, event) for c in r.conditions].count(True) == len(r.conditions):
                        self._trace("Match: rule {}".format(describe_action(r)))
                        result = r(self.scope, event)

            except queue.Empty:
                # Timeout on waiting, loop to check condition
                pass


rules = set()


def describe_action(fn):
    parts = []
    parts.append(fn.__name__)

    parts.append(" ({}:{})".format(os.path.relpath(fn.__code__.co_filename), fn.__code__.co_firstlineno))
    
    return ''.join(parts)


def prepare_action(fn):
    """Prepares a function to be usable as an action.

    This function assigns an empty list of the 'conditions' attribute if it is
    not yet available. This function also registers the action with the action
    library.

    """
    fn.conditions = getattr(fn, 'conditions', [])
    fn.events = getattr(fn, 'events', set())
    rules.add(fn)


def condition(c):
    """Adds a condition callable to the action.

    The condition must be callable. The condition will receive a context and
    an event, and must return True or False.

    This function returns a decorator so we can pass an argument to the
    decorator itself. This is why we define a new function and return it
    without calling it.

    (See http://docs.python.org/3/glossary.html#term-decorator)

    """
    def condition_decorator(fn):
        prepare_action(fn)
        fn.conditions.append(c)
        return fn
    return condition_decorator


def event(eventname):
    """Attaches the action to an event.

    This is effectively the same as adding the 'event.name == eventname'
    condition. Adding multiple event names will prevent the rule from
    triggering.

    As condition, this function generates a decorator.

    """
    def event_decorator(fn):
        prepare_action(fn)
        fn.events.add(eventname)
        return fn
    return event_decorator
