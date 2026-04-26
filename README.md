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
which provides options-derived market data including GEX (Gamma Exposure), greeks, and orderflow metrics.

## spec

The specification is located at [`latest/gexbot.spec3.yaml`](latest/gexbot.spec3.yaml).

### base url

```
https://api.gex.bot/v2
```

### authentication

All endpoints (except `/tickers`) require a valid gexbot API key in the `Authorization` header.

### endpoints

| Endpoint                                     | Description                          |
|----------------------------------------------|--------------------------------------|
| `/{ticker}/classic/{category}`               | Classic GEX chart data               |
| `/{ticker}/state/{category}`                 | State greeks chart data              |
| `/{ticker}/orderflow/{category}`             | Orderflow metrics                    |
| `/{ticker}/classic/{category}/majors`        | Key GEX levels (classic)             |
| `/{ticker}/state/{category}/majors`          | Key GEX levels (state)               |
| `/{ticker}/classic/{category}/maxchange`     | Max GEX change by lookback (classic) |
| `/{ticker}/state/{category}/maxchange`       | Max GEX change by lookback (state)   |
| `/tickers`                                   | List available ticker symbols        |
| `/hist/{ticker}/{package}/{category}/{date}` | Download historical data             |
| `/negotiate`                                 | Negotiate WebSocket connection       |

### subscription tiers

Subscriptions are available for different data packages at https://www.gexbot.com/:

- **Classic** — Classic GEX data
- **State** — State greeks data
- **Orderflow** — Orderflow metrics
- **Quant** — Full access including historical data and WebSocket feeds

## related repositories

- [quant-python-sockets](https://github.com/nfa-llc/quant-python-sockets) — Python client for real-time WebSocket feeds
- [quant-historical](https://github.com/nfa-llc/quant-historical) — Historical data download examples

## links

- [gexbot.com](https://www.gexbot.com)
- [Terms and Conditions](https://www.gexbot.com/terms-and-conditions)
