from . import http
import queue

class ServerSideEvents(http.Handler):
    def __init__(self, request):
        super().__init__(request)
        self.queue = queue.Queue()

    def send_event(self, target, event):
        self.queue.put(event)

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
            event_line = "event: {}\n".format(event.name)
            self.request.wfile.write(event_line.encode('utf-8'))

            data_line = "data: {}\n".format(event.json)
            self.request.wfile.write(data_line.encode('utf-8'))

            self.request.wfile.write("\n".encode('utf-8'))
            self.request.wfile.flush()

            return True
        except IOError:
            return False
        except:
            return False

