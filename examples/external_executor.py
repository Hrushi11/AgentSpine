"""Reference external executor consuming AgentSpine execution signals."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length) or b"{}")
        print("received execution signal:", json.dumps(payload, indent=2))

        body = json.dumps({"ok": True, "processed_action_id": payload.get("action_id")}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8090), Handler).serve_forever()
