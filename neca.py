#!/usr/bin/env python3
import argparse
import threading

from eca import *

import eca.http


def main():
    parser = argparse.ArgumentParser(description='The Neca HTTP server.')
    parser.add_argument('-t', '--trace', default=False, action='store_true', help='Trace the execution of rules.')
    args = parser.parse_args()

    class HelloHandler:
        def __init__(self, handler):
            self.handler = handler

        def do_POST(self):
            self.handler.send_response(200)
            self.handler.send_header('content-type','text/html; charset=utf-8')
            self.handler.end_headers()
            self.handler.wfile.write("<!DOCTYPE html><html><body><h1>Hello world!</h1></body></html>".encode('utf-8'))

    httpd = eca.http.HTTPServer(('',8000), eca.http.HTTPRequestHandler)
    httpd.handlers.append(('GET','/test', HelloHandler))
    httpd.serve_forever()

#    import simple
#
#    context = Context(trace=args.trace)
#
#    # run worker
#    thread = threading.Thread(target=context.run)
#    thread.start()
#
#    with context_switch(context):
#        new_event('init')
#        new_event('message', {'foo': 13, 'bar': 37})


if __name__ == "__main__":
    main()
