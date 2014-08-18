from eca import *

#static_content_path = 'static'

def add_request_handlers(httpd):
    httpd.add_handler('/hello/', eca.http.HelloWorld)
    httpd.add_handler('/wiki', eca.http.Redirect('http://www.wikipedia.net'))
    httpd.add_handler('/redir', eca.http.Redirect('/test/'))
    httpd.add_handler('/test', eca.sessions.GenerateEvent('request'), methods=['POST'])


@event('init')
def init(context, event):
    context.silent = False
    print("INIT")


@event('main')
@condition(lambda c, e: not c.silent)
def fizz_bang(context, event):
    print("Fizz Bang!")
    print("Printing an event now:" + str(event))
    new_event('ping', {'a': 10})


@event('ping')
def on_ping(context, event):
    print("Ping with " + str(event.a))


@event('request')
def on_request(contenxt, event):
    print("WOoot!" + str(event))
    emit('test',{
        'a':10
    })
