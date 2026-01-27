# freqtrade-testing

This Helm chart deploys Freqtrade in Kubernetes for testing workflows: downloading
historical data, running backtests, and running hyperopt. It also includes an
optional web UI for inspecting results and the API.

## What it deploys

- A StatefulSet with two containers:
  - `testing`: runs download-data, backtesting, and/or hyperopt, then stays idle
  - `ui`: runs the Freqtrade webserver (optional)
- Secrets for `config.json` and API credentials
- ConfigMap for strategy files
- Services (headless + UI)
- Optional Ingress for the UI
- Optional PVC for persistent `user_data`

## Defaults and behavior

- Testing features are disabled by default. Enable them under `testing.*`.
- The UI is disabled by default. Enable it via `testing.ui.enabled`.
- When any of `testing.download_data.enabled`, `testing.backtesting.enabled`, or
  `testing.hyperopt.enabled` is true, the `testing` container becomes the default
  container for `kubectl exec` and `kubectl logs`.

## Minimal usage

Render:

```bash
helm template freqtrade-testing . -n freqtrade-testing
```

Install:

```bash
helm install freqtrade-testing . -n freqtrade-testing --create-namespace
```

## Enabling testing

Example: download data and run backtests.

```bash
helm upgrade --install freqtrade-testing . \
  -n freqtrade-testing \
  --create-namespace \
  --set testing.enabled=true \
  --set testing.download_data.enabled=true \
  --set testing.backtesting.enabled=true
```

## Enabling the UI

```bash
helm upgrade --install freqtrade-testing . \
  -n freqtrade-testing \
  --create-namespace \
  --set testing.enabled=true \
  --set testing.ui.enabled=true
```

Port-forward:

```bash
kubectl -n freqtrade-testing port-forward svc/freqtrade-testing-freqtrade-testing-ui 8080:8080
```

## Configuration

Key values:

- `config.*` Freqtrade configuration
- `testing.*` download/backtest/hyperopt controls
- `testing.ui.*` UI and ingress settings
- `image.*` container image and tag
- `persistance.*` PVC settings

## Notes

- The API password is generated if `config.api_server.password` is empty.
- Strategy selection is controlled by `strategy` and `strategies`.
