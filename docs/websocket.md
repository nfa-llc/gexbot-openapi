# websocket real-time feed

> **Requires Quant Subscription**
>
> ⚠️ Data is only published during New York Stock Exchange cash hours (9:30 AM–4:00 PM ET).

Provides real-time, low-latency market data via WebSocket.

## connecting

1. Make a `GET /negotiate` request (with required headers) to receive connection URLs and the group `PREFIX`.
2. Connect to a hub (e.g., `classic`, `state`) and join groups (e.g., `blue_SPX_state_gamma_zero`) to subscribe.

### negotiate response

```json
{
  "websocket_urls": {
    "classic": "wss://ws.gex.bot:443/client/hubs/classic?access_token=<access_token>",
    "state_gex": "wss://ws.gex.bot:443/client/hubs/state_gex?access_token=<access_token>",
    "state_greeks_zero": "wss://ws.gex.bot:443/client/hubs/state_greeks_zero?access_token=<access_token>",
    "state_greeks_one": "wss://ws.gex.bot:443/client/hubs/state_greeks_one?access_token=<access_token>",
    "orderflow": "wss://ws.gex.bot:443/client/hubs/orderflow?access_token=<access_token>"
  },
  "prefix": "blue"
}
```

## messages

Messages are [Zstandard](https://facebook.github.io/zstd/)-compressed [Protobufs](https://protobuf.dev/).

## connection limits

- Each Quant subscriber is allowed **1 active connection per hub**. Additional requests to `/negotiate` will kick all existing connections.
- To maintain multiple hub connections simultaneously, use the authorized hub endpoints from a **single** negotiate request and connect to each hub within **15 minutes**.
- If a hub connection is dropped more than 15 minutes after negotiating, you must re-negotiate and re-connect to each hub.

## diagnosing with wscat

[wscat](https://github.com/websockets/wscat) is a command-line WebSocket client useful for verifying connectivity, join/leave group flow, and raw message delivery without writing any application code.

### install

```sh
npm install -g wscat
```

### connect to a hub

Use the full URL from the `/negotiate` response and specify the Azure Web PubSub subprotocol:

```sh
wscat -c "wss://ws.gex.bot:443/client/hubs/orderflow?access_token=<access_token>" \
      --subprotocol json.webpubsub.azure.v1
```

Replace `<access_token>` with the token from the corresponding `websocket_urls` entry in the negotiate response. Swap `orderflow` for any other hub name as needed.

### join a group

Once connected, send a `joinGroup` message. The `group` name must use the `prefix` returned by `/negotiate`:

```json
{"type":"joinGroup","group":"blue_SPX_orderflow_orderflow","ackId":1}
```

A successful join returns an ack:

```json
{"type":"ack","ackId":1,"success":true}
```

If `success` is `false`, double-check the hub/group pairing and that the prefix matches the negotiate response.

### what to look for

| Symptom | Likely cause |
|---|---|
| Connection closes immediately | Token expired or `/negotiate` was called again after connecting |
| Ack returns `success: false` | Wrong hub for the group, or malformed group name |
| Connection succeeds but no messages arrive | Outside NYSE cash hours, or group name prefix is wrong/hardcoded |
| Binary messages received | Expected — messages are Zstandard-compressed Protobufs and won't be human-readable in wscat |

## common problems

### connections dropped immediately after connecting

**Cause:** Calling `/negotiate` more than once before all hub connections are established.

Each call to `/negotiate` invalidates all previously issued access tokens and kicks any existing connections. If you negotiate a second time while still connecting to hubs from the first response, those connections will be dropped.

**Fix:** Call `/negotiate` exactly once, store the full response, then open all desired hub connections using the URLs from that single response. Only re-negotiate when a connection expires (beyond 15 minutes) or is lost.

---

### not receiving messages after connecting

**Cause:** Subscribing to groups on the wrong hub, or using a hardcoded prefix instead of the one returned by `/negotiate`.

Each hub only routes messages for its own groups:

| Hub                 | Group prefix pattern                             | Example group                      |
|---------------------|--------------------------------------------------|------------------------------------|
| `classic`           | `{prefix}_{ticker}_classic_{category}`           | `blue_SPX_classic_gex_full`        |
| `state_gex`         | `{prefix}_{ticker}_state_gex_{category}`         | `blue_SPX_state_gex_gamma`         |
| `state_greeks_zero` | `{prefix}_{ticker}_state_greeks_zero_{category}` | `blue_SPX_state_greeks_zero_delta` |
| `state_greeks_one`  | `{prefix}_{ticker}_state_greeks_one_{category}`  | `blue_SPX_state_greeks_one_delta`  |
| `orderflow`         | `{prefix}_{ticker}_orderflow_{category}`         | `blue_SPX_orderflow_orderflow`     |

Joining a `state_gex` group on the `classic` hub (or vice versa) will silently succeed but never deliver messages.

**Fix:** Always connect to the hub that matches the group you want, and always construct group names dynamically using the `prefix` field from the `/negotiate` response — do not hardcode it. The prefix can change between negotiate calls.

---

### can I connect to multiple hubs simultaneously on one Quant subscription?

Yes. You are allowed 1 active connection per hub, so you can hold connections to all hubs at the same time from a single subscription.

---

### is there a total connection limit beyond 1 per hub?

No. The only limit is 1 connection per hub. There is no additional cap on the number of hubs you connect to concurrently.

---

### does opening a new hub connection ever invalidate an existing one?

No, with one important exception: calling `/negotiate` again.

- **Connecting to a different hub** (e.g., connecting to `state_gex` while already connected to `classic`) using the *same* original `/negotiate` response will **not** affect your existing connection.
- **Connecting to the same hub again** using the same URL from the `/negotiate` response will disconnect your previous connection to that specific hub, because you are only allowed one active connection per hub.
- **Calling `/negotiate` a second time** to get new credentials will immediately invalidate **all** access tokens from the first response and kick **all** active connections.




