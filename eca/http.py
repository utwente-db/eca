import http.server
import http.cookies
import socketserver
import logging

import os.path
import posixpath
import urllib

logger = logging.getLogger(__name__)

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
    error_message_format = DEFAULT_ERROR_MESSAGE
    server_version = 'EcaHTTP/2'
    default_request_version = 'HTTP/1.1'

    def dispatch(self):
        """Dispath the request to a specialised handler if needed."""
        self.handler = self
        method_name = "handle_{}".format(self.command)

        handler_class = self.server.dispatch(self.command, self.path)
        if handler_class:
            self.handler = handler_class(self)

        if not hasattr(self.handler, method_name):
            self.send_error(501, "Unsupported method ({})".format(self.command))
            return

        for filter_class in self.server.get_filters(self.command, self.path):
            filter = filter_class(self)
            if not hasattr(filter, method_name):
                self.send_error(501, "Unsupported method ({})".format(self.command))
                return
            filter_method = getattr(filter, method_name)
            filter_method()

        method = getattr(self.handler, method_name)
        method()

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Replace path translation with static web root.
        """
        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        # Don't forget explicit trailing slash when normalizing. Issue17324
        trailing_slash = path.rstrip().endswith('/')
        path = posixpath.normpath(urllib.parse.unquote(path))
        words = path.split('/')
        words = filter(None, words)
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

    # fallback handlers for static content
    def handle_GET(self): super().do_GET()
    def handle_HEAD(self): super().do_HEAD()

    # handle logging
    def _log_data(self):
        return {'address': self.client_address, 'location': self.path, 'method': self.command}
    def log_message(self, format, *args):
        logger.debug("[{}, {} {}] {}".format(self.client_address[0], self.command, self.path, format%args), extra=self._log_data())
    def log_error(self, format, *args):
        logger.warn("[{}, {} {}] {}".format(self.client_address[0], self.command, self.path, format%args), extra=self._log_data())


class HTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    def __init__(self, server_address, RequestHandlerClass=HTTPRequestHandler):
        self.handlers = []
        self.filters = []
        super().__init__(server_address, RequestHandlerClass)

    def dispatch(self, method, path):
        matches = [m for m in self.handlers if (method in m[0] or '*' in m[0]) and path.startswith(m[1])]
        if matches:
            return max(matches, key=lambda e: len(e[1]))[2]
        else:
            return None

    def get_filters(self, method, path):
        matches = [f[2] for f in self.filters if (method in f[0] or '*' in f[0]) and path.startswith(f[1])]
        return matches

    def add_handler(self, method, path, handler_class):
        methods = [m.strip() for m in method.upper().split(',')]
        logger.debug("Adding HTTP request handler '{}.{}' for ({} {})".format(handler_class.__module__, handler_class.__name__, methods, path))
        self.handlers.append((methods, path, handler_class))

    def add_filter(self, method, path, filter_class):
        methods = [m.strip() for m in method.upper().split(',')]
        logger.debug("Adding HTTP request filter '{}.{}' for ({} {})".format(filter_class.__module__, filter_class.__name__, methods, path))
        self.filters.append((methods, path, filter_class))

    def serve_forever(self):
        logger.info("Serving static content from: '{}'".format(self.static_path))
        super().serve_forever()


class Handler:
    def __init__(self, request):
        self.request = request


class Filter(Handler):
    pass


# Basic cookie filter
class CookieFilter(Filter):
    def handle_GET(self): self.handle()
    def handle_POST(self): self.handle()
    def handle_HEAD(self): self.handle()
    def handle(self):
        info = None
        if 'cookie' in self.request.headers:
            C = http.cookies.SimpleCookie()
            C.load(self.request.headers['cookie'])
            info = C['eca-session'].value
        self.request.cookie_info = info

        cookies = http.cookies.SimpleCookie()
        #FIXME: context manager should cough up a cookie here
        cookies['eca-session'] = 'foobar'
        cookies['eca-session']['path'] = '/'

        for c in cookies.output(header='',sep='\n').split('\n'):
            self.request.send_header('set-cookie', c)


# Some basic handlers

class HelloWorld(Handler):
    def handle_GET(self):
        self.request.send_response(200)
        self.request.send_header('content-type','text/html; charset=utf-8')
        self.request.end_headers()

        self.request.wfile.write("<!DOCTYPE html><html><body><h1>Hello world!</h1><p><i>eca-session:</i> {}</p></body></html>".format(self.request.cookie_info).encode('utf-8'))

class StaticContent(Handler):
    def handle_GET(self):
        self.request.handle_GET()

    def handle_HEAD(self):
        self.request.handle_HEAD()

def Redirect(realpath):
    class RedirectHandler(Handler):
        def handle_GET(self):
            location = None
    
            if realpath.startswith("http:"):
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
            self.request.wfile.write("<!DOCTYPE html><html><body><p>Redirect to <a href='{0}'>{0}</a></p></body></html>".format(location).encode('utf-8'))

    return RedirectHandler


