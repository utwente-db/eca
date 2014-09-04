from eca import *

import random

@event('init')
def setup(ctx, e):
    ctx.count = 0
    fire('sample', {'previous': 0.0})

def clip(lower, value, upper):
    return max(lower, min(value, upper))

@event('sample')
def generate_sample(ctx, e):
    ctx.count += 1
    if ctx.count % 50 == 0:
        emit('debug', {'text': 'Log message #'+str(ctx.count)+'!'})

    # base sample on previous one
    sample = clip(-100, e.previous + random.uniform(+5.0, -5.0), 100)

    # emit to outside world
    emit('sample',{
        'action': 'add',
        'value': sample
    })

    # chain event
    fire('sample', {'previous': sample}, delay=0.05)

