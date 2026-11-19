"""Liveness/readiness REST, sem expor mensagens, endereços ou tokens."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
import time


class Health:
    def __init__(self, service):
        self.service = service
        self.ready = False
        self.last_success = None
        self.max_age = None

    def success(self):
        self.ready = True
        self.last_success = time.time()

    def start(self, port):
        state = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path not in ("/health", "/ready"):
                    self.send_error(404)
                    return
                ready = state.ready and (state.max_age is None or state.last_success is not None and
                                         time.time() - state.last_success < state.max_age)
                status = 200 if self.path == "/health" or ready else 503
                data = json.dumps({"service": state.service, "ready": ready,
                                   "last_success": state.last_success}).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, *_):
                pass

        server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        return server
