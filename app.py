"""Flask and gRPC greeting application."""

import os
from concurrent import futures

import grpc
from flask import Flask, jsonify, request

import greeting_pb2
import greeting_pb2_grpc
import telemetry


app = Flask(__name__)
telemetry_providers = telemetry.configure(app)


def greeting(name: str) -> str:
    """Return the shared greeting used by both transports."""
    return f"Hello, {name}!"


@app.get("/")
def index():
    return jsonify(
        {
            "message": "Flask and gRPC greeting service",
            "http_endpoint": "/greet?name=World",
            "grpc_service": "Greeter/SayHello",
        }
    )


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/greet")
def greet():
    name = request.args.get("name", "World").strip()
    if not name:
        return jsonify({"error": "name must not be empty"}), 400
    return jsonify({"message": greeting(name)})


class Greeter(greeting_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        name = request.name.strip()
        if not name:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "name must not be empty")
        return greeting_pb2.HelloReply(message=greeting(name))


def serve_grpc(port: int) -> grpc.Server:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    greeting_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
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
