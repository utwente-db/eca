from eca import *
from eca.generators import start_offline_tweets
from eca.http import GenerateEvent

import datetime
import textwrap
import time
import pprint

def add_request_handlers(httpd):
    httpd.add_route('/api/poke', GenerateEvent('poke'), methods=['POST'])

@event('poke')
def setup(ctx, e):
    # start the offline tweet stream
    start_offline_tweets('data/test.txt', 'chirp', time_factor=None)

@event('chirp')
def tweet(ctx, e):
    # we receive a tweet
    tweet = e.data

    # parse date
    time = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y')

    # nicify text
    text = textwrap.fill(tweet['text'],initial_indent='    ', subsequent_indent='    ')

    # generate output
    output = "[{}] {} (@{}):\n{}".format(time, tweet['user']['name'], tweet['user']['screen_name'], text)
    # print(output)

    print('-----------------------')
    print()
    pprint.pprint(tweet['text'])
    print()
    pprint.pprint(tweet['entities'])
    print()

    emit('tweet', tweet)
