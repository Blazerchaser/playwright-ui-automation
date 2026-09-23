from playwright.sync_api import expect

from tests.pages.authenticated_app_page import (
    APP_URL,
    AUTHENTICATED_APP_HTML,
    AuthenticatedAppPage,
)


FAKE_AUTH_TOKEN = "fake-local-token"


def fulfill_authenticated_app(route):
    route.fulfill(
        status=200,
        content_type="text/html",
        body=AUTHENTICATED_APP_HTML,
    )


def test_fresh_context_does_not_inherit_auth_state(page):
    page.route(APP_URL, fulfill_authenticated_app)
    first_app = AuthenticatedAppPage(page)
    first_app.open()
    page.evaluate(
        "token => localStorage.setItem('auth_token', token)",
        FAKE_AUTH_TOKEN,
    )
    first_app.open()

    expect(first_app.welcome_message).to_have_text("Welcome, Egor")

    fresh_context = page.context.browser.new_context()

    try:
        fresh_page = fresh_context.new_page()
        fresh_page.route(APP_URL, fulfill_authenticated_app)
        fresh_app = AuthenticatedAppPage(fresh_page)
        fresh_app.open()

        expect(fresh_app.sign_in_message).to_have_text("Please sign in.")
    finally:
        fresh_context.close()


def test_storage_state_restores_fake_auth_state(page, tmp_path):
    page.route(APP_URL, fulfill_authenticated_app)
    first_app = AuthenticatedAppPage(page)
    first_app.open()
    page.evaluate(
        "token => localStorage.setItem('auth_token', token)",
        FAKE_AUTH_TOKEN,
    )
    state_path = tmp_path / "fake-auth-state.json"
    page.context.storage_state(path=state_path)

    restored_context = page.context.browser.new_context(storage_state=state_path)

    try:
        restored_page = restored_context.new_page()
        restored_page.route(APP_URL, fulfill_authenticated_app)
        restored_app = AuthenticatedAppPage(restored_page)
        restored_app.open()

        expect(restored_app.welcome_message).to_have_text("Welcome, Egor")
    finally:
        restored_context.close()
