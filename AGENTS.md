# AGENTS.md

## project overview
- OpenAPI specification for the NFA gexbot API.
- The API provides GEX (Gamma Exposure), greeks, orderflow, majors, and max change data for enumerated tickers and categories.
- Spec version: 2.2.0. Server: `https://api.gex.bot/v2`.

## key files & structure
- `latest/gexbot.spec3.yaml`: The main OpenAPI 3.0.1 specification (source of truth).
- `latest/gexbot.spec3.json`: JSON conversion of the YAML spec.
- `README.md`: Project overview, endpoint table, subscription tiers, and related repo links.
- `tests/`: HTTP client test files for the API (run via `ijhttp`).

## API patterns & conventions
- Endpoints are split by package prefix: `/{ticker}/classic/{category}`, `/{ticker}/state/{category}`, `/{ticker}/orderflow/{category}`.
- Sub-endpoints `/majors` and `/maxchange` exist under classic and state paths.
- Security is `bearer_auth` (HTTP Bearer token). The `/tickers` endpoint is the only unauthenticated endpoint (`security: []`).
- `User-Agent` and `Accept` headers are required on all requests (reusable parameters: `user_agent_header`, `accept_header`).
- Tickers are enumerated across `ticker_stock`, `ticker_index`, and `ticker_variant` schemas.
- Categories are scoped per package: `category_classic`, `category_state`, `category_orderflow`.
- Error responses use the shared `error_response` schema (`{"error": "..."}`).
- Response schemas: `basic_response`, `orderflow_response`, `majors_response`, `maxchange_response`.
- Tags represent subscription tiers: `Public`, `Classic`, `State`, `Orderflow`, `Quant`.
- **Rate limiting**: Data is not updated more than once per second. Requests should not exceed one request per second
  per ticker per metric.
- **HTTP client configuration**: Request timeouts should be configured to no more than 1 second.

## developer workflows
- To update the API, edit `latest/gexbot.spec3.yaml` directly.
- Regenerate the JSON spec from the YAML when the YAML changes.
- Run API tests: `ijhttp --private-env-file="tests/http-client.private.env.json" --env-file="tests/http-client.env.json" -L VERBOSE --env="production" .\tests\run_api_tests.http`
- Validate the spec using external tools (e.g., Swagger Editor, openapi-generator-cli) as needed.

## naming conventions
- All user-defined identifiers (schema names, parameter names, security scheme names, response names, property names) **must** use `snake_case`.
- Do not use camelCase or PascalCase for user-defined names. OpenAPI spec keywords (e.g., `oneOf`, `minLength`, `maxLength`, `termsOfService`) are exempt.
- Markdown headings in project files use lowercase.

## guidance for AI agents
- Always reference `latest/gexbot.spec3.yaml` for API details, allowed values, and parameter requirements.
- Do not assume additional endpoints, parameters, or workflows beyond what is defined in the spec.
- When documenting or generating code, use the exact enums and schema names from the spec.
- If extending the API, follow the existing structure and conventions in the spec.
- Respect rate limits: do not make more than one request per second per ticker per metric (data updates once per
  second).
- Configure HTTP client timeouts to 1 second or less.
- Keep the JSON spec in sync with the YAML spec after changes.

## example patterns
- Classic endpoint: `/{ticker}/classic/{category}` → `basic_response`
- State endpoint: `/{ticker}/state/{category}` → `basic_response`
- Orderflow endpoint: `/{ticker}/orderflow/orderflow` → `orderflow_response`
- Majors: `/{ticker}/classic/{category}/majors` → `majors_response`
- Max change: `/{ticker}/state/{category}/maxchange` → `maxchange_response`
- Ticker enums: `AAPL`, `SPX`, `ES_SPX`, ... (see `ticker_stock`, `ticker_index`, `ticker_variant`)
- Category enums: `full`, `gex_full`, `delta`, `gamma`, `orderflow`, ... (see `category_classic`, `category_state`, `category_orderflow`)
