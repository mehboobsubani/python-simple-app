# Python shopping application

The Python shopping service is in [`application/`](application). It provides a
Flask product catalog and cart API, a gRPC product lookup service, and
OpenTelemetry instrumentation.

Run it locally or with Docker from that directory. Kubernetes deployment is managed by Flux from the OCI Helm charts in
`helm/python-simple-app` and `helm/lgtm`. The application and LGTM stack are
separate Flux HelmReleases; Kustomize only groups the LGTM HelmRelease.
