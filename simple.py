from eca import *
import eca.http

# configuration

static_content_path = 'static'

def add_request_handlers(httpd):
    httpd.add_route('/wiki', eca.http.Redirect('http://www.wikipedia.net'))
    httpd.add_route('/redir', eca.http.Redirect('/test/'))
    httpd.add_route('/test', eca.http.GenerateEvent('request'), methods=['POST'])


#rules 

@event('init')
def init(context, event):
    context.silent = False
    print("INIT")


@event('main')
@condition(lambda c, e: not c.silent)
def fizz_bang(context, event):
    print("Fizz Bang!")
    print("Printing an event now:" + str(event))
    fire('ping', {'a': 10})


@event('ping')
def on_ping(context, event):
    print("Ping with " + str(event.a))


@event('request')
def on_request(context, event):
    print("WOoot!" + str(event))
    emit('test',{
        'a':10
    })
