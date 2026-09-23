import pytest
from playwright.sync_api import expect
from tests.pages.user_form_page import UserFormPage


@pytest.fixture
def user_form(page):
    user_form_page = UserFormPage(page)
    user_form_page.open()

    return user_form_page


def test_form_submits_with_valid_name_and_email(user_form):
    user_form.submit(name="Egor", email="egor@example.com")

    expect(user_form.success_message).to_have_text("Form submitted successfully.")


def test_invalid_email_shows_error_message(user_form):
    user_form.submit(name="Egor", email="invalid-email")

    expect(user_form.error_message).to_have_text("Enter a valid email address.")


def test_form_title_uses_test_id_as_fallback_locator(user_form):
    expect(user_form.title).to_have_text("User form")
