import json
import subprocess
from subprocess import PIPE
import http.server
import socketserver

PORT = 8099
DIRECTORY = "www/html"

class ReusableAddressTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def send_sse_events(self):
        print("hiii")
        # Set the headers necessary for SSE
        self.send_response(200)
        self.send_header("Content-type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

        with subprocess.Popen(['python', 'api.py'], stdout=PIPE, bufsize=1, text=True) as process:
            assert process.stdout
            for line in process.stdout:  # iterate over the output line by line
                self.wfile.write(line.encode())  # assuming wfile expects bytes
                self.wfile.flush()

        if process.returncode != 0:
            exit(1)

        self.wfile.flush() 

    def do_GET(self):
        if self.path == "/api":
            self.send_sse_events()  # Handle SSE endpoint
        else:
            super().do_GET()  # Handle regular file serving


with ReusableAddressTCPServer(("", PORT), Handler) as httpd:
    print(f"Serving on localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
