import http.server
import http.cookies
import socketserver
import logging

import os.path
import posixpath
import urllib

from collections import namedtuple

# Logging
logger = logging.getLogger(__name__)

# Hard-coded default error message
DEFAULT_ERROR_MESSAGE = """\
<!DOCTYPE html>
<html>
<head>
<style type="text/css">
* { /* Reset the worst style breakers */
    padding: 0;
    margin: 0;
}

html { /* We always want at least this height */
    min-height: 100%%;
}

body#error {
    font-family: sans-serif;
    height: 100%%;
    background: #3378c6;
    background: -webkit-radial-gradient(center, ellipse cover, #3378c6 0%%,#23538a 100%%);
    background: radial-gradient(ellipse at center, #3378c6 0%%,#23538a 100%%);
    background-size: 100%% 100%%;
    background-repeat: no-repeat;
}

#error #message {
    position: absolute;
    width: 34em;
    height: 4em;

    top: 50%%;
    margin-top: -2em;
    left: 50%%;
    margin-left: -17em;

    text-align: center;
    color: #114;
    text-shadow: 0 1px 0 #88d;
}
</style>
<title>%(code)d - %(message)s</title>
</head>
<body id='error'>
<div id='message'>
<h1>%(message)s</h1>
<span>%(explain)s</span>
</div>
</body>
</html>
"""

class HTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """
    This request handler routes requests to a specialised handler.

    Handling a request is roughly done in two steps:
      1) Requests are first passed through matching registered filters
      2) Request is passed to the matching handler.

    Responsibility for selecting the handler is left to the server class.
    """
    error_message_format = DEFAULT_ERROR_MESSAGE
    server_version = 'EcaHTTP/2'
    default_request_version = 'HTTP/1.1'

    def send_header(self, key, value):
        """Buffer headers until they can be sent."""
        if not self.response_sent:
            if not hasattr(self, '_cached_headers'):
                self._cached_headers = []
            self._cached_headers.append((key,value))
        else:
            super().send_header(key, value)

    def send_response(self, *args, **kwargs):
        """Sends the necessary response, and appends buffered headers."""
        super().send_response(*args, **kwargs)
        self.response_sent = True
        if hasattr(self, '_cached_headers'):
            for h in self._cached_headers:
                self.send_header(*h)
            self._cached_headers = []

    def dispatch(self):
        """Dispatch incoming requests."""
        self.handler = None
        self.response_sent = False

        # the method we will be looking for
        # (uses HTTP method name to build Python method name)
        method_name = "handle_{}".format(self.command)

        # let server determine specialised handler factory, and call it
        handler_factory = self.server.get_handler(self.command, self.path)
        if not handler_factory:
            self.send_error(404)
            return

        # instantiate handler
        self.handler = handler_factory(self)

        # check for necessary HTTP method
        if not hasattr(self.handler, method_name):
            self.send_error(501, "Unsupported method ({})".format(self.command))
            return

        # apply filters to request
        # note: filters are applied in order of registration
        for filter_factory in self.server.get_filters(self.command, self.path):
            filter = filter_factory(self)
            if not hasattr(filter, method_name):
                self.send_error(501, "Unsupported method ({})".format(self.command))
                return
            filter_method = getattr(filter, method_name)
            filter_method()

        # select and invoke actual method
        method = getattr(self.handler, method_name)
        method()

    def translate_path(self, path):
        """
        Translate a /-separated PATH to the local filename syntax.

        This method is unelegantly 'borrowed' from SimpleHTTPServer.py to change
        the original so that it has the `path = self.server.static_path' line.
        """
        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = path[len(self.url_path):]
        # Don't forget explicit trailing slash when normalizing. Issue17324
        trailing_slash = path.rstrip().endswith('/')
        path = posixpath.normpath(urllib.parse.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        # server content from static_path, instead of os.getcwd()
        path = self.local_path
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        if trailing_slash:
            path += '/'
        return path

    # Standard HTTP verbs bound to dispatch method
    def do_GET(self): self.dispatch()
    def do_POST(self): self.dispatch()
    def do_PUT(self): self.dispatch()
    def do_DELETE(self): self.dispatch()
    def do_HEAD(self): self.dispatch()

    # Fallback handlers for static content
    # (These invoke the original SimpleHTTPRequestHandler behaviour)
    def handle_GET(self): super().do_GET()
    def handle_HEAD(self): super().do_HEAD()

    # handle logging
    def _log_data(self):
        path = getattr(self, 'path','<unknown path>')
        command = getattr(self, 'command', '<unknown command>')
        return {
            'address': self.client_address,
            'location': path,
            'method': command
        }

    def _get_message_format(self, format, args):
        log_data = self._log_data()
        message_format = "[{}, {} {}] {}".format(self.client_address[0], 
                                                 log_data['method'], 
                                                 log_data['location'], 
                                                 format%args)
        return message_format

    #overload logging methods
    def log_message(self, format, *args):
        logger.debug(self._get_message_format(format, args), extra=self._log_data())

    def log_error(self, format, *args):
        logger.warn(self._get_message_format(format, args), extra=self._log_data())

HandlerRegistration = namedtuple('HandlerRegistration',['methods','path','handler'])

class HTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """
    HTTP Server with path/method registration functionality to allow simple
    configuration of served content.
    """
    def __init__(self, server_address, RequestHandlerClass=HTTPRequestHandler):
        self.handlers = []
        self.filters = []
        super().__init__(server_address, RequestHandlerClass)

    def get_handler(self, method, path):
        """Selects the best matching handler."""
        # Select handlers for the given method, that match any path or a prefix of the given path
        matches = [m
                   for m
                   in self.handlers
                   if (not m.methods or method in m.methods) and path.startswith(m.path)]

        # if there are matches, we select the one with the longest matching prefix
        if matches:
            best = max(matches, key=lambda e: len(e.path))
            return best.handler
        else:
            return None

    def get_filters(self, method, path):
        """Selects all applicable filters."""
        # Select all filters that the given method, that match any path or a suffix of the given path
        return [f.handler
                for f
                in self.filters
                if (not f.methods or method in f.methods) and path.startswith(f.path)]

    def _log_registration(self, kind, registration):
        message_format = "Adding HTTP request {} {} for ({} {})"
        message = message_format.format(kind,
                                        registration.handler,
                                        registration.methods,
                                        registration.path)
        logger.info(message)

    def add_route(self, path, handler_factory, methods=["GET"]):
        """
        Adds a request handler to the server.

        The handler can be specialised in in or more request methods by
        providing a comma separated list of methods. Handlers are matched
        longest-matching-prefix with regards to paths.
        """
        reg = HandlerRegistration(methods, path, handler_factory)
        self._log_registration('handler', reg)
        self.handlers.append(reg)

    def add_content(self, path, local_path, methods=['GET','HEAD']):
        """
        Adds a StaticContent handler to the server.

        This method is shorthand for
        self.add_route(path, StaticContent(path, local_path), methods)
        """
        if not path.endswith('/'):
            logger.warn("Static content configured without trailing '/'. "+
                        "This is different from traditional behaviour.")
        logger.info("Serving static content for {} under '{}' from '{}'".format(methods,path,local_path))
        self.add_route(path, StaticContent(path, local_path), methods)

    def add_filter(self, path, filter_factory, methods=[]):
        """
        Adds a filter to the server.

        Like handlers, filters can be specialised on in or more request methods
        by providing a comma-separated list of methods. Filters are selected on
        match prefix with regards to paths.

        Filters are applied in order of registration.
        """
        reg = HandlerRegistration(methods, path, filter_factory)
        self._log_registration('filter', reg)
        self.filters.append(reg)

    def serve_forever(self):
        logger.info("Server is running...")
        super().serve_forever()


class Handler:
    """
    Handler base class.
    """
    def __init__(self, request):
        self.request = request


class Filter(Handler):
    """
    Filter base class that does nothing.
    """
    def handle_GET(self): self.handle()
    def handle_POST(self): self.handle()
    def handle_HEAD(self): self.handle()
    def handle(self):
        pass


# static content handler defined here, because of intrinsice coupling with
# request handler.
def StaticContent(url_path, local_path):
    class StaticContent(Handler):
        """
        Explicit fallback handler.
        """
        def set_paths(self):
            self.request.local_path = local_path
            self.request.url_path = url_path
            
        def handle_GET(self):
            self.set_paths()
            self.request.handle_GET()

        def handle_HEAD(self):
            self.set_paths()
            self.request.handle_HEAD()

    # return class so that it can be constructed
    return StaticContent

