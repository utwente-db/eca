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
    fire('sample', {'previous': 0.0})


# define a normal Python function
def clip(lower, value, upper):
    return max(lower, min(value, upper))

@event('sample')
def generate_sample(ctx, e):
    ctx.count += 1
    if ctx.count % 50 == 0:
        emit('debug', {'text': 'Log message #'+str(ctx.count)+'!'})
        emit('barsample', {'action': 'reset'})

    # base sample on previous one

    sample = random.uniform(+5.0, -5.0)

    li = int(random.uniform(+5.0,0))+1
    l = 'cat'+str(li)
    v = random.uniform(+10.0,0)

    # emit to outside world
    # emit('linesample',{
        # 'action': 'add',
	# 'series' : 'lineA',
        # 'value': [[ctx.count,random.uniform(+10.0,0)]]
    # })
    # emit('linesample',{
        # 'action': 'add',
	# 'series' : 'lineB',
        # 'value': [[ctx.count,random.uniform(+10.0,0)]]
    # })
    emit('barsample',{ 'action': 'set', 'series': 'serie'+str(int(random.uniform(1,4))), 'value': [l,v] })
    emit('wordsample',{
        'action': 'add',
        'value': [l,v]
    })
    # chain event
    fire('sample', {'previous': sample}, delay=0.05)

