import threading
import time
from datetime import datetime
import json
from . import fire, get_context, context_switch, register_auxiliary, auxiliary
import logging
import sys

logger = logging.getLogger(__name__)

class OfflineTweetGenerator:
    def __init__(self, context, data_file, time_factor=1000.0, event_name='tweet'):
        self.context = context
        self.data_file = data_file
        self.time_factor = time_factor
        self.event_name = event_name


    def start(self):
        thread = threading.Thread(target=self.run)
        thread.start()


    def run(self):
        logger.debug("Running tweet event generator")
        try:
            with context_switch(self.context), open(self.data_file) as data:
                for event in self.generate_events(data):
                    fire(self.event_name, event)
        except IOError as e:
            print(e, file=sys.stderr)
            logger.error("Is the tweet data downloaded?")

       
    def generate_events(self, data):
        last_time = None
        for line in data:
            tweet = json.loads(line)
            tweet_time = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y')
            if not last_time:
                logger.debug("Initialised last time at {}".format(tweet_time))
                last_time = tweet_time
            
            wait = tweet_time - last_time 
            delay = wait.total_seconds() / self.time_factor

            logger.debug("Delay for next tweet {}s".format(delay))
            time.sleep(delay)
            yield tweet

def start_offline_tweets(data_file, name='tweeter', **kwargs):
    context = get_context()
    if context is None:
        raise NotImplementedError("Can not start offline tweet replay outside of a context.")
    register_auxiliary(name, OfflineTweetGenerator(get_context(), data_file, **kwargs))
    auxiliary(name).start()
