from eca import *


@event('main')
def setup(ctx, e):
    """
    Initialise the context with an accumulator value, and inform
    the user about the fact that we process input.
    """
    print("Enter a number per line and end with EOF:")
    print("(EOF is ctrl+d under linux and MacOSes, ctrl+z followed by return under Windows)")
    ctx.accumulator = 0
    ctx.count = 0


@event('line')
def line(ctx, e):
    """
    Tries to parse the input line as a number and add it to the accumulator.
    """
    try:
        value = float(e.data) if '.' in e.data else int(e.data)
        ctx.accumulator += value
        ctx.count += 1
        print("sum = " + str(ctx.accumulator))
    except ValueError:
        print("'{}' is not a number.".format(e.data))


@event('end-of-input')
@condition(lambda c,e: c.count > 0)
def done(ctx, e):
    """
    Outputs the final average to the user.
    """
    print("{} samples with average of {}".format(ctx.count, ctx.accumulator / ctx.count))
    shutdown()


@event('end-of-input')
@condition(lambda c,e: c.count == 0)
def no_input(ctx, e):
    """
    Invoked of no input is given and input is finished.
    """
    print("0 samples. \"Does not compute!\"")
    shutdown()
