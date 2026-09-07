# Python Flask + gRPC app

A small Python application exposing the same greeting through a Flask HTTP API
and a gRPC service.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

The HTTP API listens on `http://localhost:5000` and gRPC listens on
`localhost:50051`. Ports can be changed with `HTTP_PORT` and `GRPC_PORT`.

```bash
curl http://localhost:5000/health
curl "http://localhost:5000/greet?name=Ada"
```

The gRPC contract is in `proto/greeting.proto`. A Python client can call it
with `greeting_pb2_grpc.GreeterStub`:

```python
import grpc
import greeting_pb2
import greeting_pb2_grpc

with grpc.insecure_channel("localhost:50051") as channel:
    stub = greeting_pb2_grpc.GreeterStub(channel)
    print(stub.SayHello(greeting_pb2.HelloRequest(name="Ada")).message)
```

Run the tests with:

```bash
python -m pytest
```

## Run with Docker

Build and start the container:

```bash
docker build -t python-simple-app .
docker run --rm --name python-simple-app \
  -p 5000:5000 \
  -p 50051:50051 \
  python-simple-app
```

The same HTTP and gRPC endpoints are then available on the host at ports
`5000` and `50051`. Flask debug mode is enabled for local development, with
the reloader disabled so the gRPC server is started only once.

## OpenTelemetry and LGTM

The Flask and gRPC servers are instrumented with OpenTelemetry. Traces and
metrics are exported using OTLP/gRPC. Start the application and a local
OpenTelemetry Collector together:

```bash
docker compose up --build
```

If an existing container already owns ports `5000` or `50051`, stop it first
with `docker stop python-simple-app`, or use alternate host ports:

```bash
APP_HTTP_PORT=15000 APP_GRPC_PORT=15051 docker compose up --build
```

Generate a trace:

```bash
curl "http://localhost:5000/greet?name=Ada"
```

The collector receives OTLP on ports `4317` (gRPC) and `4318` (HTTP), and
prints received spans and metrics in its logs:

```bash
docker compose logs -f otel-collector
```

The collector currently uses the `debug` exporter so traces are immediately
visible. Replace that exporter with Tempo or another LGTM backend later. For a
standalone app container, set `OTEL_EXPORTER_OTLP_ENDPOINT` to the hostname
and port of your collector, for example `http://otel-collector:4317` when
both containers share a Docker network.
