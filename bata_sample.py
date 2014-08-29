import threading
import urllib.request
import json
from eca import *

import random

root_content_path = 'bata-sample'

@event('init')
def setup(ctx, e):
    ctx.count = 0
    # fire('batatweet', {'previous': 0.0})
    try:
        t = threading.Thread(target=generate_batatweets, args=(get_context(),))
        t.start()
    except:
        print("Error: unable to start generate_batatweets thread")


def clip(lower, value, upper):
    return max(lower, min(value, upper))

@event('batatweet')
def generate_batatweet(ctx, e):
    ctx.count += 1
    if ctx.count % 50 == 0:
        emit('debug', {'text': 'Log message #'+str(ctx.count)+'!'})

    # base batatweet on previous one
    graphvalue = clip(-100, e.previous + random.uniform(+5.0, -5.0), 100)

    # emit to outside world
    emit('sample',{
        'action': 'add',
        'value': graphvalue
    })

    # chain event
    fire('batatweet', {'previous': graphvalue}, delay=0.05)

def json2objects(data):
        try:
                return json.loads(data)
        except Exception as e:
                print("WARNING: no json: "+str(e))
                return None

# Define a function for the thread
def generate_batatweets(ctx):
    print(str(ctx))
    # fire('batatweet', {'previous': 0.0})
    ctx.channel.publish('batatweet', {'previous': 0.0}, None)
    link = "http://library.ewi.utwente.nl/ecadata/batatweets.txt"
    req = urllib.request.Request(link)
    response = urllib.request.urlopen(req)
    page_str = response.read().decode("utf-8")
    for line in page_str.split("\n"):
        jo = json2objects(line)
        try:
            # print(jo['text'])
            a = 1
        except:
            print("IGNORE:"+line)


