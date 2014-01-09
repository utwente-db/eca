from eca import *


@event('init')
def init(context, event):
    context.silent = False


@event('message')
@condition(lambda c, e: not c.silent)
def fizz_bang(context, event):
    print("Fizz Bang!")
    print(event)
    new_event('ping', {'a': 10})


@event('ping')
def on_ping(context, event):
    print("Ping with " + str(event.a))
