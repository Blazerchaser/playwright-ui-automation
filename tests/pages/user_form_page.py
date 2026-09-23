USER_FORM_HTML = """
<h1 data-testid="form-title">User form</h1>
<form id="user-form">
  <label for="name">Name</label>
  <input id="name" name="name">

  <label for="email">Email</label>
  <input id="email" name="email">

  <button type="submit">Submit</button>
</form>
<p id="form-message"></p>

<script>
  document.querySelector("#user-form").addEventListener("submit", (event) => {
    event.preventDefault();

    const email = document.querySelector("#email").value;
    const message = document.querySelector("#form-message");

    if (!email.includes("@")) {
      message.setAttribute("role", "alert");
      message.textContent = "Enter a valid email address.";
      return;
    }

    message.setAttribute("role", "status");
    message.textContent = "Form submitted successfully.";
  });
</script>
"""


class UserFormPage:
    def __init__(self, page):
        self.page = page
        self.name_input = page.get_by_label("Name")
        self.email_input = page.get_by_label("Email")
        self.submit_button = page.get_by_role("button", name="Submit")
        self.success_message = page.get_by_role("status")
        self.error_message = page.get_by_role("alert")
        self.title = page.get_by_test_id("form-title")

    def open(self):
        self.page.set_content(USER_FORM_HTML)

    def submit(self, name, email):
        self.name_input.fill(name)
        self.email_input.fill(email)
        self.submit_button.click()
