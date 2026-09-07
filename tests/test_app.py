import socket

import app
import grpc
import greeting_pb2
import greeting_pb2_grpc
import pytest


def test_http_greeting(client):
    response = client.get("/greet?name=Ada")

    assert response.status_code == 200
    assert response.get_json() == {"message": "Hello, Ada!"}


def test_http_greeting_rejects_empty_name(client):
    response = client.get("/greet?name=")

    assert response.status_code == 400
    assert response.get_json() == {"error": "name must not be empty"}


def test_grpc_greeting():
    with socket.socket() as sock:
        sock.bind(("localhost", 0))
        port = sock.getsockname()[1]
    server = app.serve_grpc(port)
    try:
        with grpc.insecure_channel(f"localhost:{port}") as channel:
            response = greeting_pb2_grpc.GreeterStub(channel).SayHello(
                greeting_pb2.HelloRequest(name="Grace")
            )
        assert response.message == "Hello, Grace!"
    finally:
        server.stop(0)


@pytest.fixture
def client():
    app.app.config.update(TESTING=True)
    with app.app.test_client() as test_client:
        yield test_client
