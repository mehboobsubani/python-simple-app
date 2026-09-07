# Kubernetes deployment

The application is packaged only as `helm/python-simple-app` at the repository
root and is deployed directly with Helm. It is not included in Flux and has no
Flux Kustomization or HelmRelease. The LGTM stack is packaged
only as Flux `HelmRelease` resources under `flux/observability`, grouped by a
Kustomize file. It includes Grafana, Loki, Tempo, Mimir, and Grafana Alloy.

The application source and Docker build context are under `application/`.
Build the image from that directory and push it as
`mehb786/python-simple-app:latest`.

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

The Flux Git URL is configured for
`https://github.com/mehboobsubani/python-simple-app`. For a private repository,
configure Flux authentication separately; no Secret or credential is included
in this repository. Set the Docker Hub image repository and tag in the
HelmRelease (or Helm values) rather than changing templates.

The local Helm values use ephemeral storage and are not intended for durable
production observability data. For production, configure persistent storage,
authentication, TLS, and appropriately sized resource requests.
