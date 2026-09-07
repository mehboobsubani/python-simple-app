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

Create the Docker Hub pull secret in the `flux-system` namespace:

```bash
kubectl create secret docker-registry dockerhub-credentials \
  --namespace flux-system \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username="$DOCKERHUB_USERNAME" \
  --docker-password="$DOCKERHUB_TOKEN"
```

Flux manages both HelmReleases. The Python HelmRelease selects the newest
published OCI chart using version constraint `>=0.1.0`. CI packages each
Python chart with the matching application image tag (`v1.0.<run_number>`), so
Flux upgrades the chart and image together without ImagePolicy or
ImageUpdateAutomation.

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
| Grafana | `lgtm-grafana`, port `30000` |
| Loki gateway | `lgtm-loki-gateway`, port `30100` |
| Tempo | `lgtm-tempo`, port assigned by Helm |
| Mimir | `lgtm-mimir-nginx`, port `30300` |
| Alloy OTLP/gRPC | `lgtm-alloy`, port assigned by Helm |
| Alloy OTLP/HTTP | `lgtm-alloy`, port assigned by Helm |

If the kind cluster does not publish NodePorts to the host, use
`kubectl port-forward` against the corresponding service instead.

For Grafana, the reliable local command is:

```bash
kubectl --context=kind-kind port-forward \
  -n observability svc/lgtm-grafana 3000:80
```

Then open `http://localhost:3000`.

The `observability-manifests` Git source points to
`https://github.com/mehboobsubani/python-simple-app` only so Flux can fetch the
LGTM manifests under `deploy/flux/observability`. It does not deploy or
reference the Python application Helm chart. For a private repository,
configure Flux authentication separately; no Secret or credential is included
in this repository.

The local Helm values use ephemeral storage and are not intended for durable
production observability data. For production, configure persistent storage,
authentication, TLS, and appropriately sized resource requests.
