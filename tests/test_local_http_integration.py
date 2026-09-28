import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

import pytest
from playwright.sync_api import expect

from tests.pages.user_form_page import UserFormPage


LOCAL_FORM_HTML = """<!doctype html>
<html lang="en">
  <head><title>Local user form</title></head>
  <body>
    <h1>User form</h1>
    <form>
      <label for="name">Name</label>
      <input id="name" name="name">
      <label for="email">Email</label>
      <input id="email" name="email">
      <button type="submit">Submit</button>
    </form>
    <p role="status" aria-live="polite"></p>
    <script>
      document.querySelector("form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const response = await fetch("/users", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({
            name: document.querySelector("#name").value,
            email: document.querySelector("#email").value
          })
        });
        const user = await response.json();
        document.querySelector('[role="status"]').textContent = `Created user: ${user.name}`;
      });
    </script>
  </body>
</html>
"""


@pytest.fixture
def local_users_server():
    users = {}

    class FakeUsersHandler(BaseHTTPRequestHandler):
        def _send(self, status, body, content_type):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path == "/":
                self._send(200, LOCAL_FORM_HTML.encode("utf-8"), "text/html; charset=utf-8")
                return

            user = users.get(self.path.removeprefix("/users/"))
            if self.path.startswith("/users/") and user is not None:
                self._send(200, json.dumps(user).encode("utf-8"), "application/json")
                return

            self._send(404, b'{}', "application/json")

        def do_POST(self):
            if self.path != "/users":
                self._send(404, b'{}', "application/json")
                return

            length = int(self.headers["Content-Length"])
            data = json.loads(self.rfile.read(length))
            user = {"id": len(users) + 1, "name": data["name"], "email": data["email"]}
            users[str(user["id"])] = user
            self._send(201, json.dumps(user).encode("utf-8"), "application/json")

        def log_message(self, format, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), FakeUsersHandler)
    server_thread = Thread(target=server.serve_forever)
    server_thread.start()

    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        server_thread.join()


def test_create_user_through_local_http(page, local_users_server):
    user_form = UserFormPage(page)
    user_form.open_from_url(local_users_server)

    with page.expect_response(
        lambda response: response.url == f"{local_users_server}/users"
        and response.request.method == "POST"
    ) as post_response_info:
        user_form.submit(name="Egor", email="egor@example.com")

    post_response = post_response_info.value
    created_user = {"id": 1, "name": "Egor", "email": "egor@example.com"}

    expect(user_form.success_message).to_have_text("Created user: Egor")
    assert post_response.status == 201
    assert post_response.json() == created_user

    get_response = page.context.request.get(f"{local_users_server}/users/1")
    assert get_response.status == 200
    assert get_response.json() == created_user
