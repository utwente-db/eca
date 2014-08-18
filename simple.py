from eca import *

#static_content_path = 'static'

@event('init')
def init(context, event):
    context.silent = False
    print("INIT")


@event('main')
@condition(lambda c, e: not c.silent)
def fizz_bang(context, event):
    print("Fizz Bang!")
    print("Printing an event now:" + str(event))
    new_event('ping', {'a': 10})


@event('ping')
def on_ping(context, event):
    print("Ping with " + str(event.a))
