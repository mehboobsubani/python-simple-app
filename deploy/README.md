# Kubernetes deployment

The repository now contains three deployment options:

- `kustomize/base` is a reusable application base.
- `kustomize/overlays/kind` is a one-replica local-kind overlay. Build the
  image as `python-simple-app:dev`, load it with `kind load docker-image`, and
  apply the overlay.
- `helm/python-simple-app` is the equivalent configurable Helm chart.
- `kustomize/observability` installs a deliberately small local LGTM stack
  (Loki, Grafana, Tempo, Prometheus) and Grafana Alloy. Alloy receives OTLP
  traces and metrics from the app, sends traces to Tempo, and remote-writes
  metrics to Prometheus. Grafana has anonymous viewer access for local use.
- `flux/observability` installs the same LGTM components through Flux
  `HelmRelease` resources backed by Grafana and Prometheus Community
  `HelmRepository` resources.
- `flux-system` contains credential-free Flux `GitRepository` and
  `Kustomization` objects. `flux/apps/helmrelease.yaml` installs the app chart.

The Flux Git URL is configured for
`https://github.com/mehboobsubani/python-simple-app`. For a private repository,
configure Flux authentication separately; no Secret or credential is included
in this repository. Set the Docker Hub image repository and tag in the
HelmRelease (or Helm values) rather than changing templates.

The local manifests use `emptyDir` storage and are not intended for durable
production observability data. For production, use the upstream Grafana Helm
charts with persistent storage, authentication, TLS, and appropriately sized
resource requests.
