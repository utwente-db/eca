from eca import *
import datetime
import eca.http

# add message posting handler
def add_request_handlers(httpd):
    httpd.add_route('/api/message', eca.http.GenerateEvent('incoming'), methods=['POST'])

    # use the library content from the template_static dir instead of our own
    # this is a bit finicky, since execution now depends on a proper working directory.
    httpd.add_content('/lib/', 'template_static/lib')
    httpd.add_content('/style/', 'template_static/style')


# store name of context
@event('init')
def setup(ctx, e):
    ctx.name = e.data['name']


# emit incoming messages to the client
@event('message')
def on_message(ctx, e):
    name = e.data['name']
    text = e.data['text']
    time = e.data['time'].strftime('%Y-%m-%d %H:%M:%S')

    emit('message',{
        'text': "{} @{}: {}".format(name, time, text)
    })


# do a global fire for each message from the client
@event('incoming')
def on_incoming(ctx, e):
    fire_global('message', {
        'name': ctx.name,
        'text': e.data['text'],
        'time': datetime.datetime.now()
    })
