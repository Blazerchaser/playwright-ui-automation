# Playwright UI Tests

Minimal local-only UI tests for learning Playwright locators and auto-waiting.
Most pages use `page.set_content` or mocked requests. One integration test uses
a temporary fake HTTP server on `127.0.0.1`; no external website is contacted.

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

The tests first use an already installed Google Chrome through Playwright's
Chromium engine, so no browser download is required. If Chrome is unavailable,
they use Playwright's bundled Chromium when it is already installed. To install
that browser explicitly, run:

```powershell
.\.venv\Scripts\python.exe -m playwright install chromium
```

## Run the tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Continuous integration

`.github/workflows/playwright.yml` runs on `push` and `pull_request` with
read-only repository contents permission. The Linux job sets up Python 3.12,
installs `requirements.txt`, installs Playwright Chromium, and runs
`python -m pytest -q`.

If the test step fails, GitHub Actions uploads `test-results/` with the saved
screenshot and trace. If the directory has no files, that upload does not fail
the job.

## Debug artifacts after a failure

For a failed test, the fixture saves a full-page screenshot and a Playwright trace:

```text
test-results/<test-name>/failure.png
test-results/<test-name>/trace.zip
```

Successful tests do not write these files. Open a saved trace with:

```powershell
.\.venv\Scripts\python.exe -m playwright show-trace test-results\<test-name>\trace.zip
```

## What the tests demonstrate

- `UserFormPage` keeps form locators and UI actions together; tests retain the
  business intent and assertions.
- `get_by_label` fills the form fields and `get_by_role` clicks the Submit button.
- `expect(...).to_have_text(...)` waits for the success or error UI state without
  `time.sleep`.
- `get_by_test_id` is used once as a fallback locator for the specially marked form title.
- `page.route(...).fulfill(...)` lets profile tests verify success and error UI
  states from predictable mocked responses without a real network request.
- These network mocks do not prove that a real backend is available, that its
  response contract is correct, or that authentication works.
- The localhost integration test loads a page over HTTP, sends a real browser
  `POST /users`, and reads the stored user with `GET /users/1`. Its server is a
  temporary in-memory fake, so it does not prove a deployed backend works.
- `context.storage_state(...)` demonstrates restoring a fake localStorage token
  into a new BrowserContext for local UI tests. It does not perform a real login
  or validate a real token. Real storage-state files can contain sensitive data,
  so they must not be committed; this project writes its demo state only to
  pytest's temporary `tmp_path`.
