import threading
import time
from datetime import datetime
import json
from . import fire, get_context, context_switch, register_auxiliary, auxiliary
import logging
import sys


logger = logging.getLogger(__name__)

class EventGenerator:
    """
    An event generator uses a generation function to generate events from
    any external source.
    """
    def __init__(self, context, generator, event_name='tweet', **kwargs):
        self.context = context
        self.event_name = event_name
        self.generator = generator
        self.generator_args = kwargs
        self.stop_flag = threading.Event()

    def start(self):
        """
        Starts a thread to handle run this generator.
        """
        thread = threading.Thread(target=self.run)
        thread.start()

    def stop(self):
        """
        Requests shutdown of generator.
        """
        self.stop_flag.set()

    def run(self):
        """
        Invoke the generator to get a sequence of events.

        This method passes an event to the generator which will be set to True
        if the generator should terminate. Immediate termination is not required.
        """
        logger.debug("Running event generator")
        with context_switch(self.context):
            for event in self.generator(self.stop_flag, **self.generator_args):
                fire(self.event_name, event)

    
def offline_tweets(stop, data_file, time_factor=1000):
    """
    Offline tweet replay.

    Takes a datafile formatted with 1 tweet per line, and generates a sequence of
    scaled realtime items.
    """

    # timing functions return false if we need to abort
    def delayer(duration):
        logger.debug("Delay for next tweet {}s ({}s real)".format(delay, delay/time_factor))
        return not stop.wait(delay / time_factor)

    def immediate(duration):
        return not stop.is_set()

    # select timing function based on time_factor
    delayed = immediate if time_factor is None else delayer

    with open(data_file) as data:
        last_time = None
        lines = 0
        for line in data:
            lines += 1

            try:
                tweet = json.loads(line)
            except ValueError as e:
                logger.error("Could not read tweet on {}:{} (reason: {})".format(data_file,lines, e))
                continue

            # time scale the tweet
            tweet_time = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y')

            if not last_time:
                last_time = tweet_time
            
            wait = tweet_time - last_time 
            delay = wait.total_seconds()
   
            # delay and yield or break depending on success
            if delayed(delay):
                yield tweet
                last_time = tweet_time
            else:
                break

      
def start_offline_tweets(data_file, event_name='tweet', aux_name='tweeter', **kwargs):
    context = get_context()
    if context is None:
        raise NotImplementedError("Can not start offline tweet replay outside of a context.")
    register_auxiliary(aux_name, EventGenerator(context, generator=offline_tweets, data_file=data_file, event_name=event_name, **kwargs))
    auxiliary(aux_name).start()
