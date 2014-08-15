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
    parser.add_argument('-p', '--port', default=8080, help="The port to bind the HTTP server to (default to '%(default)s')", type=int)
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


    httpd = eca.http.HTTPServer(('', args.port))
    httpd.static_path = static_path
    httpd.add_handler('GET,HEAD', '/', eca.http.StaticContent)
    httpd.add_handler('*', '/test/', eca.http.HelloWorld)
    httpd.add_handler('*', '/wiki', eca.http.Redirect('http://www.wikipedia.net'))
    httpd.add_handler('*', '/redir', eca.http.Redirect('/test/'))
    httpd.add_filter('*', '/', eca.http.CookieFilter)
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
