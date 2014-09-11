from eca import *

import random

## You might have to update the root path to point to the correct path
## (by default, it points to <rules>_static)
# root_content_path = 'template_static'


# binds the 'setup' function as the action for the 'init' event
# the action will be called with the context and the event
@event('init')
def setup(ctx, e):
    ctx.count = 0
    ctx.samples = {
        'sensor0': 0.0,
        'sensor1': 0.0
    }

    fire('sample', {
        'previous': 0.0,
        'name': 'sensor0',
        'failure-chance': 0.0,
        'reboot-chance': 1.0,
        'delay': 0.05
    })

    fire('sample', {
        'previous': 0.0,
        'name': 'sensor1',
        'failure-chance': 0.05,
        'reboot-chance': 0.1,
        'delay': 0.05
    })

    fire('sample', {
        'previous': None,
        'name': 'sensor2',
        'failure-chance': 0.2,
        'reboot-chance': 0.8,
        'delay': 0.1
    })

    fire('tick')


# define a normal Python function
def clip(lower, value, upper):
    return max(lower, min(value, upper))

@event('sample')
@condition(lambda c,e: e.get('previous') is not None)
def generate_sample(ctx, e):
    sample = e.get('previous')
    # failure chance off...
    if e.get('failure-chance') > random.random():
        sample = None
        del ctx.samples[e.get('name')]
    else:
        # base sample on previous one
        sample = clip(-100, e.get('previous') + random.uniform(+5.0, -5.0), 100)
        ctx.samples[e.get('name')] = sample

    # chain event
    data = dict(e.data)
    data.update({'previous': sample})
    fire('sample', data, delay=e.get('delay'))

@event('sample')
@condition(lambda c,e: e.get('previous') is None)
def try_reboot(ctx, e):
    sample = e.get('previous')
    if e.get('reboot-chance') > random.random():
        sample = random.uniform(100,-100)
        ctx.samples[e.get('name')] = sample

    data = dict(e.data)
    data.update({'previous': sample})
    fire('sample', data, delay=e.get('delay'))


@event('tick')
def tick(ctx, e):
    # emit to outside world
    emit('sample',{
        'action': 'add',
        'values': ctx.samples
    })
    fire('tick', delay=0.05);


