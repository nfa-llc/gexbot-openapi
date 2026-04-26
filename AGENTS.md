# AGENTS.md

## Project Overview
- This project contains the OpenAPI specification for the NFA gexbot API, located in `latest/gexbot.spec3.yaml`.
- The API provides endpoints for accessing chart data, max change data, and majors data for various tickers, packages, and categories.
- The API supports multiple versions/servers (see `servers` in the spec).

## Key Files & Structure
- `latest/gexbot.spec3.yaml`: The main OpenAPI 3.0.1 specification. All endpoints, schemas, parameters, and responses are defined here.
- `README.md`: Minimal, only states the project and spec purpose.

## API Patterns & Conventions
- All endpoints are parameterized by `{ticker}`, `{package}`, and `{category}` (see `paths`).
- Security is handled via `apiKeyAuth` (query param `key`) or `cookieAuth` (cookie `auth`).
- Tickers, packages, and categories are strictly enumerated in the spec (see `components/schemas`).
- Categories are grouped into `classic`, `state`, and `orderflow` packages, each with their own allowed values.
- Filters like `majors` and `maxchange` are supported for some endpoints.
- Responses are standardized and reference shared schemas (e.g., `BasicResponse`).

## Developer Workflows
- There are no build, test, or code generation scripts in this repo. It is a static OpenAPI spec repository.
- To update the API, edit `latest/gexbot.spec3.yaml` directly.
- Validate the OpenAPI spec using external tools (e.g., Swagger Editor, openapi-generator-cli) as needed.

## Integration Points
- The API is intended to be consumed by clients integrating with the NFA gexbot service at `https://api.gexbot.com` or `https://api.gex.bot/v2`.
- All integration details (parameters, security, response formats) are discoverable in the OpenAPI spec.

## Project-Specific Guidance for AI Agents
- Always reference `latest/gexbot.spec3.yaml` for any API details, including allowed values and parameter requirements.
- Do not assume additional endpoints, parameters, or workflows beyond what is defined in the spec.
- When documenting or generating code, use the exact enums and schema names from the spec.
- If extending the API, follow the structure and conventions already present in the OpenAPI file.
- No custom scripts, build tools, or test harnesses are present—focus on the OpenAPI file.

## Example Patterns
- Endpoint: `/{ticker}/{package}/{category}` (GET)
  - Parameters: `ticker`, `package`, `category`, `key` (optional, for apiKeyAuth)
  - Security: `apiKeyAuth` or `cookieAuth`
  - Response: `BasicResponse` schema
- Ticker enum example: `AAPL`, `AMD`, `AMZN`, ... (see `ticker_stock`)
- Package enum example: `classic`, `state`, `orderflow`
- Category enum example: `full`, `gex_full`, `zero`, ... (see `category_classic`, etc.)

