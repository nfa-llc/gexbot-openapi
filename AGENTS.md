# AGENTS.md

## project overview
- OpenAPI specification for the NFA gexbot API.
- The API provides GEX (Gamma Exposure), greeks, orderflow, majors and max change data for enumerated tickers and categories. It also provides research charts, option expiries, futures conversion terms, history downloads, end-of-day reports and WebSocket negotiation.
- Spec version: 2.5.3. Server: `https://api.gex.bot/v2`. Every route in this file is relative to the server URL.
- The API generation is the `v2` in the server URL. `info.version` is the version of this document, which OpenAPI defines as distinct from the API version. The author of a change raises it in the source repository, in the same pull request that changes the contract. A raised patch marks a new document, not a compatible change to the API.

## complete documentation

This file and the spec state the contract. `https://docs.gexbot.com/` states everything else: access tiers, permitted use, data cadence, quota pools, field semantics, the WebSocket protocol, the metric definitions and the platform integrations.

The site serves every page as plain markdown. Fetch a markdown feed. Do not parse the HTML.

- `https://docs.gexbot.com/llms.txt` — an index of every page, with one link and one description for each.
- `https://docs.gexbot.com/llms-full.txt` — the markdown of every page, in one response.
- `https://docs.gexbot.com/llms.mdx/docs/<slug>/content.md` — the markdown of one page.

Read `llms.txt` first. Read one `content.md` when the index names the page you need. Read `llms-full.txt` when you need every page. For example, read the rate limit page at `https://docs.gexbot.com/llms.mdx/docs/apidocs/general/rate-limits/content.md`.

These pages answer a question that this repository does not answer:

| Page slug | Subject |
|---|---|
| `apidocs` | Access tiers, permitted use, data cadence, quotas |
| `apidocs/general/authentication` | Key formats, required headers, `/whoami` |
| `apidocs/general/rate-limits` | Quota pools, the reset schedule, the 429 response |
| `apidocs/general/latency` | Phase measurement, connection reuse, the poll rate |
| `apidocs/quant/websocket` | The negotiate flow, protobuf decode, session limits |
| `apidocs/quant/historical-download` | Retention, the signed URL, gzip, field name classes |
| `apidocs/general/historical-eod` | The archive contents per tier and the release schedule |
| `apidocs/orderflow` | What each orderflow field measures |
| `apidocs/research` | Metric aliases, parameter defaults, output columns |
| `metrics` | What GEX, DEX, vanna and charm measure |
| `integrations` | The official platform plugins |
| `glossary` | Every term, acronym and alias |

## key files & structure
- `latest/gexbot.spec3.yaml`: The published OpenAPI 3.0.1 specification. It is generated output, not the source.
- `latest/gexbot.spec3.json`: The JSON twin of the YAML. It is generated output too.
- `scripts/spec-version.py`: States `info.version` consistently in the four files that carry it. Run `--check` to prove they agree, and `--sync` to repair the twin and the prose after a hand edit to the YAML.
- `README.md`: Project overview, endpoint table, subscription tiers, and related repo links.
- `docs/websocket.md`: The WebSocket real-time feed guide for the `/negotiate` operations.

## API patterns & conventions
- Endpoints are split by package prefix: `/{ticker}/classic/{category}`, `/{ticker}/state/{category}`, `/{ticker}/orderflow/{category}`.
- Sub-endpoints `/majors` and `/maxchange` exist under classic and state paths.
- Security is `bearer_auth` (the API key in the `Authorization` header with the `Bearer` scheme). The `/tickers`, `/tickers/quant` and `/{package}/categories` endpoints are unauthenticated (`security: []`). The `/tickers/quant` tickers stream on the WebSocket feed only and are not valid on the REST chart routes.
- Each product requires a dedicated API key: a **gexbot** key for gexbot endpoints, and a **gexbot research** (`gbR`) key for `/research` endpoints. Keys are product-specific and not interchangeable.
- Every request must include a `User-Agent` header (400 if absent). Send `Accept: application/json` on the JSON routes. The `/hist/eod/{ticker}` route returns `application/zip`. The `/research/{ticker}/{metric}` route accepts `application/json` or `text/csv`. The spec keeps `accept_header` required as a client convention. The chart routes do not read the header. Reusable parameters: `user_agent_header`, `accept_header`.
- The chart routes enumerate tickers with `ticker` (`ticker_stock`, `ticker_index`, `ticker_variant`). The `/options/{ticker}/expiries` route uses `option_ticker`, which adds `quant_stock_ticker` and `quant_index_ticker`. The `/futures/conversion` route uses `futures_conversion_ticker` and `synth_future_ticker`. The `/research` route uses `research_ticker`, a pattern and not an enum.
- Categories are scoped per package: `category_classic`, `category_state`, `category_orderflow`. The `/{package}/categories` response uses `data_category`.
- Error responses use the shared `error_response` schema (`{"error": "..."}`).
- Chart response schemas: `basic_response`, `option_profile_response`, `orderflow_response`, `majors_response`, `maxchange_response`. Other response schemas: `quant_tickers_response`, `option_expiries_response`, `futures_conversion_response`, `research_asset_descriptor`, `websocket_negotiate_response`, `websocket_group_update_response`, `websocket_legacy_negotiate_response`, `who_am_i_response`.
- `GET /whoami` accepts every product API key, including a **gexbot research** key. It returns the subscription levels, the add-ons, the entitlements, the permissions and the account flags of the caller, and the masked API key. Call it to read the access of a key. Do not probe a data route to find the access.
- Tags represent subscription tiers: `Public`, `Classic`, `State`, `Orderflow`, `Quant`, `Research`.
- **Rate limits**: Data updates at most once per second. Do not send more than one request per second per ticker per
  metric. Quotas: each endpoint pool has a daily and a monthly allowance. A breach returns 429
  `{"error":"Rate limit exceeded."}`.
