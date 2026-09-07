import socket

import app
import grpc
import greeting_pb2
import greeting_pb2_grpc
import pytest


def test_product_catalog(client):
    response = client.get("/products")

    assert response.status_code == 200
    assert len(response.get_json()["products"]) == 3


def test_add_product_to_cart(client):
    response = client.post(
        "/cart", json={"product_id": "coffee-mug", "quantity": 2}
    )

    assert response.status_code == 201
    assert response.get_json()["subtotal"] == 29.98


def test_missing_product_returns_not_found(client):
    response = client.get("/products/unknown")

    assert response.status_code == 404


def test_grpc_product_lookup():
    with socket.socket() as sock:
        sock.bind(("localhost", 0))
        port = sock.getsockname()[1]
    server = app.serve_grpc(port)
    try:
        with grpc.insecure_channel(f"localhost:{port}") as channel:
            product = greeting_pb2_grpc.ShoppingCatalogStub(channel).GetProduct(
                greeting_pb2.ProductRequest(product_id="coffee-mug")
            )
        assert product.name == "Cloud Coffee Mug"
    finally:
        server.stop(0)


@pytest.fixture
def client():
    app.app.config.update(TESTING=True)
    with app.app.test_client() as test_client:
        yield test_client
