PROFILE_HTML = """
<h1>Profile</h1>
<button type="button">Load profile</button>
<p id="profile-message"></p>

<script>
  document.querySelector("button").addEventListener("click", async () => {
    const message = document.querySelector("#profile-message");
    const response = await fetch("https://ui.test/api/profile");

    if (!response.ok) {
      message.setAttribute("role", "alert");
      message.textContent = "Could not load profile.";
      return;
    }

    const profile = await response.json();
    message.setAttribute("role", "status");
    message.textContent = `Profile loaded: ${profile.name}`;
  });
</script>
"""


class ProfilePage:
    def __init__(self, page):
        self.page = page
        self.load_profile_button = page.get_by_role("button", name="Load profile")
        self.success_message = page.get_by_role("status")
        self.error_message = page.get_by_role("alert")

    def open(self):
        self.page.set_content(PROFILE_HTML)

    def load_profile(self):
        self.load_profile_button.click()
