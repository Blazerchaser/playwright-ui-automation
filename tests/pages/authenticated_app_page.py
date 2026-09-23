APP_URL = "https://ui.test/"

AUTHENTICATED_APP_HTML = """
<h1>Local authenticated app</h1>
<main id="app"></main>

<script>
  const app = document.querySelector("#app");
  const token = localStorage.getItem("auth_token");

  if (token) {
    app.innerHTML = '<p role="status">Welcome, Egor</p>';
  } else {
    app.innerHTML = '<p role="alert">Please sign in.</p>';
  }
</script>
"""


class AuthenticatedAppPage:
    def __init__(self, page):
        self.page = page
        self.welcome_message = page.get_by_role("status")
        self.sign_in_message = page.get_by_role("alert")

    def open(self):
        self.page.goto(APP_URL)
