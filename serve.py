import http.server
import socketserver

PORT = 8099
DIRECTORY = "www/html"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving on localhost:{PORT}")
    httpd.serve_forever()
