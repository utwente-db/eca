import http.server
import http.cookies
import socketserver

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

class HTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    def __init__(self, server_address, RequestHandlerClass):
        self.handlers = []
        super().__init__(server_address, RequestHandlerClass)

    def dispatch(self, method, path):
        matches = [m for m in self.handlers if m[0] == method and path.startswith(m[1])]
        if matches:
            return max(matches, key=len)[2]
        else:
            return None

class HTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    error_message_format = DEFAULT_ERROR_MESSAGE
    server_version = 'EcaHTTP/2'
    default_request_version = 'HTTP/1.1'

    def dispatch(self):
        """Dispath the request to a specialised handler if needed."""
        handler = super()
        method_name = "do_{}".format(self.command)

        handler_class = self.server.dispatch(self.command, self.path)
        if handler_class:
            handler = handler_class(self)

        if not hasattr(handler, method_name):
            self.send_error(501, "Unsupported method ({})".format(self.command))
            return

        method = getattr(handler, method_name)
        method()

    # Standard HTTP verbs bound to dispatch method
    def do_GET(self): self.dispatch()
    def do_POST(self): self.dispatch()
    def do_PUT(self): self.dispatch()
    def do_DELETE(self): self.dispatch()
    def do_HEAD(self): self.dispatch()
