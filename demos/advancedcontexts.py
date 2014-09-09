from eca import *
import random

# declare two separate rule sets

consumer = Rules()
producer = Rules()


# default init

@event('init')
def bootstrap(c, e):
    # start a few contexts for the generation of stock quotes
    # (The simple workload here can easily be done in a single context, but we
    # do this in separate contexts to give an example of the feature.)
    spawn_context({'symbol':'GOOG', 'start':500.0, 'delay':1.2}, rules=producer, daemon=True)
    spawn_context({'symbol':'AAPL', 'start':99.0, 'delay':0.9}, rules=producer, daemon=True)
    spawn_context(rules=consumer, daemon=True)

@event('end-of-input')
def done(c,e):
    # terminate if the input is closed
    shutdown()


# producer rules 

@producer.event('init')
def start_work(c, e):
    c.symbol = e.data['symbol']
    c.delay = e.data['delay']

    fire('sample', {
        'previous': e.data['start']
    })

@producer.event('sample')
def work(c, e):
    current = e.data['previous'] + random.uniform(-0.5, 0.5)

    fire_global('quote', {
        'symbol': c.symbol, 
        'value': current
    })

    fire('sample', {
        'previous': current
    }, delay=c.delay)


# consumer rules

@consumer.event('quote')
def show_quote(c, e):
    print("Quote for {symbol}: {value}".format(**e.data))
