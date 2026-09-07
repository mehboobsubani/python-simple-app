# Python shopping application

This application exposes a small in-memory shopping catalog through Flask and
gRPC. It includes product browsing, product lookup, and cart subtotal
calculation.

## Run locally

```bash
cd application
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

The HTTP API listens on port `5000` and gRPC listens on port `50051`.

```bash
curl http://localhost:5000/products
curl http://localhost:5000/products/coffee-mug
curl -X POST http://localhost:5000/cart \
  -H 'Content-Type: application/json' \
  -d '{"product_id":"coffee-mug","quantity":2}'
```

## Run with Docker

```bash
cd application
docker build -t mehb786/python-simple-app:latest .
docker run --rm -p 5000:5000 -p 50051:50051 \
  mehb786/python-simple-app:latest
```

OpenTelemetry is configured through `OTEL_EXPORTER_OTLP_ENDPOINT`. The local
Compose file starts an OpenTelemetry Collector for development.
