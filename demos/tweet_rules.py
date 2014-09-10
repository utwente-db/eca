from eca import *
from eca.generators import start_offline_tweets

import datetime
import textwrap

@event('init')
def setup(ctx, e):
    # start the offline tweet stream
    start_offline_tweets('data/batatweets.txt', 'chirp', time_factor=10000)

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
    emit('tweet', output)
