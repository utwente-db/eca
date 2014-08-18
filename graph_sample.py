from eca import *

import time
import random

root_content_path = 'graph-sample'

@event('init')
def setup(ctx, e):
    fire('sample', {'previous': 0.0})

def clip(lower, value, upper):
    return max(lower, min(value, upper))

@event('sample')
def generate_sample(ctx, e):
    # base sample on previous one
    sample = clip(-100, e.previous + random.uniform(+5.0, -5.0), 100)

    # emit to outside world
    emit('sample',{
        'value': sample
    })

    # this will halt the execution of other rules in this context
    time.sleep(0.05)

    # chain event
    fire('sample',{
        'previous': sample
    })
