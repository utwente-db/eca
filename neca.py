#!/usr/bin/env python3
import argparse
import threading
import importlib
import os.path
import logging

from eca import *
import eca.httpd
import eca.http

# logging
logger = logging.getLogger(__name__)


def _hr_items(seq):
    """Creates a more readable comma-separated list of things."""
    return ', '.join("'{}'".format(e) for e in seq)


def log_level(level):
    """argparse type to allow log level to be set directly."""
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise argparse.ArgumentTypeError("'{}' is not a valid logging level. Choose from {}".format(level, _hr_items(log_level.allowed)))
    return numeric_level

# the following are allowed names for log levels
log_level.allowed = ['debug', 'info', 'warning','error','critical']


def main_server(args, rules_module):
    """
    HTTP server entry point.
    """
    # determine initial static content path 
    rules_path = os.path.dirname(os.path.abspath(rules_module.__file__))
    static_path = os.path.join(rules_path, 'static')

    # see if an override has been given (absolute or relative)
    if hasattr(rules_module, 'static_content_path'):
        if os.path.isabs(rules_module.static_content_path):
            static_path = rules_module.static_content_path
        else:
            static_path = os.path.join(rules_path, rules_module.static_content_path)

    # configure http server
    httpd = eca.httpd.HTTPServer((args.ip, args.port))
    # default static route
    httpd.add_content('/', static_path)
    # default events route
    httpd.add_route('/events', eca.http.EventStream)
    # default handlers for cookies and sessions
    httpd.add_filter('/', eca.http.Cookies)
    httpd.add_filter('/', eca.http.SessionManager('eca-session'))

    # invoke module specific configuration
    if hasattr(rules_module, 'add_request_handlers'):
        rules_module.add_request_handlers(httpd)
    
    # start serving
    httpd.serve_forever()

def main_engine(args, rules_module):
    """
    Rules engine only entry point.
    """
    # create context
    context = Context()
    context.start(daemon=False)

    with context_switch(context):
        logger.info("Starting module '{}'...".format(args.module))
        fire_event('main')


def main():
    """
    Main program entry point.
    """
    parser = argparse.ArgumentParser(description='The Neca HTTP server.')
    parser.set_defaults(entry_point=main_engine)
    parser.add_argument('module',
                        default='simple',
                        help="The rules module to load (defaults to %(default)s).",
                        nargs='?')
    parser.add_argument('-t', '--trace',
                        default=False,
                        action='store_true',
                        help='Trace the execution of rules.')
    parser.add_argument('-l', '--log',
                        default='warning',
                        help="The log level to use. One of {} (defaults to '%(default)s')".format(_hr_items(log_level.allowed)),
                        metavar='LEVEL',
                        type=log_level)
    parser.add_argument('-s','--server',
                        dest='entry_point',
                        action='store_const',
                        const=main_server,
                        help='Start HTTP server instead of directly executing the module.')
    parser.add_argument('-p', '--port',
                        default=8080,
                        help="The port to bind the HTTP server to (default to '%(default)s')",
                        type=int)
    parser.add_argument('-i', '--ip',
                        default='localhost',
                        help="The IP to bind the HTTP server to (defaults to '%(default)s'")
    args = parser.parse_args()

    # set logging level
    logging.basicConfig(level=args.log)

    # enable trace logger if requested
    if args.trace:
        logging.getLogger('trace').setLevel(logging.DEBUG)

    # load module, and determine static content path
    rules_module = importlib.import_module(args.module)

    args.entry_point(args, rules_module)

if __name__ == "__main__":
    main()
