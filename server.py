"""
Server for viewing the DC Code locally

Requires python 3.3 or greater.

Run `python3 server.py`

Visit `localhost:8000` in your web browser.
"""

from http.server import SimpleHTTPRequestHandler, HTTPServer
import argparse
import sys, os
import urllib.parse
import posixpath
import json

DIR = os.path.abspath(os.path.dirname(__file__))

class RequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        redirect = self.server.redirects.get(self.path)
        if redirect:
            sa = self.server.socket.getsockname()
            location = 'http://{}:{}{}'.format(*sa, redirect)
            self.send_response(302)
            self.send_header('Location', location)
            self.end_headers()
        else:
            super().do_GET()

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        # replace colons (not allowed in win paths) with tilde
        path = path.replace(':', '~')
        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        # Don't forget explicit trailing slash when normalizing. Issue17324
        trailing_slash = path.rstrip().endswith('/')
        try:
            path = urllib.parse.unquote(path, errors='surrogatepass')
        except UnicodeDecodeError:
            path = urllib.parse.unquote(path)
        path = posixpath.normpath(path)
        words = path.split('/')
        words = filter(None, words)
        path = DIR
        for word in words:
            if os.path.dirname(word) or word in (os.curdir, os.pardir):
                # Ignore components that are not a simple file/directory name
                continue
            path = os.path.join(path, word)
        if trailing_slash:
            path += '/'
        return path

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--bind', '-b', default='127.0.0.1', metavar='ADDRESS',
                        help='Specify alternate bind address '
                             '[default: localhost]')
    parser.add_argument('port', action='store',
                        default=8000, type=int,
                        nargs='?',
                        help='Specify alternate port [default: 8000]')
    args = parser.parse_args()

    server_address = (args.bind, args.port)

    httpd = HTTPServer(server_address, RequestHandler)

    raw_redirects = []
    try:
        with open(os.path.join(DIR, 'redirects.json')) as f:
            raw_redirects = json.load(f)
    except:
        pass
    redirects = {r[0]: r[1] for r in raw_redirects}
    httpd.redirects = redirects

    sa = httpd.socket.getsockname()
    print("Serving HTTP on", sa[0], "port", sa[1], "...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, exiting.")
        httpd.server_close()
        sys.exit(0)
