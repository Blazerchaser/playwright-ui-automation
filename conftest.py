from pathlib import Path

import pytest
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        item.rep_call = report


@pytest.fixture
def page(request):
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(channel="chrome")
        except PlaywrightError:
            browser = playwright.chromium.launch()

        context = browser.new_context()
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        page = context.new_page()

        yield page

        report = getattr(request.node, "rep_call", None)

        if report is not None and report.failed:
            artifact_dir = Path("test-results") / request.node.name
            artifact_dir.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=artifact_dir / "failure.png", full_page=True)
            context.tracing.stop(path=artifact_dir / "trace.zip")
        else:
            context.tracing.stop()

        context.close()
        browser.close()
