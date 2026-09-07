# Kubernetes deployment

The application is packaged as the OCI chart `mehb786/python-simple-app` from
`helm/python-simple-app` and is deployed by Flux through a HelmRelease. The
LGTM stack is packaged as the OCI chart `mehb786/lgtm` from `helm/lgtm` and is
deployed by a separate Flux HelmRelease grouped by a small Kustomize file. It
includes Grafana, Loki, Tempo, Mimir, and Grafana Alloy.

The application source and Docker build context are under `application/`.
Build the image from that directory and push it as
`mehb786/python-simple-app:latest`.

The workflow at `.github/workflows/ci.yml` builds from `application/`, publishes
immutable image tags in the form `v1.0.${GITHUB_RUN_NUMBER}`, and publishes
both Helm charts as OCI artifacts with version `0.1.${GITHUB_RUN_NUMBER}`.
Configure
these repository secrets before enabling it:

```text
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
```

Flux manages both HelmReleases. Update the application image tag in
`deploy/flux-system/python-simple-app-helmrelease.yaml` to the CI-published
`v1.0.x` tag, and Flux will reconcile the new image. The chart versions are
selected from Docker Hub OCI using `>=0.1.0`.

Install or upgrade the application directly:

```bash
helm upgrade --install python-simple-app ./helm/python-simple-app \
  --namespace python-simple-app \
  --create-namespace \
  --set image.repository=mehb786/python-simple-app \
  --set image.tag=shopping-v2 \
  --set replicaCount=1 \
  --set ingress.enabled=true \
  --set otel.endpoint=http://alloy.observability.svc.cluster.local:4317
```

Alloy receives OTLP traces and metrics from the app, sends traces to Tempo,
and remote-writes metrics to Mimir. Grafana is provisioned with Mimir, Tempo,
and Loki datasources for Explore.

For the kind cluster, these observability services are exposed as NodePorts:

| Service | URL/port |
|---|---|
| Grafana | `http://localhost:30000` |
| Loki gateway | `http://localhost:30100` |
| Tempo | `http://localhost:30200` |
| Mimir | `http://localhost:30300` |
| Alloy OTLP/gRPC | `localhost:30431` |
| Alloy OTLP/HTTP | `localhost:30432` |

If the kind cluster does not publish NodePorts to the host, use
`kubectl port-forward` against the corresponding service instead.

The `observability-manifests` Git source points to
`https://github.com/mehboobsubani/python-simple-app` only so Flux can fetch the
LGTM manifests under `deploy/flux/observability`. It does not deploy or
reference the Python application Helm chart. For a private repository,
configure Flux authentication separately; no Secret or credential is included
in this repository.

The local Helm values use ephemeral storage and are not intended for durable
production observability data. For production, configure persistent storage,
authentication, TLS, and appropriately sized resource requests.
