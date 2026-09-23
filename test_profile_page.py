from playwright.sync_api import expect

from tests.pages.profile_page import ProfilePage


def test_profile_name_is_rendered_from_mocked_response(page):
    page.route(
        "**/api/profile",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            headers={"Access-Control-Allow-Origin": "*"},
            body='{"name": "Egor"}',
        ),
    )
    profile_page = ProfilePage(page)
    profile_page.open()
    profile_page.load_profile()

    expect(profile_page.success_message).to_have_text("Profile loaded: Egor")


def test_profile_error_is_visible_when_mock_returns_500(page):
    page.route(
        "**/api/profile",
        lambda route: route.fulfill(
            status=500,
            headers={"Access-Control-Allow-Origin": "*"},
        ),
    )
    profile_page = ProfilePage(page)
    profile_page.open()
    profile_page.load_profile()

    expect(profile_page.error_message).to_have_text("Could not load profile.")
