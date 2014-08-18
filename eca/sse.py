import queue
from collections import namedtuple

from . import httpd

PendingEvent = namedtuple('PendingEvent', ['data', 'name', 'id'])

class ServerSideEvents(httpd.Handler):
    """
    Base class for server side events. See the specification of the W3C
    at http://dev.w3.org/html5/eventsource/
    
    This class handles decoupling through the default Queue. Events can be
    posted for transmission by using send_event.
    """

    def __init__(self, request):
        super().__init__(request)
        self.queue = queue.Queue()

    def send_event(self, data, name=None, id=None):
        self.queue.put(PendingEvent(data, name, id))

    def go_subscribe(self):
        pass

    def go_unsubscribe(self):
        pass

    def handle_GET(self):
        self.go_subscribe()

        # Send HTTP headers:
        self.request.send_response(200)
        self.request.send_header("Content-type", "text/event-stream")
        self.request.end_headers()

        done = False
        while not done:
            event = self.queue.get()
            if event == None:
                done = True
            else:
                done = not self._send_message(event)

        self.go_unsubscribe()

    def _send_message(self, event):
        try:
            if event.id is not None:
                id_line = "id: {}\n".format(event.id)
                self.request.wfile.write(id_line.encode('utf-8'))

            if event.name is not None:
                event_line = "event: {}\n".format(event.name)
                self.request.wfile.write(event_line.encode('utf-8'))

            data_line = "data: {}\n".format(event.data)
            self.request.wfile.write(data_line.encode('utf-8'))

            self.request.wfile.write("\n".encode('utf-8'))
            self.request.wfile.flush()

            return True
        except IOError:
            return False

