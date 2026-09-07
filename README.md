# Python shopping application

The Python shopping service is in [`application/`](application). It provides a
Flask product catalog and cart API, a gRPC product lookup service, and
OpenTelemetry instrumentation.

Run it locally or with Docker from that directory. Kubernetes deployment is managed by Flux from the OCI Helm charts in
`helm/python-simple-app` and `helm/lgtm`. The application and LGTM stack are
separate Flux HelmReleases; Kustomize only groups the LGTM HelmRelease.

## Ollama shopping assistant

The application uses a local Ollama model through `POST /assistant`.
Start Ollama, pull a model, and run the application with:

```bash
ollama pull llama3.2
export OLLAMA_URL=http://localhost:11434
export OLLAMA_MODEL=llama3.2
python application/app.py
```

Ask a catalog question:

```bash
curl -X POST http://localhost:5000/assistant \
  -H 'Content-Type: application/json' \
  -d '{"question":"Which product is best for a developer?"}'
```

With Docker Compose, the default
`http://host.docker.internal:11434` URL lets the container reach Ollama on
the host. Pull the model locally with `ollama pull llama3.2` first.
