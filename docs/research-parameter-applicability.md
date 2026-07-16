# research parameter applicability

The `GET /research/{ticker}/{metric}` endpoint accepts a flat list of optional query parameters, but not every
parameter applies to every request. This document defines the OpenAPI extensions used to encode those rules in
[`latest/gexbot.spec3.yaml`](../latest/gexbot.spec3.yaml) and provides the full applicability matrix, so clients
(such as interactive URL builders) can disable inapplicable controls up front.

## request routing

Requests are routed in two steps:

1. **Dedicated metrics** — a small set of metric values always render a fixed chart. The `view` parameter and all
   view-scoped parameters are ignored.
2. **Views** — every other metric renders one of three views selected by the `view` parameter: `skew` (the
   default), `term`, or `surface`.

Inapplicable or invalid optional query parameters are **silently ignored** and server defaults are applied; they
do not cause a `400` response. A request that mixes inapplicable parameters still succeeds — the extra parameters
simply have no effect.

## extensions

### `x-applicable_views` (parameter level)

An allowlist of the views in which the query parameter takes effect. When omitted, the parameter applies to all
views. Example:

```yaml
- name: strikes
  in: query
  x-applicable_views: [skew]
```

Clients should disable the control when the effective view (the `view` parameter, or `skew` when unset) is not in
the list, or when the selected metric is a dedicated metric that does not support the parameter.

### `x-chart_only` (parameter level)

`true` when the parameter only affects rendered charts. It has no effect when `format` is `json` or `csv`.

### `x-dedicated_metrics` (operation level)

Maps each dedicated metric value to the query parameters it supports (`supported_parameters`). All other query
parameters — including `view` — are ignored for these metrics.

## applicability matrix

Views apply to all non-dedicated metrics. ✓ means the parameter takes effect; ✗ means it is ignored.

| parameter           | skew | term | surface | max_pain | parity / put_call_parity | gamma_flip | chart only |
|---------------------|:----:|:----:|:-------:|:--------:|:------------------------:|:----------:|:----------:|
| `format`            |  ✓   |  ✓   |    ✓    |    ✓     |            ✓             |     ✓      |            |
| `theme`             |  ✓   |  ✓   |    ✓    |    ✓     |            ✓             |     ✓      |     ✓      |
| `start_dte`         |  ✓   |  ✓   |    ✓    |    ✓     |            ✓             |     ✓      |            |
| `end_dte`           |  ✓   |  ✓   |    ✓    |    ✓     |            ✓             |     ✓      |            |
| `expiration_filter` |  ✓   |  ✓   |    ✓    |    ✓     |            ✓             |     ✓      |            |
| `view`              |  —   |  —   |    —    |    ✗     |            ✗             |     ✗      |            |
| `type`              |  ✓   |  ✓   |    ✗    |    ✗     |            ✗             |     ✗      |     ✓      |
| `strikes`           |  ✓   |  ✗   |    ✗    |    ✗     |            ✗             |     ✗      |            |
| `series`            |  ✗   |  ✓   |    ✗    |    ✗     |            ✗             |     ✗      |     ✓      |
| `contract_filter`   |  ✓   |  ✓   |    ✓    |    ✗     |            ✓             |     ✗      |            |
| `moneyness_filter`  |  ✓   |  ✓   |    ✓    |    ✗     |            ✓             |     ✗      |            |
| `contract_agg`      |  ✓   |  ✓   |    ✗    |    ✗     |            ✗             |     ✗      |            |
| `expiry_agg`        |  ✓   |  ✗   |    ✗    |    ✗     |            ✗             |     ✗      |            |
| `skew_adj`          |  ✓   |  ✗   |    ✗    |    ✗     |            ✗             |     ✗      |     ✓      |
| `limit_y`           |  ✗   |  ✓   |    ✗    |    ✗     |            ✗             |     ✗      |     ✓      |

Notes:

- `view` selects the view for non-dedicated metrics (`—`) and is ignored by dedicated metrics.
- "chart only" parameters are ignored when `format` is `json` or `csv`, regardless of view.
- Defaults may vary by metric (for example, the default `type` and the default `strikes` count depend on the
  metric, and implied-volatility metrics default `moneyness_filter` to `ntm`). The spec documents the common
  defaults.

## maintenance

These extensions describe server routing behavior and must be updated together with the API implementation
whenever parameter handling changes. The YAML spec is the source of truth; regenerate the JSON spec after any
change.
