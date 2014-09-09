from eca import *
import eca.http

from pprint import pprint

# This function will be called to set up the HTTP server
def add_request_handlers(httpd):
    # add an event-generating request handler to fire 'order' events
    # This requires the POST method because the event generation handler only
    # understands POST requests.
    httpd.add_route('/api/order', eca.http.GenerateEvent('order'), methods=['POST'])

    # use the library content from the template_static dir instead of our own
    # this is a bit finicky, since execution now depends on a proper working directory.
    httpd.add_content('/lib/', 'template_static/lib')
    httpd.add_content('/style/', 'template_static/style')


@event('order')
def order(c, e):
    # we received an order...
    
    # ...go an print it
    print("Received a new order:")
    pprint(e.data)

    # ...and emit it to all interested browsers
    # (conceptually, this could also include the Barista's workstation)
    emit('orders',{
        'text': str(e.data)
    });


# Below are some examples of how to handle incoming requests based
# on observed qualities.

# Inform the coffee machine handler that more coffee is required.
@event('order')
@condition(lambda c,e: e.data['drink'] == 'Coffee')
def start_brewing(c,e):
    print("-> Start the coffee brewer!")


# Check for a very specific order
@event('order')
@condition(lambda c,e: e.data['drink'] == 'Tea'
                   and not e.data['additives']
                   and e.data['type'].lower() == 'earl grey'
                   and 'hot' in e.data['notes'].lower())
def picard_has_arrived(c,e):
    print("-> Captain Picard has arrived.")

