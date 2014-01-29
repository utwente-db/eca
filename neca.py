#!/usr/bin/env python3
import argparse
import threading
import importlib
import os.path
import logging

from eca import *

import eca.http
import http.cookies

logger = logging.getLogger(__name__)

def _hr_items(seq):
    return ', '.join("'{}'".format(e) for e in seq)

def log_level(level):
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise argparse.ArgumentTypeError("'{}' is not a valid logging level. Choose from {}".format(level, _hr_items(log_level.allowed)))
    return numeric_level

log_level.allowed = ['debug', 'info', 'warning','error','critical']

def main():
    parser = argparse.ArgumentParser(description='The Neca HTTP server.')
    parser.add_argument('-t', '--trace', default=False, action='store_true', help='Trace the execution of rules.')
    parser.add_argument('-l', '--log', default='warning', help="The log level to use. One of {} (defaults to '%(default)s')".format(_hr_items(log_level.allowed)), metavar='LEVEL', type=log_level)
    parser.add_argument('-m', '--module', default='simple', help="The rules module to load (defaults to '%(default)s')")
    args = parser.parse_args()

    # set logging level
    logging.basicConfig(level=args.log)

    if args.trace:
        logging.getLogger('trace').setLevel(logging.DEBUG)

    # load module, and determine static content path
    rules_module = importlib.import_module(args.module)

    rules_path = os.path.dirname(os.path.abspath(rules_module.__file__))
    static_path = os.path.join(rules_path, 'static')
    if hasattr(rules_module, 'static_content_path'):
        if os.path.isabs(rules_module.static_content_path):
            static_path = rules_module.static_content_path
        else:
            static_path = os.path.join(rules_path, rules_module.static_content_path)

    class HelloHandler(eca.http.Handler):
        def handle_GET(self):
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

    class FallbackHandler(eca.http.Handler):
        def handle_GET(self):
            self.handler.handle_GET()

        def handle_HEAD(self):
            self.handler.handle_HEAD()

    httpd = eca.http.HTTPServer(('',8000))
    httpd.static_path = static_path
    httpd.add_handler('GET,HEAD', '/', FallbackHandler)
    httpd.add_handler('*', '/test', HelloHandler)
    httpd.serve_forever()

#    import simple
#
#    context = Context()
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
