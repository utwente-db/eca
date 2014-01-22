#!/usr/bin/env python3
import argparse
import threading
import importlib
import os.path

from eca import *

import eca.http
import http.cookies


def main():
    parser = argparse.ArgumentParser(description='The Neca HTTP server.')
    parser.add_argument('-t', '--trace', default=False, action='store_true', help='Trace the execution of rules.')
    parser.add_argument('-m', '--module', default='simple', help='The rules module to load.')
    args = parser.parse_args()

    # load module, and determine static content path
    rules_module = importlib.import_module(args.module)

    rules_path = os.path.dirname(os.path.abspath(rules_module.__file__))
    static_path = os.path.join(rules_path, 'static')
    if hasattr(rules_module, 'static_content_path'):
        if os.path.isabs(rules_module.static_content_path):
            static_path = rules_module.static_content_path
        else:
            static_path = os.path.join(rules_path, rules_module.static_content_path)

    print("Serving static content from: '{}'".format(static_path))

    class HelloHandler:
        def __init__(self, handler):
            self.handler = handler

        def do_GET(self):
            info = None
            if 'cookie' in self.handler.headers:
                C = http.cookies.SimpleCookie()
                C.load(self.handler.headers['cookie'])
                info = C['eca-session'].value

            cookies = http.cookies.SimpleCookie()
            cookies['eca-session'] = 'foobar'
            cookies['eca-session']['path'] = '/'

            self.handler.send_response(200)
            for c in cookies.output(header='',sep='\n').split('\n'):
                self.handler.send_header('set-cookie', c)
            self.handler.send_header('content-type','text/html; charset=utf-8')
            self.handler.end_headers()

            self.handler.wfile.write("<!DOCTYPE html><html><body><h1>Hello world!</h1><p><i>eca-session:</i> {}</p></body></html>".format(info).encode('utf-8'))

    httpd = eca.http.HTTPServer(('',8000), eca.http.HTTPRequestHandler)
    httpd.handlers += [('GET','/test', HelloHandler)]
    httpd.static_path = static_path
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
