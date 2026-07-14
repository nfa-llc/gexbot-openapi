# websocket real-time feed

> **Requires Quant Subscription**
>
> ⚠️ Data is only published during New York Stock Exchange cash hours (9:30 AM–4:00 PM ET).

Provides real-time, low-latency market data via Azure Web PubSub.

## recommended flow

1. Build the complete initial set of unprefixed groups you want.
2. `POST /v2/negotiate` with `{"groups": [...]}`.
3. Connect to the returned hub URLs. The response includes every hub URL authorized for your API key.
4. Listen for group messages. Requested groups are auto-joined by the server; do **not** call `joinGroup` for this POST flow.
5. To change groups without reconnecting, `PATCH /v2/negotiate` with the complete desired `{ hub, group }` set.

## group format

POST groups are unprefixed and use:

```text
{ticker}_{package}_{category}
```

Standard examples:

```text
SPX_classic_gex_full
SPX_state_gamma_zero
ES_SPX_orderflow_orderflow
```

Explicit-expiry groups use the same format with a `YYYYMMDD` category suffix:

```text
SPX_classic_gex_20260717
SPX_state_gex_20260717
SPX_state_delta_20260717
SPX_state_gamma_20260717
SPX_state_vanna_20260717
SPX_state_charm_20260717
SPX_orderflow_20260717
```

Discover valid expiry dates with:

```http
GET https://api.gex.bot/v2/options/{ticker}/expiries
```

The response returns every valid expiration for that ticker within the current-date-through-90-day horizon, including non-Friday expirations where available. Remove the dashes from a returned `YYYY-MM-DD` date to build the WebSocket group suffix. For example, `2026-07-17` becomes `20260717`.

Additional Quant tickers are discoverable with:

```http
GET https://api.gex.bot/tickers/quant
```

These supplemental Quant stock and index tickers are WebSocket/PubSub-only. They can publish realtime standard groups and explicit expiry groups, but they are not REST chart/history endpoints. The `indexes` response currently contains `XSP`.

Hub mapping:

| Hub | Group examples |
|---|---|
| `classic` | `SPX_classic_gex_full`, `SPX_classic_gex_zero`, `SPX_classic_gex_one`, `SPX_classic_gex_20260717` |
| `state_gex` | `SPX_state_gex_full`, `SPX_state_gex_zero`, `SPX_state_gex_one`, `SPX_state_gex_20260717` |
| `state_greeks_zero` | `SPX_state_delta_zero`, `SPX_state_gamma_zero`, `SPX_state_vanna_zero`, `SPX_state_charm_zero` |
| `state_greeks` | `SPX_state_delta_20260717`, `SPX_state_gamma_20260717`, `SPX_state_vanna_20260717`, `SPX_state_charm_20260717` |
| `state_greeks_one` | `SPX_state_delta_one`, `SPX_state_gamma_one`, `SPX_state_vanna_one`, `SPX_state_charm_one` |
| `orderflow` | `ES_SPX_orderflow_orderflow`, `SPX_orderflow_orderflow`, `SPX_orderflow_20260717` |

Notes:

- Explicit expiry groups are realtime WebSocket/PubSub-only; they are not persisted to REST history.
- Explicit expiry groups are published on a lower cadence than standard groups, currently about every 5 seconds.
- Explicit expiry groups use canonical option-owning tickers such as `SPX`, `NDX`, `SPY`, `QQQ`, Quant-only stock tickers, or the Quant-only `XSP` index.
- Volume groups are not available on the API WebSocket feed.

