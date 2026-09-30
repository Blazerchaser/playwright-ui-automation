"""Opt-in comparison of one product expectation in normal and fault modes."""

from threading import Thread

import pytest
from playwright.sync_api import expect

from local_demo_server import create_server
from tests.pages.user_form_page import UserFormPage


@pytest.fixture(params=[False, True], ids=["normal", "fault"])
def demo_server(request):
    server = create_server(port=0, simulate_no_save=request.param)
    server_thread = Thread(target=server.serve_forever)
    server_thread.start()

    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        server_thread.join()


def test_post_201_persists_user(page, demo_server):
    form = UserFormPage(page)
    form.open_from_url(demo_server)
    name = "Regression learner"
    email = "regression@example.test"

    with page.expect_response(
        lambda response: response.url == f"{demo_server}/users"
        and response.request.method == "POST"
    ) as post_response_info:
        form.submit(name=name, email=email)

    post_response = post_response_info.value
    assert post_response.status == 201
    created = post_response.json()
    assert created == {"id": created["id"], "name": name, "email": email}
    expect(form.success_message).to_have_text(f"Created user: {name}")

    get_response = page.context.request.get(f"{demo_server}/users/{created['id']}")
    assert get_response.status == 200, (
        f"POST returned 201 for user {created['id']}, "
        f"but GET /users/{created['id']} returned {get_response.status}"
    )
    assert get_response.json() == created
