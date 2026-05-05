# Klaviyo MCP Server
<!-- mcp-name: com.mcparmory/klaviyo -->

Base URL: https://a.klaviyo.com
| | |
|---|---|
| **Category** | Marketing |
| **Tools** | 295 |
| **Auth** | API Key, OAuth2 |

## API Info
- **API License:** License — [https://www.klaviyo.com/legal](https://www.klaviyo.com/legal)
- **Contact:** Klaviyo Developer Experience Team (developers@klaviyo.com) — [https://developers.klaviyo.com](https://developers.klaviyo.com)
- **Terms of Service:** [https://www.klaviyo.com/legal/api-terms](https://www.klaviyo.com/legal/api-terms)

---

## Install

### Quick Start (recommended)

```bash
OAUTH2_CLIENT_ID=YOUR_OAUTH2_CLIENT_ID \
OAUTH2_CLIENT_SECRET=YOUR_OAUTH2_CLIENT_SECRET \
OAUTH2_SCOPES=YOUR_OAUTH2_SCOPES \
API_KEY=YOUR_API_KEY \
uvx mcparmory-klaviyo
```

### With pip

```bash
pip install mcparmory-klaviyo
OAUTH2_CLIENT_ID=YOUR_OAUTH2_CLIENT_ID \
OAUTH2_CLIENT_SECRET=YOUR_OAUTH2_CLIENT_SECRET \
OAUTH2_SCOPES=YOUR_OAUTH2_SCOPES \
API_KEY=YOUR_API_KEY \
mcparmory-klaviyo
```

### MCP Client Configuration

Add to your MCP client config (e.g. Claude Desktop, Cursor, Codex):

```json
{
  "mcpServers": {
    "klaviyo": {
      "command": "uvx",
      "args": ["mcparmory-klaviyo"],
      "env": {
        "OAUTH2_CLIENT_ID": "YOUR_OAUTH2_CLIENT_ID",
        "OAUTH2_CLIENT_SECRET": "YOUR_OAUTH2_CLIENT_SECRET",
        "OAUTH2_SCOPES": "YOUR_OAUTH2_SCOPES",
        "API_KEY": "YOUR_API_KEY"
      }
    }
  }
}
```

Set `OAUTH2_SCOPES` to a comma-separated list of scopes your app requires (e.g. `OAUTH2_SCOPES=scope_a,scope_b`). Some OAuth2 providers may also use additional scope env vars such as `OAUTH2_USER_SCOPES`; open `.env` to see all generated scope buckets and descriptions.

---

## Credentials

Set the following environment variables (via MCP client `env` config, shell export, or `.env` file):

- `OAUTH2_CLIENT_ID` — OAuth2 client ID
- `OAUTH2_CLIENT_SECRET` — OAuth2 client secret
- `OAUTH2_SCOPES` — OAuth2 scopes (comma-separated)
- `API_KEY` — API Key Authentication (Authorization)
Do not commit credentials to version control.

### OAuth2

Add this **redirect URI** to your OAuth provider's allowed redirect URIs:

```
http://localhost:9400/callback
```

If you change `OAUTH2_CALLBACK_PORT` in `.env`, update the redirect URI to match.

On first use, a browser window opens automatically for OAuth authorization. Grant access when prompted — tokens are saved to `tokens/oauth2_tokens.json` and refreshed automatically.

**Re-authorization:** Delete `tokens/oauth2_tokens.json` and restart the server.

---

## Run Locally

**First**, configure your credentials in `.env` (see [Credentials](#credentials) above).

```bash
pip install -r requirements.txt
python server.py
```

## Connect MCP Client

Edit `.mcp.json` and replace `<SERVER_DIR>` with the absolute path to this directory, then add to your MCP client configuration.

Example (if server is at `/home/user/mcp-servers/klaviyo`):
```json
{
  "mcpServers": {
    "klaviyo": {
      "command": "python",
      "args": ["/home/user/mcp-servers/klaviyo/server.py"]
    }
  }
}
```

---

## Docker

### Pre-built image (recommended)

```bash
docker run -p 8000:8000 -p 9400:9400 -v ./tokens:/app/tokens \
  -e OAUTH2_CLIENT_ID=YOUR_OAUTH2_CLIENT_ID \
  -e OAUTH2_CLIENT_SECRET=YOUR_OAUTH2_CLIENT_SECRET \
  -e OAUTH2_SCOPES=YOUR_OAUTH2_SCOPES \
  -e API_KEY=YOUR_API_KEY \
  ghcr.io/mcparmory/klaviyo:latest
```

### Build from source

**First**, configure your credentials in `.env` (see [Credentials](#credentials) above).

```bash
docker build -t klaviyo .
mkdir -p tokens
docker run -p 8000:8000 -p 9400:9400 -v ./tokens:/app/tokens --env-file .env klaviyo
```

**Before running**, make sure ports 8000, 9400 are free. If you changed the callback port in `.env`, update the `-p` port mapping and your OAuth provider's redirect URI to match.

On first run, the server prints an authorization URL — check `docker logs` for the URL. Open it in your browser to complete OAuth consent. Tokens are persisted to `./tokens/` via the volume mount so re-authorization is not needed on subsequent runs.
### MCP client config (Docker)

For Docker, use SSE transport in your MCP client config:
```json
{
  "mcpServers": {
    "klaviyo": {
      "type": "sse",
      "url": "http://localhost:8000/sse"
    }
  }
}
```

---

## Files

- `.env` - Credentials and server configuration
- `.mcp.json` - MCP client config template
- `Dockerfile` - Container build
- `LICENSE` - MIT license for this generated code
- `requirements.txt` - Python dependencies
- `README.md` - This file
- `server.py` - MCP server entry point
- `_auth.py` - Authentication handlers
- `_models.py` - Request/response models
- `_validators.py` - Input validation

**Note:** Files starting with `.` are hidden by default on macOS/Linux. Use `ls -a` in terminal or enable "Show hidden files" in your file manager to see `.env` and `.mcp.json`.

---

<p align="center">
  <a href="https://mcpblacksmith.com"><img src="https://wjxawmrpsfuivlicnepc.supabase.co/storage/v1/object/public/newsletter/logo-blacksmith.png" alt="MCP Blacksmith" height="48"></a>
  <br>
  <sub>Generated by <a href="https://mcpblacksmith.com">MCP Blacksmith</a> · <a href="https://docs.mcpblacksmith.com/quickstart">Quickstart docs</a> · <a href="mailto:contact@mcpblacksmith.com">Report a bug</a></sub>
</p>
