"""Flask and gRPC shopping application."""

import json
import os
from concurrent import futures

import grpc
from flask import Flask, jsonify, request

import greeting_pb2
import greeting_pb2_grpc
import ollama_client
import telemetry


app = Flask(__name__)
telemetry_providers = telemetry.configure(app)

PRODUCTS = {
    "coffee-mug": {
        "id": "coffee-mug",
        "name": "Cloud Coffee Mug",
        "description": "A durable mug for long coding sessions.",
        "price": 14.99,
        "currency": "USD",
        "stock": 25,
    },
    "mechanical-keyboard": {
        "id": "mechanical-keyboard",
        "name": "Mechanical Keyboard",
        "description": "A compact keyboard with tactile switches.",
        "price": 79.99,
        "currency": "USD",
        "stock": 12,
    },
    "developer-hoodie": {
        "id": "developer-hoodie",
        "name": "Developer Hoodie",
        "description": "A comfortable hoodie for everyday development.",
        "price": 49.99,
        "currency": "USD",
        "stock": 8,
    },
}


@app.get("/")
def index():
    return jsonify(
        {
            "message": "Flask and gRPC shopping service",
            "http_endpoints": ["/products", "/cart"],
            "grpc_service": "ShoppingCatalog/GetProducts",
        }
    )


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/products")
def products():
    return jsonify({"products": list(PRODUCTS.values())})


@app.get("/products/<product_id>")
def product(product_id):
    item = PRODUCTS.get(product_id)
    if item is None:
        return jsonify({"error": "product not found"}), 404
    return jsonify(item)


@app.post("/cart")
def cart():
    payload = request.get_json(silent=True) or {}
    product_id = payload.get("product_id")
    quantity = payload.get("quantity", 1)
    item = PRODUCTS.get(product_id)
    if item is None:
        return jsonify({"error": "product not found"}), 404
    if not isinstance(quantity, int) or quantity < 1:
        return jsonify({"error": "quantity must be a positive integer"}), 400
    if quantity > item["stock"]:
        return jsonify({"error": "requested quantity is unavailable"}), 409
    return jsonify(
        {
            "product_id": product_id,
            "quantity": quantity,
            "subtotal": round(item["price"] * quantity, 2),
            "currency": item["currency"],
        }
    ), 201


@app.post("/assistant")
def assistant():
    """Answer a shopping question using the local Ollama model."""
    payload = request.get_json(silent=True) or {}
    question = payload.get("question")
    if not isinstance(question, str) or not question.strip():
        return jsonify({"error": "question must be a non-empty string"}), 400

    catalog = json_catalog()
    prompt = (
        "You are a concise shopping assistant. Answer only using this product "
        f"catalog:\n{catalog}\n\nCustomer question: {question.strip()}"
    )
    try:
        answer = ollama_client.generate(prompt)
    except ollama_client.OllamaError as exc:
        return jsonify({"error": str(exc)}), 503
    return jsonify({"answer": answer, "model": os.getenv("OLLAMA_MODEL", "llama3.2")})


def json_catalog():
    """Return the catalog as stable JSON for the model prompt."""
    return json.dumps(list(PRODUCTS.values()), sort_keys=True)


class ShoppingCatalog(greeting_pb2_grpc.ShoppingCatalogServicer):
    def GetProduct(self, request, context):
        item = PRODUCTS.get(request.product_id)
        if item is None:
            context.abort(grpc.StatusCode.NOT_FOUND, "product not found")
        return greeting_pb2.Product(
            id=item["id"],
            name=item["name"],
            description=item["description"],
            price=item["price"],
            currency=item["currency"],
            stock=item["stock"],
        )


def serve_grpc(port: int) -> grpc.Server:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    greeting_pb2_grpc.add_ShoppingCatalogServicer_to_server(ShoppingCatalog(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    return server


def run() -> None:
    http_port = int(os.getenv("HTTP_PORT", "5000"))
    grpc_port = int(os.getenv("GRPC_PORT", "50051"))
    grpc_server = serve_grpc(grpc_port)
    try:
        app.run(host="0.0.0.0", port=http_port, debug=True, use_reloader=False)
    finally:
        grpc_server.stop(grace=5)
        telemetry.shutdown(telemetry_providers)


if __name__ == "__main__":
    run()
