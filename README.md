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

- **gexbot** — Options-derived market data: GEX (Gamma Exposure), greeks and orderflow metrics for enumerated tickers.
- **gexbot research** (`gbR`) — Chart and analytical data for a broad range of options metrics across any supported
  ticker, with a choice of output format, view and filter.

## documentation

This repository states the contract. [docs.gexbot.com](https://docs.gexbot.com/) states everything else. Read the
documentation site for a fact that this repository does not give.

| Page                                                                     | Subject                                                |
|--------------------------------------------------------------------------|--------------------------------------------------------|
| [api overview](https://docs.gexbot.com/apidocs)                          | Access tiers, permitted use, data cadence and quotas   |
| [authentication](https://docs.gexbot.com/apidocs/general/authentication) | Key formats, required headers and `/whoami`            |
| [rate limits](https://docs.gexbot.com/apidocs/general/rate-limits)       | Quota pools, the reset schedule and the 429 response   |
| [latency](https://docs.gexbot.com/apidocs/general/latency)               | Phase measurement, connection reuse and the poll rate  |
| [websocket feed](https://docs.gexbot.com/apidocs/quant/websocket)        | The negotiate flow, protobuf decode and session limits |
| [orderflow](https://docs.gexbot.com/apidocs/orderflow)                   | What each orderflow field measures                     |
| [research](https://docs.gexbot.com/apidocs/research)                     | Metric aliases, parameter defaults and output columns  |
| [metrics and theory](https://docs.gexbot.com/metrics)                    | What GEX, DEX, vanna and charm measure                 |
| [integrations](https://docs.gexbot.com/integrations)                     | The official platform plugins                          |
| [glossary](https://docs.gexbot.com/glossary)                             | Every term, acronym and alias                          |

### documentation for ai agents

The documentation site serves every page as plain markdown. Fetch a markdown feed. Do not parse the HTML.

| Feed                                                      | Content                                                             |
|-----------------------------------------------------------|---------------------------------------------------------------------|
| `https://docs.gexbot.com/llms.txt`                        | An index of every page, with one link and one description for each. |
| `https://docs.gexbot.com/llms-full.txt`                   | The markdown of every page, in one response.                        |
| `https://docs.gexbot.com/llms.mdx/docs/<slug>/content.md` | The markdown of one page.                                           |

Read `llms.txt` first. Read one `content.md` when the index names the page you need. Read `llms-full.txt` when you need
every page. For example, the rate limit page is at
`https://docs.gexbot.com/llms.mdx/docs/apidocs/general/rate-limits/content.md`.

## spec

- [YAML](latest/gexbot.spec3.yaml)
- [JSON](latest/gexbot.spec3.json)

The specification version is `2.5.5`.

Both files are generated. The source is `specs/public.yaml` in the private
repository `nfa-llc/nfa-api-openapi-spec`. A nightly build commits the result
here, so `master` always carries the current build. Do not edit `latest/` by
hand: the next build overwrites it. To change the published specification,
change the source.

### version

The API generation is the `v2` in the base URL. `info.version` is the version
of this document, which OpenAPI defines as distinct from the API version. The
author of a change raises it in the source repository, in the same pull request
that changes the contract. A raised patch therefore marks a new document, not a
compatible change to the API itself.

### base url

```
https://api.gex.bot/v2
```

A route in this document without a host is relative to this base URL. The same host also serves the legacy v1 routes without the
`/v2` prefix. This specification covers the v2 contract only.

### authentication

All endpoints except `/tickers`, `/tickers/quant` and `/{package}/categories` require a valid API key in the
`Authorization` header with the `Bearer` scheme. Every request must also include a `User-Agent` header.
Each product requires a dedicated API key — a **gexbot** key for the gexbot endpoints and a **gexbot research** (`gbR`)
key for the `/research` endpoints. Keys are not interchangeable between products.
Every product key can call `GET /whoami`. Use it to read the subscription levels, the add-ons and the permissions of a
key.

### endpoints

#### gexbot

| Method  | Endpoint                                     | Description                                             |
|---------|----------------------------------------------|---------------------------------------------------------|
| `GET`   | `/{ticker}/classic/{category}`               | Classic GEX chart data                                  |
| `GET`   | `/{ticker}/state/{category}`                 | State GEX and greeks chart data                         |
| `GET`   | `/{ticker}/orderflow/{category}`             | Orderflow metrics (category `orderflow`)                |
| `GET`   | `/{ticker}/classic/{category}/majors`        | Key GEX levels (classic)                                |
| `GET`   | `/{ticker}/state/{category}/majors`          | Key GEX levels (state)                                  |
| `GET`   | `/{ticker}/classic/{category}/maxchange`     | Max GEX change by lookback (classic)                    |
| `GET`   | `/{ticker}/state/{category}/maxchange`       | Max GEX change by lookback (state)                      |
| `GET`   | `/tickers`                                   | List available ticker symbols                           |
| `GET`   | `/{package}/categories`                      | List available data category names for a package        |
| `GET`   | `/tickers/quant`                             | List Quant WebSocket-only tickers (no API key)          |
| `GET`   | `/whoami`                                    | Identify the account and the API key of the caller      |
| `GET`   | `/options/{ticker}/expiries`                 | List all valid expiries for realtime groups             |
| `GET`   | `/futures/conversion`                        | Convert a cash ticker price to a futures price          |
| `GET`   | `/hist/{ticker}/{package}/{category}/{date}` | Download historical data                                |
| `GET`   | `/hist/eod/{ticker}`                         | Download the latest end-of-day ZIP report               |
| `POST`  | `/negotiate`                                 | Negotiate V2 WebSocket URLs, analytics, and spot groups |
| `PATCH` | `/negotiate`                                 | Replace active V2 WebSocket groups without reconnecting |
| `GET`   | `/negotiate`                                 | Legacy WebSocket negotiation compatibility              |

#### gexbot research (gbR)

| Method | Endpoint                      | Description                                 |
|--------|-------------------------------|---------------------------------------------|
| `GET`  | `/research/{ticker}/{metric}` | Research chart data for a ticker and metric |

### example

**gexbot — Request**

```http request
GET /SPX/classic/gex_full
Authorization: Bearer gexbot_custom_<your-api-key-secret>
User-Agent: my-app/1.0
Accept: application/json
```

> **Note:** Your gexbot API key must include both the prefix `gexbot_custom_` and your secret key in the `Authorization`
> header (e.g., `gexbot_custom_your-secret-key`).

**Response**

The example shows four strike rows. A live response returns every strike.

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
    [
      6890,
      -228.01,
      -86.9,
      [
        -240.55,
        -243.15,
        -245.22,
        -221.27,
        -220.12
      ]
    ],
    [
      6895,
      -48.47,
      69.76,
      [
        -49.05,
        -46.76,
        -45.55,
        -45.53,
        -42.97
      ]
    ],
    [
      7380,
      44.16,
      75.99,
      [
        0,
        47.7,
        47.3,
        0,
        40.55
      ]
    ],
    [
      7385,
      5.5,
      14.27,
      [
        0,
        0,
        0,
        0,
        0
      ]
    ]
  ],
  "sum_gex_vol": 1712585.519,
  "sum_gex_oi": 51521.105,
  "delta_risk_reversal": 0.118,
  "max_priors": [
    [
      7140,
      170979.742
    ],
    [
      7135,
      1145886.722
    ],
    [
      7135,
      997473.336
    ],
    [
      7135,
      1106210.715
    ],
    [
      7135,
      1128504.809
    ],
    [
      7135,
      1131150.488
    ]
  ]
}
```

### gexbot research (gbR) example

**Request**

```http request
GET /research/SPX/gex_both
Authorization: Bearer research_<your-gbR-api-key-secret>
User-Agent: my-app/1.0
Accept: application/json
```

> **Note:** The `/research` endpoints require a dedicated **gexbot research** (`gbR`) API key with `research_` prefix.
> This is separate from
> your gexbot API key and is not interchangeable.

**Query parameters (all optional)**

| Parameter           | Type    | Description                                                                               |
|---------------------|---------|-------------------------------------------------------------------------------------------|
| `format`            | string  | Output format: `png`, `jpeg`, `svg`, `pdf`, `json`, `csv`, `webp`                         |
| `view`              | string  | Chart view: `skew`, `term`, `surface`, `mirror`                                           |
| `type`              | string  | Chart type: `line`, `histogram`, `scatter`, `bar`                                         |
| `theme`             | string  | Color theme: `light`, `dark` (default: `dark`)                                            |
| `strikes`           | integer | Number of strikes to include                                                              |
| `start_dte`         | integer | Start DTE filter                                                                          |
| `end_dte`           | integer | End DTE filter                                                                            |
| `expiration_filter` | string  | Expiration date filter                                                                    |
| `contract_agg`      | boolean | Aggregate by contract                                                                     |
| `expiry_agg`        | boolean | Aggregate by expiry                                                                       |
| `skew_adj`          | boolean | Apply skew adjustment                                                                     |
| `limit_y`           | boolean | Limit y-axis range                                                                        |
| `series`            | string  | Term-view series: `moneyness`, `strikes`, `deltas`                                        |
| `contract_filter`   | string  | Filter contracts: `calls`, `puts`, `all`                                                  |
| `moneyness_filter`  | string  | Filter by moneyness or delta band: `atm`, `itm`, `ntm`, `otm`, `d10`, `d15`, `d20`, `d25` |

Send `Accept: text/csv` when `format` is `csv`. Send `Accept: application/json` for every other format.

### subscription tiers

Subscriptions are available for different data packages at https://www.gexbot.com/:

- **Classic** — the classic package and the EOD report
- **State** — Classic plus the state package
- **Orderflow** — State plus the orderflow package
- **Quant** — every package, the 90-day history downloads, the option expiries and the WebSocket feeds
- **Research** (add-on) — a **gexbot research** (`gbR`) key for the `/research` endpoints. The add-on is separate from
  the tiers above.

## websocket real-time feed

The WebSocket feed requires a Quant API key for a custom integration. Send the complete analytics group set to
`POST /negotiate`. Include one matching `{ticker}_spot` group for each analytics ticker. The server returns authorized
`v2_*` hub URLs and joins the initial memberships.
Analytics and spot use separate groups on the same V2 connections. Spot messages carry a type URL that contains
`proto.spot`.
A POST request with no spot groups remains on the current-generation hubs for compatibility.

Use `PATCH /negotiate` to replace the complete V2 membership set without reconnecting. Repeat each spot membership on
every V2 hub that has analytics for that ticker. Spot memberships count toward the WebSocket group limit.

Realtime analytics groups include the standard full/zero/one groups and explicit-expiry groups such as
`SPX_state_gamma_20260717`. Use `GET /options/{ticker}/expiries` to discover valid expiry dates. Use
`GET /tickers/quant` to discover additional Quant tickers. This route requires no API key. These tickers stream on the
WebSocket feed only. They are not valid on the REST chart routes.

Do not use `GET /negotiate` for a new custom Quant integration. Move an existing custom integration to POST and PATCH.
Official Orderflow integrations keep the GET flow.

See [docs/websocket.md](docs/websocket.md) for the full WebSocket real-time feed documentation.

## related repositories

- [quant-python-sockets](https://github.com/nfa-llc/quant-python-sockets) — Python client for real-time WebSocket feeds
- [quant-historical](https://github.com/nfa-llc/quant-historical) — Historical data download examples

## links

- [gexbot.com](https://www.gexbot.com)
- [documentation](https://docs.gexbot.com)
- [Terms and Conditions](https://www.gexbot.com/terms-and-conditions)
