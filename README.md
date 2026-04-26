# gexbot-openapi

The NFA gexbot OpenAPI Specification.

## Overview

This repository contains the [OpenAPI 3.0.1](https://spec.openapis.org/oas/v3.0.1) specification for the NFA gexbot API, which provides options-derived market data including GEX (Gamma Exposure), greeks, and orderflow metrics.

## Spec

The specification is located at [`latest/gexbot.spec3.yaml`](latest/gexbot.spec3.yaml).

### Base URL

```
https://api.gex.bot/v2
```

### Authentication

All endpoints (except `/tickers`) require a Bearer token in the `Authorization` header.

### Endpoints

| Endpoint | Description |
|---|---|
| `/{ticker}/classic/{category}` | Classic GEX chart data |
| `/{ticker}/state/{category}` | State greeks chart data |
| `/{ticker}/orderflow/{category}` | Orderflow metrics |
| `/{ticker}/classic/{category}/majors` | Key GEX levels (classic) |
| `/{ticker}/state/{category}/majors` | Key GEX levels (state) |
| `/{ticker}/classic/{category}/maxchange` | Max GEX change by lookback (classic) |
| `/{ticker}/state/{category}/maxchange` | Max GEX change by lookback (state) |
| `/tickers` | List available ticker symbols |
| `/hist/{ticker}/{package}/{category}/{date}` | Download historical data |
| `/negotiate` | Negotiate WebSocket connection |

### Subscription Tiers

- **Classic** — Classic GEX data
- **State** — State greeks data
- **Orderflow** — Orderflow metrics
- **Quant** — Full access including historical data and WebSocket feeds

## Related Repositories

- [quant-python-sockets](https://github.com/nfa-llc/quant-python-sockets) — Python client for real-time WebSocket feeds
- [quant-historical](https://github.com/nfa-llc/quant-historical) — Historical data download examples

## Links

- [gexbot.com](https://www.gexbot.com)
- [Terms and Conditions](https://www.gexbot.com/terms-and-conditions)
