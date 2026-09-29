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