## POST /v2/negotiate

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
    "ES_SPX_orderflow_orderflow",
    "SOXL_state_gamma_20260717"
  ]
}
```

### response

```json
{
  "websocket_urls": {
    "classic": "wss://ws.gex.bot:443/client/hubs/classic?access_token=<access_token>",
    "state_gex": "wss://ws.gex.bot:443/client/hubs/state_gex?access_token=<access_token>",
    "state_greeks_zero": "wss://ws.gex.bot:443/client/hubs/state_greeks_zero?access_token=<access_token>",
    "state_greeks": "wss://ws.gex.bot:443/client/hubs/state_greeks?access_token=<access_token>",
    "state_greeks_one": "wss://ws.gex.bot:443/client/hubs/state_greeks_one?access_token=<access_token>",
    "orderflow": "wss://ws.gex.bot:443/client/hubs/orderflow?access_token=<access_token>"
  }
}
```

The response includes all hubs authorized for your API key. Initial groups from the POST body are auto-joined only on their matching hubs.

## PATCH /v2/negotiate

Use PATCH to replace active group subscriptions without reconnecting. This is a **full replacement** request: any currently-active group not present in the payload is removed server-side.

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
    { "hub": "classic", "group": "SPX_classic_gex_full" },
    { "hub": "state_greeks_zero", "group": "SPX_state_gamma_zero" },
    { "hub": "orderflow", "group": "ES_SPX_orderflow_orderflow" },
    { "hub": "state_greeks", "group": "SOXL_state_gamma_20260717" }
  ]
}
```

### response

```json
{
  "updated_groups": 4,
  "hubs": {
    "classic": 1,
    "state_gex": 0,
    "state_greeks_zero": 1,
    "state_greeks": 1,
    "state_greeks_one": 0,
    "orderflow": 1
  }
}
```

The `hub` value must match the group. For example, `SPX_classic_gex_full` must use hub `classic`.

## group limits

- Standard Quant API keys are limited to 150 active groups by default.
- Commercial or contracted API keys may have a higher custom group limit.
- Duplicate groups count once.
- Each explicit expiry metric is its own group, so multi-ticker/multi-expiry subscriptions can consume the limit quickly.
- Limits apply independently per API websocket slot.

Over-limit requests return `403 Forbidden`.

## messages

Messages are [Zstandard](https://facebook.github.io/zstd/)-compressed [Protobufs](https://protobuf.dev/). Explicit expiry groups use the same Protobuf message types as their standard package equivalents.

## connection behavior

- A successful POST negotiate closes existing API websocket connections for the same API websocket slot before issuing new URLs.
- PATCH replaces group memberships without reconnecting and does not issue new URLs.
- WebSocket URLs must be used before their connection token expires. If a connection is dropped after token expiration, negotiate again.
- Connect to the hub URLs returned by a single POST response. Connecting to additional hubs from that same response does not require another negotiate call.

## diagnosing with wscat

[wscat](https://github.com/websockets/wscat) can verify that a negotiated URL connects. For the POST flow, groups are server-joined; do not send `joinGroup`.

```sh
wscat -c "wss://ws.gex.bot:443/client/hubs/orderflow?access_token=<access_token>" \
      --subprotocol json.webpubsub.azure.v1
```

Binary messages are expected because payloads are compressed Protobufs.

## legacy GET /v2/negotiate

`GET /v2/negotiate` is deprecated and exists only for legacy clients. It returns a `prefix` and broad client-side join permissions so older clients can send Azure Web PubSub `joinGroup` messages.

New clients should use POST/PATCH. Do not build new integrations around legacy GET.

Legacy response shape:

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

Legacy group names must prepend the returned prefix, e.g. `blue_SPX_orderflow_orderflow`.

## common problems

### over-limit errors

**Cause:** The POST or PATCH request contains more groups than allowed for the API key.

**Fix:** Send fewer groups, or contact us if your commercial or contracted plan requires a custom group limit.

---

### no messages after connecting

**Cause:** The group was not included in the POST negotiate body or the latest PATCH replacement body, or the client is connected to the wrong hub.

**Fix:** Ensure every desired group is included in the current full group set and that the hub matches the group package/category. For explicit expiry groups, also confirm the ticker is canonical and the `YYYYMMDD` suffix came from `GET /v2/options/{ticker}/expiries`.

---

### subscriptions disappear after PATCH

**Cause:** PATCH is a full replacement. Omitted groups are removed.

**Fix:** Send every group you want to remain subscribed to in every PATCH request.
