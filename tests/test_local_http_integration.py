from threading import Thread

import pytest
from playwright.sync_api import expect

from local_demo_server import create_server
from tests.pages.user_form_page import UserFormPage


@pytest.fixture
def local_users_server():
    server = create_server(port=0)
    server_thread = Thread(target=server.serve_forever)
    server_thread.start()

    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        server_thread.join()


@pytest.fixture
def fault_users_server():
    server = create_server(port=0, simulate_no_save=True)
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


def test_duplicate_email_shows_conflict_without_creating_user(page, local_users_server):
    user_form = UserFormPage(page)
    user_form.open_from_url(local_users_server)
    email = "learner@example.test"
    post_user = lambda response: (
        response.url == f"{local_users_server}/users"
        and response.request.method == "POST"
    )

    with page.expect_response(post_user) as first_response_info:
        user_form.submit(name="Learner", email=email)

    first_response = first_response_info.value
    first_user = {"id": 1, "name": "Learner", "email": email}
    assert first_response.status == 201
    assert first_response.json() == first_user
    expect(user_form.success_message).to_have_text("Created user: Learner")

    first_get = page.context.request.get(f"{local_users_server}/users/1")
    assert first_get.status == 200
    assert first_get.json() == first_user

    with page.expect_response(post_user) as duplicate_response_info:
        user_form.submit(name="Another learner", email=email)

    duplicate_response = duplicate_response_info.value
    assert duplicate_response.status == 409
    assert duplicate_response.request.post_data_json["email"] == email
    assert duplicate_response.json() == {"error": "Email already exists."}
    expect(user_form.error_message).to_have_text("Email already exists.")
    expect(user_form.success_message).to_have_count(0)

    second_get = page.context.request.get(f"{local_users_server}/users/2")
    assert second_get.status == 404
    unchanged_get = page.context.request.get(f"{local_users_server}/users/1")
    assert unchanged_get.json() == first_user


def test_fault_mode_is_deterministic_training_fixture(page, fault_users_server):
    """Verify the opt-in simulation itself, not a regression against the app."""
    user_form = UserFormPage(page)
    user_form.open_from_url(fault_users_server)

    with page.expect_response(
        lambda response: response.url == f"{fault_users_server}/users"
        and response.request.method == "POST"
    ) as post_response_info:
        user_form.submit(name="Demo learner", email="demo@example.test")

    first_response = post_response_info.value
    assert first_response.status == 201
    assert first_response.json() == {
        "id": 1, "name": "Demo learner", "email": "demo@example.test"
    }
    expect(user_form.success_message).to_have_text("Created user: Demo learner")
    assert page.context.request.get(f"{fault_users_server}/users/1").status == 404

    second_response = page.context.request.post(
        f"{fault_users_server}/users",
        data={"name": "Second learner", "email": "second@example.test"},
    )
    assert second_response.status == 201
    assert page.context.request.get(f"{fault_users_server}/users/1").json() == {
        "id": 1, "name": "Second learner", "email": "second@example.test"
    }
