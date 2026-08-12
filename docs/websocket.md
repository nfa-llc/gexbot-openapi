# websocket real-time feed

> **Requires Quant Subscription**
>
> Data publishes during New York Stock Exchange cash hours from 9:30 AM through 4:00 PM Eastern Time.

The feed uses Azure Web PubSub.
The second-generation feed is called V2.
V2 sends analytics and spot as separate messages.

## recommended flow

1. Build the complete initial analytics group set.
2. Add one matching `{ticker}_spot` group for each analytics ticker.
3. Send the unprefixed groups to `POST /v2/negotiate`.
4. Connect to the returned `v2_*` hub URLs.
5. Listen for analytics and `proto.spot` messages on the same connections.
6. Use `PATCH /v2/negotiate` to replace the complete membership set without reconnecting.

The server joins the initial groups from the POST request.
Do not send `joinGroup` messages for this flow.

## group format

Analytics groups use this unprefixed format:

```text
{ticker}_{package}_{category}
```

Standard examples:

```text
SPX_classic_gex_full
SPX_state_gamma_zero
ES_SPX_orderflow_orderflow
```

Spot groups use this unprefixed format:

```text
{ticker}_spot
```

Examples:

```text
SPX_spot
ES_SPX_spot
```

Do not add the Web PubSub color prefix to a POST or PATCH request.
The server adds the configured prefix.

## V2 hub mapping

| V2 hub | Analytics group examples |
|---|---|
| `v2_classic` | `SPX_classic_gex_full`, `SPX_classic_gex_zero`, `SPX_classic_gex_one`, `SPX_classic_gex_20260717` |
| `v2_state_gex` | `SPX_state_gex_full`, `SPX_state_gex_zero`, `SPX_state_gex_one`, `SPX_state_gex_20260717` |
| `v2_state_greeks_zero` | `SPX_state_delta_zero`, `SPX_state_gamma_zero`, `SPX_state_vanna_zero`, `SPX_state_charm_zero` |
| `v2_state_greeks` | `SPX_state_delta_20260717`, `SPX_state_gamma_20260717`, `SPX_state_vanna_20260717`, `SPX_state_charm_20260717` |
| `v2_state_greeks_one` | `SPX_state_delta_one`, `SPX_state_gamma_one`, `SPX_state_vanna_one`, `SPX_state_charm_one` |
| `v2_orderflow` | `ES_SPX_orderflow_orderflow`, `SPX_orderflow_orderflow`, `SPX_orderflow_20260717` |

Each `{ticker}_spot` group uses every V2 hub that has analytics for that ticker.
There is no dedicated spot hub URL.
There is no second spot connection.

## explicit expirations

Discover valid expiration dates with:

```http
GET https://api.gex.bot/v2/options/{ticker}/expiries
```

Remove the dashes from a returned `YYYY-MM-DD` date.
For example, convert `2026-07-17` to `20260717`.

Explicit-expiration groups use these formats:

```text
{ticker}_classic_gex_YYYYMMDD
{ticker}_state_gex_YYYYMMDD
{ticker}_state_delta_YYYYMMDD
{ticker}_state_gamma_YYYYMMDD
{ticker}_state_vanna_YYYYMMDD
{ticker}_state_charm_YYYYMMDD
{ticker}_orderflow_YYYYMMDD
```

Explicit-expiration groups are real-time only.
They are not stored in REST history.
They publish at a lower cadence than standard groups.

Additional Quant tickers are available from:

```http
GET https://api.gex.bot/tickers/quant
```

These additional tickers are WebSocket-only.
They are not REST chart or history tickers.

## POST /v2/negotiate

List each spot group once in the POST body.
The server expands that group onto each applicable V2 hub.
A POST request with no spot groups remains on the current-generation hubs for compatibility.
Do not use the current-generation flow for a new custom Quant integration.

### request

```http
POST https://api.gex.bot/v2/negotiate
Authorization: Bearer <YOUR_API_KEY>
User-Agent: my-app/1.0
Accept: application/json
Content-Type: application/json
```

```json
{
  "groups": [
    "SPX_classic_gex_full",
    "SPX_state_gamma_zero",
    "SPX_spot",
    "ES_SPX_orderflow_orderflow",
    "ES_SPX_spot"
  ]
}
```

This request creates these memberships:

```text
v2_classic: SPX_classic_gex_full, SPX_spot
v2_state_greeks_zero: SPX_state_gamma_zero, SPX_spot
v2_orderflow: ES_SPX_orderflow_orderflow, ES_SPX_spot
```

### response

```json
{
  "websocket_urls": {
    "v2_classic": "wss://ws.gex.bot:443/client/hubs/v2_classic?access_token=<access_token>",
    "v2_state_gex": "wss://ws.gex.bot:443/client/hubs/v2_state_gex?access_token=<access_token>",
    "v2_state_greeks_zero": "wss://ws.gex.bot:443/client/hubs/v2_state_greeks_zero?access_token=<access_token>",
    "v2_state_greeks": "wss://ws.gex.bot:443/client/hubs/v2_state_greeks?access_token=<access_token>",
    "v2_state_greeks_one": "wss://ws.gex.bot:443/client/hubs/v2_state_greeks_one?access_token=<access_token>",
    "v2_orderflow": "wss://ws.gex.bot:443/client/hubs/v2_orderflow?access_token=<access_token>"
  }
}
```

