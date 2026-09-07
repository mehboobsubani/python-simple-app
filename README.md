# Python shopping application

The Python shopping service is in [`application/`](application). It provides a
Flask product catalog and cart API, a gRPC product lookup service, and
OpenTelemetry instrumentation.

Run it locally or with Docker from that directory. Kubernetes deployment is
managed directly with the root-level Helm chart in `helm/python-simple-app`.
The Python app is not managed by Flux or Kustomize. The LGTM stack is managed
separately through Flux HelmReleases grouped by Kustomize.
