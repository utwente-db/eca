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

    def dispatch(self):
        """Dispatch incoming requests."""
        # start out with using fallback handling
        self.handler = self

        # the method we will be looking for
        # (uses HTTP method name to build Python method name)
        method_name = "handle_{}".format(self.command)

        # let server determine specialised handler class, and instance it
        handler_class = self.server.get_handler(self.command, self.path)
        if handler_class:
            self.handler = handler_class(self)

        # check for necessary HTTP method
        if not hasattr(self.handler, method_name):
            self.send_error(501, "Unsupported method ({})".format(self.command))
            return

        # apply filters to request
        for filter_class in self.server.get_filters(self.command, self.path):
            filter = filter_class(self)
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
        # Don't forget explicit trailing slash when normalizing. Issue17324
        trailing_slash = path.rstrip().endswith('/')
        path = posixpath.normpath(urllib.parse.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        # server content from static_path, instead of os.getcwd()
        path = self.server.static_path
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
        return {
            'address': self.client_address,
            'location': self.path,
            'method': self.command
        }

    #overload logging methods
    def log_message(self, format, *args):
        message_format = "[{}, {} {}] {}".format(self.client_address[0], 
                                                 self.command, 
                                                 self.path, 
                                                 format%args)
        logger.debug(message_format, extra=self._log_data())

    def log_error(self, format, *args):
        message_format = "[{}, {} {}] {}".format(self.client_address[0], 
                                                 self.command, 
                                                 self.path, 
                                                 format%args)
        logger.warn(message_format, extra=self._log_data())

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
                   if (method in m.methods or '*' in m.methods) and path.startswith(m.path)]

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
                if (method in f.methods or '*' in f.methods) and path.startswith(f.path)]

    def _log_registration(self, kind, registration):
        message_format = "Adding HTTP request {} '{}.{}' for ({} {})"
        message = message_format.format(kind,
                                        registration.handler.__module__,
                                        registration.handler.__name__,
                                        registration.methods,
                                        registration.path)
        logger.debug(message)

    def add_handler(self, method, path, handler_class):
        methods = [m.strip() for m in method.upper().split(',')]
        reg = HandlerRegistration(methods, path, handler_class)
        self._log_registration('handler', reg)
        self.handlers.append(reg)

    def add_filter(self, method, path, filter_class):
        methods = [m.strip() for m in method.upper().split(',')]
        reg = HandlerRegistration(methods, path, filter_class)
        self._log_registration('filter', reg)
        self.filters.append(reg)

    def serve_forever(self):
        logger.info("Serving static content from: '{}'".format(self.static_path))
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


# Cookie filters

class Cookies(Filter):
    """Filter to read cookies from request."""
    def handle(self):
        # process available cookies
        cookies = http.cookies.SimpleCookie()
        if 'cookie' in self.request.headers:
            cookies.load(self.request.headers['cookie'])
        self.request.cookies = cookies

class EcaCookie(Filter):
    def handle(self):
        # determine new cookie
        cookies = http.cookies.SimpleCookie()
        #FIXME: context manager should cough up a cookie here
        cookies['eca-session'] = 'foobar'
        cookies['eca-session']['path'] = '/'

        # set new cookie
        for c in cookies.output(header='',sep='\n').split('\n'):
            self.request.send_header('set-cookie', c)


# Some basic handlers

class HelloWorld(Handler):
    """The mandatory Hello World example."""
    def handle_GET(self):
        self.request.send_response(200)
        self.request.send_header('content-type','text/html; charset=utf-8')
        self.request.end_headers()

        output = "<!DOCTYPE html><html><body><h1>Hello world!</h1><p><i>eca-session:</i> {}</p></body></html>"

        try:
            if not hasattr(self.request, 'cookies'): raise KeyError()
            cookie = self.request.cookies['eca-session'].value
        except KeyError:
            cookie = '<i>no cookie</i>';
        
        self.request.wfile.write(output.format(cookie).encode('utf-8'))

class StaticContent(Handler):
    """
    Explicit fallback handler.

    This can be used to configure complex sub-paths.
    """
    def handle_GET(self):
        self.request.handle_GET()

    def handle_HEAD(self):
        self.request.handle_HEAD()

def Redirect(realpath):
    """
    Factory for redirection handlers.
    """
    class RedirectHandler(Handler):
        def handle_GET(self):
            location = None

            # check for absolute paths
            if realpath.startswith("http://") or realpath.startswith('https://'):
                location = realpath
            else:
                host = self.request.server.server_address[0]
                if self.request.server.server_address[1] != 80:
                    host += ":{}".format(self.request.server.server_address[1])
    
                if 'host' in self.request.headers:
                    host = self.request.headers['host']
    
                location = "http://{}{}".format(host, realpath)

            self.request.send_response(302)
            self.request.send_header('content-type','text/html; charset=utf-8')
            self.request.send_header('location',location)
            self.request.end_headers()
            output = "<!DOCTYPE html><html><body><p>Redirect to <a href='{0}'>{0}</a></p></body></html>"
            self.request.wfile.write(output.format(location).encode('utf-8'))

    return RedirectHandler


