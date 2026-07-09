<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset=".github/_inline_3-1_dark.webp" />
    <source media="(prefers-color-scheme: light)" srcset=".github/_inline_3-1_light.webp" />
    <img src=".github/_inline_3-1_light.webp" alt="gexbot" />
  </picture>
</p>

# gexbot-openapi

The NFA gexbot OpenAPI Specification.

## overview

This repository contains the [OpenAPI 3.0.1](https://spec.openapis.org/oas/v3.0.1) specification for the NFA gexbot API,
which covers two product offerings:

- **gexbot** — Options-derived market data including GEX (Gamma Exposure), greeks, and orderflow metrics for enumerated tickers.
- **gexbot research** (`gbR`) — Chart and analytical data for a broad range of options metrics across any supported ticker, with flexible output formats, views, and filtering.

## spec

- [YAML](latest/gexbot.spec3.yaml)
- [JSON](latest/gexbot.spec3.json)

### base url

```
https://api.gex.bot/v2
```

### authentication

All endpoints (except `/tickers`) require a valid API key passed as a Bearer token in the `Authorization` header.
Each product requires a dedicated API key — a **gexbot** key for the gexbot endpoints and a **gexbot research** (`gbR`) key for the `/research` endpoints. Keys are not interchangeable between products.

### endpoints

#### gexbot

| Endpoint                                     | Description                          |
|----------------------------------------------|--------------------------------------|
| `/{ticker}/classic/{category}`               | Classic GEX chart data               |
| `/{ticker}/state/{category}`                 | State greeks chart data              |
| `/{ticker}/orderflow/orderflow`              | Orderflow metrics                    |
| `/{ticker}/classic/{category}/majors`        | Key GEX levels (classic)             |
| `/{ticker}/state/{category}/majors`          | Key GEX levels (state)               |
| `/{ticker}/classic/{category}/maxchange`     | Max GEX change by lookback (classic) |
| `/{ticker}/state/{category}/maxchange`       | Max GEX change by lookback (state)   |
| `/tickers`                                   | List available ticker symbols        |
| `/hist/{ticker}/{package}/{category}/{date}` | Download historical data             |
| `POST /negotiate`                           | Negotiate WebSocket URLs and initial groups |
| `PATCH /negotiate`                          | Replace active WebSocket groups without reconnecting |
| `GET /negotiate`                            | Legacy WebSocket negotiation (deprecated) |

#### gexbot research (gbR)

| Endpoint                      | Description                                        |
|-------------------------------|----------------------------------------------------|
| `/research/{ticker}/{metric}` | Research chart data for a ticker and metric        |

### example

**gexbot — Request**

```http request
GET https://api.gex.bot/v2/SPX/classic/gex_full
Authorization: Bearer gexbot_custom_<your-api-key-secret>
User-Agent: my-app/1.0
Accept: application/json
```

> **Note:** Your gexbot API key must include both the prefix `gexbot_custom_` and your secret key in the `Authorization`
> header (e.g., `gexbot_custom_your-secret-key`).

**Response**

```json
{
  "timestamp": 1777492800,
  "ticker": "SPX",
  "min_dte": 0,
  "sec_min_dte": 1,
  "spot": 7138.55,
  "zero_gamma": 7112.95,
  "major_pos_vol": 7135,
  "major_pos_oi": 7200,
  "major_neg_vol": 7100,
  "major_neg_oi": 6900,
  "strikes": [
    [6890,-228.01,-86.9,[-240.55,-243.15,-245.22,-221.27,-220.12]],
    [6895,-48.47,69.76,[-49.05,-46.76,-45.55,-45.53,-42.97]],
    // Trimmed for brevity
    [7380,44.16,75.99,[0,47.7,47.3,0,40.55]],
    [7385,5.5,14.27,[0,0,0,0,0]]],
  "sum_gex_vol": 1712585.519,
  "sum_gex_oi": 51521.105,
  "delta_risk_reversal": 0.118,
  "max_priors": [
    [7140,170979.742],
    [7135,1145886.722],
    [7135,997473.336],
    [7135,1106210.715],
    [7135,1128504.809],
    [7135,1131150.488]
  ]
}
```

### gexbot research (gbR) example

**Request**

```http request
GET https://api.gex.bot/v2/research/SPX/gex_both
Authorization: Bearer <your-gbR-api-key>
User-Agent: my-app/1.0
Accept: application/json
```

> **Note:** The `/research` endpoints require a dedicated **gexbot research** (`gbR`) API key. This is separate from your gexbot API key and is not interchangeable.

**Query parameters (all optional)**

| Parameter           | Type    | Description                                                |
|---------------------|---------|------------------------------------------------------------|
| `format`            | string  | Output format: `png`, `jpeg`, `svg`, `pdf`, `html`, `json`, `csv`, `plotly`, `webp` |
| `view`              | string  | Chart view: `skew`, `term`, `surface`                      |
| `type`              | string  | Chart type: `line`, `histogram`, `scatter`, `bar`          |
| `chart_type`        | string  | Rendering engine: `matplotlib`, `plotly`                   |
| `theme`             | string  | Color theme: `light`, `dark` (default: `dark`)             |
| `strikes`           | number  | Number of strikes to include                               |
| `start_dte`         | number  | Start DTE filter                                           |
| `end_dte`           | number  | End DTE filter                                             |
| `expiration_filter` | string  | Expiration date filter                                     |
| `contract_agg`      | boolean | Aggregate by contract                                      |
| `expiry_agg`        | boolean | Aggregate by expiry                                        |
| `skew_adj`          | boolean | Apply skew adjustment                                      |
| `limit_y`           | boolean | Limit y-axis range                                         |
| `contract_filter`   | string  | Filter contracts: `calls`, `puts`, `all`                   |
| `moneyness_filter`  | string  | Filter by moneyness: `atm`, `itm`, `ntm`, `otm`, `d10`, `d15`, `d20`, `d25` |
| `model`             | string  | Pricing model: `gbR`, `theo`, `last`, `classic`, `state`   |
| `series`            | string  | Series type: `deltas`, `moneyness`, `strikes`              |

### subscription tiers

Subscriptions are available for different data packages at https://www.gexbot.com/:

- **Classic** — Classic GEX data
- **State** — State greeks data
- **Orderflow** — Orderflow metrics
- **Quant** — Full access including historical data and WebSocket feeds
- **Research** — gexbot research (`gbR`) access for chart and analytical data across any ticker and metric

## websocket real-time feed

Quant API users should use `POST /negotiate` to receive authorized hub URLs and auto-join initial groups. Use `PATCH /negotiate` to replace active group subscriptions without reconnecting. Legacy `GET /negotiate` is deprecated.

See [docs/websocket.md](docs/websocket.md) for the full WebSocket real-time feed documentation.

## related repositories

- [quant-python-sockets](https://github.com/nfa-llc/quant-python-sockets) — Python client for real-time WebSocket feeds
- [quant-historical](https://github.com/nfa-llc/quant-historical) — Historical data download examples

## links

- [gexbot.com](https://www.gexbot.com)
- [Terms and Conditions](https://www.gexbot.com/terms-and-conditions)