The response can include every V2 hub that the API key can use.
Connect to each hub that your application uses.
Connect before the access token expires.

## spot messages

Spot arrives in a `google.protobuf.Any` envelope.
The type URL is:

```text
proto.spot
```

The Zstandard-compressed value contains a `spot_price.SpotPrice` Protocol Buffer message:

```proto
syntax = "proto3";

package spot_price;

message SpotPrice {
  int64 timestamp = 1;
  string ticker = 2;
  uint32 spot = 3;
  optional int64 source_timestamp_ms = 4;
}
```

The wire `spot` value is multiplied by 100.
Divide it by 100 to get the decimal price.

Analytics and spot for one calculation use the same ticker and timestamp.
Do not assume which message arrives first.
Cache either message briefly if your application must combine them.

## PATCH /v2/negotiate

PATCH replaces all active memberships for the current API WebSocket slot.
Any omitted membership is removed.

Each item must contain a V2 hub and an unprefixed group.
Repeat the spot membership on each V2 hub that has analytics for that ticker.

### request

```http
PATCH https://api.gex.bot/v2/negotiate
Authorization: Bearer <YOUR_API_KEY>
User-Agent: my-app/1.0
Accept: application/json
Content-Type: application/json
```

```json
{
  "groups": [
    { "hub": "v2_classic", "group": "SPX_classic_gex_full" },
    { "hub": "v2_classic", "group": "SPX_spot" },
    { "hub": "v2_state_greeks_zero", "group": "SPX_state_gamma_zero" },
    { "hub": "v2_state_greeks_zero", "group": "SPX_spot" },
    { "hub": "v2_orderflow", "group": "ES_SPX_orderflow_orderflow" },
    { "hub": "v2_orderflow", "group": "ES_SPX_spot" }
  ]
}
```

### response

```json
{
  "updated_groups": 6,
  "hubs": {
    "v2_classic": 2,
    "v2_state_gex": 0,
    "v2_state_greeks_zero": 2,
    "v2_state_greeks": 0,
    "v2_state_greeks_one": 0,
    "v2_orderflow": 2
  }
}
```

The client must have a live connection on each hub in the PATCH request.
Use POST and connect before you add groups to a new hub.

## group limits

- Standard Quant API keys allow 150 active hub-and-group memberships by default.
- A contract can define a different limit.
- Duplicate memberships count once.
- Server-expanded spot memberships count toward the limit.
- One spot group can consume more than one membership when its ticker uses more than one V2 hub.
- Each explicit-expiration metric is a separate membership.

An over-limit request returns `403 Forbidden`.

## connection behavior

- A successful POST closes the existing API WebSocket session for the same API slot.
- POST issues new signed URLs and joins the initial memberships.
- PATCH changes memberships without issuing new URLs.
- A dropped connection can require a new POST after its token expires.
- Binary messages are Zstandard-compressed Protocol Buffer messages.

## legacy GET compatibility

`GET /v2/negotiate` returns current-generation hub URLs and a group prefix.
Clients manually send `joinGroup` messages after they connect.

Custom Quant use of GET is deprecated.
Custom Quant clients should migrate to POST and PATCH.
Official Orderflow integrations continue to use the GET compatibility flow.

Legacy response example:

```json
{
  "websocket_urls": {
    "classic": "wss://ws.gex.bot:443/client/hubs/classic?access_token=<access_token>",
    "state_gex": "wss://ws.gex.bot:443/client/hubs/state_gex?access_token=<access_token>",
    "state_greeks_zero": "wss://ws.gex.bot:443/client/hubs/state_greeks_zero?access_token=<access_token>",
    "state_greeks": "wss://ws.gex.bot:443/client/hubs/state_greeks?access_token=<access_token>",
    "state_greeks_one": "wss://ws.gex.bot:443/client/hubs/state_greeks_one?access_token=<access_token>",
    "orderflow": "wss://ws.gex.bot:443/client/hubs/orderflow?access_token=<access_token>"
  },
  "prefix": "blue"
}
```

A legacy group name includes the returned prefix.
For example, use `blue_SPX_orderflow_orderflow`.

Do not create a new custom Quant integration with legacy GET.

## common problems

### the POST request returns a spot coverage error

**Cause:** An analytics ticker has no matching `{ticker}_spot` group, or a spot ticker has no analytics group.

**Fix:** Include one matching spot group for every analytics ticker in the POST body.

### the PATCH request returns a spot coverage error

**Cause:** A V2 analytics hub has no matching spot membership for the same ticker.

**Fix:** Add the `{ticker}_spot` membership to every V2 hub that has analytics for that ticker.

### no messages arrive after connection

**Cause:** The group is not in the current POST or PATCH membership set, or the client connected to the wrong hub.

**Fix:** Check the complete membership set and the V2 hub mapping.

### subscriptions disappear after PATCH

**Cause:** PATCH is a full replacement request.

**Fix:** Include every membership that must remain active in every PATCH request.
