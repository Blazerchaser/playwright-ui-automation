"""A loopback-only, in-memory HTTP app for manual Network-tab practice."""

import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer


LOCAL_FORM_HTML = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Local user form</title>
  </head>
  <body>
    <h1>User form</h1>
    <p>Open DevTools → Network, fill the form, then click Submit.</p>
    <form>
      <label for="name">Name</label>
      <input id="name" name="name" required>
      <label for="email">Email</label>
      <input id="email" name="email" type="email" required>
      <button type="submit">Submit</button>
    </form>
    <p role="status" aria-live="polite"></p>
    <script>
      document.querySelector("form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const status = document.querySelector('[role="status"]');
        try {
          const response = await fetch("/users", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
              name: document.querySelector("#name").value,
              email: document.querySelector("#email").value
            })
          });
          if (!response.ok) throw new Error(`HTTP ${response.status}`);
          const user = await response.json();
          status.textContent = `Created user: ${user.name}`;
        } catch (error) {
          status.textContent = `Request failed: ${error.message}`;
        }
      });
    </script>
  </body>
</html>
"""


def create_server(port=8765):
    """Bind only to localhost; user records disappear when this server exits."""
    users = {}

    class DemoHandler(BaseHTTPRequestHandler):
        def _send(self, status, body, content_type="application/json"):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path == "/":
                self._send(200, LOCAL_FORM_HTML.encode("utf-8"), "text/html; charset=utf-8")
                return

            if self.path.startswith("/users/"):
                user = users.get(self.path.removeprefix("/users/"))
                if user is not None:
                    self._send(200, json.dumps(user).encode("utf-8"))
                    return

            self._send(404, b'{}')

        def do_POST(self):
            if self.path != "/users":
                self._send(404, b'{}')
                return

            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 65536:
                    raise ValueError("Invalid request length")
                data = json.loads(self.rfile.read(length))
                name, email = data["name"], data["email"]
                if not isinstance(name, str) or not isinstance(email, str):
                    raise ValueError("Invalid user fields")
            except (ValueError, KeyError, TypeError):
                self._send(400, b'{"error":"Invalid user"}')
                return

            user = {"id": len(users) + 1, "name": name, "email": email}
            users[str(user["id"])] = user
            self._send(201, json.dumps(user).encode("utf-8"))

    return HTTPServer(("127.0.0.1", port), DemoHandler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765, help="localhost port (default: 8765)")
    args = parser.parse_args()
    if not 0 <= args.port <= 65535:
        parser.error("--port must be between 0 and 65535")

    with create_server(args.port) as server:
        print(f"Open http://127.0.0.1:{server.server_port}/ in your own Chrome.", flush=True)
        print("Press Ctrl+C in this terminal to stop the demo.", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nDemo stopped.", flush=True)


if __name__ == "__main__":
    main()