- **HTTP client configuration**: Use a short timeout (about 1 second) for the snapshot routes. Use a longer timeout for
  `/research` and `/hist`.

## developer workflows
- Do not edit `latest/` by hand. Both files are generated from `specs/public.yaml` in the private repository `nfa-llc/nfa-api-openapi-spec`, and the nightly build overwrites a hand edit.
- To change the published specification, change that source. An operation marked `x-public: false` there is held back from this repository.
- Run `python scripts/spec-version.py --check` to prove the version agrees in every file. Run `--sync` to repair the JSON twin and the prose lines.
- Integration tests live in the private `nfa-api-openapi-spec` repo (`tests/run_api_tests.http`).
- Validate the spec using external tools (e.g., Swagger Editor, openapi-generator-cli) as needed.

## naming conventions
- All user-defined identifiers (schema names, parameter names, security scheme names, response names, property names) **must** use `snake_case`.
- Do not use camelCase or PascalCase for user-defined names. OpenAPI spec keywords (e.g., `oneOf`, `minLength`, `maxLength`, `termsOfService`) are exempt.
- Markdown headings in project files use lowercase.

## guidance for AI agents
- Always reference `latest/gexbot.spec3.yaml` for API details, allowed values, and parameter requirements.
- Read `https://docs.gexbot.com/llms.txt` for a fact that the spec does not state. Do not guess the fact.
- Do not assume additional endpoints, parameters, or workflows beyond what is defined in the spec.
- The host also answers routes that are not part of this contract. Do not add a route to this spec without a decision
  recorded in the private `nfa-api-openapi-spec` repo.
- When documenting or generating code, use the exact enums and schema names from the spec.
- If extending the API, follow the existing structure and conventions in the spec.
- Respect rate limits: do not make more than one request per second per ticker per metric (data updates once per
  second).
- Use a short timeout (about 1 second) for the snapshot routes. Use a longer timeout for `/research` and `/hist`.
- Keep the JSON spec in sync with the YAML spec after changes.

## documentation language (ASD-STE100)

Write each file that explains this repo in **ASD-STE100 (Simplified Technical English)**: `AGENTS.md`, `README.md`,
everything under `docs/`, and every `summary`, `description` and `title` field in `latest/gexbot.spec3.yaml`.

- Use the active voice. Use the imperative for an instruction.
- Give one instruction in one sentence. Keep an instruction to 20 words, a description to 25.
- Use one term for one thing, in every file. Do not call an "API key" a "token" in the next paragraph.
- Use a simple tense. Do not use an `-ing` form as a verb or a noun.
- Keep a noun cluster to three words. Keep the articles: "set the connection string", not "set connection string".
- Never reword code. Identifiers, commands, paths, setting names and error strings stay exact.

## example patterns
- Classic endpoint: `/{ticker}/classic/{category}` → `basic_response`
- State endpoint: `/{ticker}/state/{category}` → `basic_response` for the gex categories, `option_profile_response` for the delta, gamma, vanna and charm categories
- Orderflow endpoint: `/{ticker}/orderflow/{category}` → `orderflow_response`
- Majors: `/{ticker}/classic/{category}/majors` → `majors_response`
- Max change: `/{ticker}/state/{category}/maxchange` → `maxchange_response`
- Ticker enums: `AAPL`, `SPX`, `ES_SPX`, ... (see `ticker`, `option_ticker`, `quant_stock_ticker`, `quant_index_ticker`, `futures_conversion_ticker`, `synth_future_ticker`)
- Category enums: `full`, `gex_full`, `delta`, `gamma`, `orderflow`, ... (see `category_classic`, `category_state`, `category_orderflow`, `data_category`)
