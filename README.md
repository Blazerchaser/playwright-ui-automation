# Playwright UI Tests

Minimal local-only UI tests for learning Playwright locators and auto-waiting.
Most pages use `page.set_content` or mocked requests. The HTTP integration
tests use a temporary fake server on `127.0.0.1`; no external website is contacted.

The default suite covers form locators and validation, mocked response states,
local HTTP create/read behavior and duplicate-email errors, and restoration of
fake authentication state. It also checks that the opt-in fault fixture is
deterministic. The separate RED/GREEN persistence exercise is excluded from
default collection. These checks do not establish deployed-backend behavior,
real authentication, or cross-browser compatibility.

## Install

Use Python 3.12, matching CI:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Direct dependencies are pinned to the versions verified locally on Python
3.12.14. This is not a full lock of transitive dependencies or browser versions.
CI installs the Chromium build supplied by the pinned Playwright version;
the already installed Chrome used locally can have a different version.
The pins have been checked against the installed environment; a clean
installation still needs verification in CI.

The tests first use an already installed Google Chrome through Playwright's
Chromium engine, so no browser download is required. If Chrome is unavailable,
they use Playwright's bundled Chromium when it is already installed. To install
that browser explicitly, run:

```powershell
.\.venv\Scripts\python.exe -m playwright install chromium
```

## Chrome DevTools MCP in Codex (Windows)

The project-local `.codex/config.toml` configures Chrome DevTools MCP for
Codex. It needs Node.js, `pnpm`, and Google Chrome installed and available on
this machine. Codex loads project configuration only for a trusted project;
after opening or trusting this repository, start a new Codex task so the MCP
tools can be discovered. No global Codex configuration or Python test
dependency is needed.

The server starts Chrome headlessly with a temporary isolated profile. Usage
statistics, CrUX performance data, and update checks are disabled. The
configuration does not connect to an existing Chrome session or personal
profile. `pnpm dlx` fetches the pinned MCP package into pnpm's cache on first
use; it does not add a dependency to this project. The first run may need
network access for that fetch.

For a quick check, ask a new Codex task in this trusted repository to use
Chrome DevTools MCP to inspect a page served only on
`http://127.0.0.1:<port>`. Keep inspection on local test pages; the MCP server
does not need access to external sites for these lessons.
In the new Codex task, use `/mcp` to check whether `chrome-devtools` is active.
If it is absent, confirm that this repository itself is trusted; checking
`codex mcp list` alone is not a check of the active tools in this task.

## Manual Network-tab practice in your own Chrome

From this repository, start the demo in a terminal and leave that terminal
running while you inspect the page:

```powershell
.\.venv\Scripts\python.exe local_demo_server.py --port 8765
```

Open `http://127.0.0.1:8765/` in your regular Chrome. Open DevTools (F12),
select **Network** and **Fetch/XHR**, then enter a name and an email address
and click **Submit**. Select `POST /users` to inspect the JSON request payload,
the `201` response, and the returned user ID. The page should show
`Created user: <name>`. Keep DevTools open and submit again to see another
request. Press **Ctrl+C** in the server terminal to stop it. If port 8765 is
busy, choose another with `--port` and use the URL printed by the server.

This toy app has one extra rule for the negative scenario: email addresses are
unique (ignoring letter case). Submit the same email again with a different
name. The second `POST /users` returns `409` and the page shows
`Email already exists.` rather than another success. In a new tab, check
`/users/1` to see the original record and `/users/2` to see `404`: the failed
request did not add a user. The integration test verifies this through a real
browser, local HTTP requests, and the page's error message. This is a learning
contract for the fake server, not a claim about a production backend.

### Fault-mode bug-report exercise

Run this separate, opt-in training server in another terminal. It leaves the
normal server and its data alone:

```powershell
.\.venv\Scripts\python.exe local_demo_server.py --port 8767 --simulate-no-save
```

Open `http://127.0.0.1:8767/` in your own Chrome. With DevTools → Network →
Fetch/XHR open, submit the form once using made-up details. Note the UI text,
the `POST /users` status, and its JSON response. In a new tab, request
`http://127.0.0.1:8767/users/1` and note the status and body. Compare what
these observations imply. The simulation applies to the first valid submit
only; stop it with **Ctrl+C** and restart the command to repeat the exercise.
This is an intentionally faulty local fixture, not a production incident.

Use this short bug-report template, filling it with what you observed:

```text
Title:
Expected:
Actual:
Steps to reproduce:
1. Start the local fault demo and open its URL.
2. Submit the form once with made-up data.
3. Request /users/1 in a new tab.
Evidence: UI message; POST /users status and response JSON; GET /users/1 status and body.
```

### Opt-in RED regression exercise

`tests/red_persistence_regression.py` expresses one product expectation from
the bug report: a `201` create response must be followed by a `200` GET for
the returned ID with the same name and email. Its one test body runs against
two server modes on separate random localhost ports. The file is deliberately
outside pytest's default `test_*.py` collection, so the ordinary suite and CI
stay green. Select one mode explicitly:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests\red_persistence_regression.py -k normal
.\.venv\Scripts\python.exe -m pytest -q tests\red_persistence_regression.py -k fault
```

The first command should be GREEN; the second should fail at the persistence
assertion. The existing `page` fixture saves
`test-results/test_post_201_persists_user[fault]/failure.png` and
`test-results/test_post_201_persists_user[fault]/trace.zip` for RED. Open the
trace with:

```powershell
.\.venv\Scripts\python.exe -m playwright show-trace 'test-results\test_post_201_persists_user[fault]\trace.zip'
```

This is different from the green test that confirms the fault fixture is
deterministic. Selecting normal mode only disables the *training simulation*;
it is not a fix for a production bug. Do not add the RED selection to default
CI while this intentional fault remains.

The server listens only on `127.0.0.1`; users are held only in memory and are
discarded on stop. Use made-up details, not real personal data. Pytest starts
the same app only for the duration of its integration test, so its temporary
URL is not suitable for this manual exercise. The Chrome DevTools MCP setting
above opens a separate isolated Chrome; it cannot see the Network tab of your
regular Chrome or Playwright's browser unless it performs the scenario itself.

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
  `POST /users`, and reads the stored user with `GET /users/1`. It also checks
  that a duplicate email returns `409`, shows an error, and does not create a
  second user. Its server is a temporary in-memory fake, so it does not prove
  a deployed backend works.
- `context.storage_state(...)` demonstrates restoring a fake localStorage token
  into a new BrowserContext for local UI tests. It does not perform a real login
  or validate a real token. Real storage-state files can contain sensitive data,
  so they must not be committed; this project writes its demo state only to
  pytest's temporary `tmp_path`.
