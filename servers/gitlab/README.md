# GitLab MCP Server
<!-- mcp-name: com.mcparmory/gitlab -->

Base URL: https:///api/v4
| | |
|---|---|
| **Category** | Developer Tools |
| **Tools** | 52 |
| **Auth** | API Key, OAuth2 |

## API Info
- **API License:** CC BY-SA 4.0 — [https://gitlab.com/gitlab-org/gitlab/-/blob/master/LICENSE](https://gitlab.com/gitlab-org/gitlab/-/blob/master/LICENSE)
- **Terms of Service:** [https://about.gitlab.com/terms/](https://about.gitlab.com/terms/)

---

## Install

### Quick Start (recommended)

```bash
OAUTH2_CLIENT_ID=YOUR_OAUTH2_CLIENT_ID \
OAUTH2_CLIENT_SECRET=YOUR_OAUTH2_CLIENT_SECRET \
OAUTH2_SCOPES=YOUR_OAUTH2_SCOPES \
API_KEY=YOUR_API_KEY \
SERVER_GITLAB_HOST=YOUR_SERVER_GITLAB_HOST \
uvx mcparmory-gitlab
```

### With pip

```bash
pip install mcparmory-gitlab
OAUTH2_CLIENT_ID=YOUR_OAUTH2_CLIENT_ID \
OAUTH2_CLIENT_SECRET=YOUR_OAUTH2_CLIENT_SECRET \
OAUTH2_SCOPES=YOUR_OAUTH2_SCOPES \
API_KEY=YOUR_API_KEY \
SERVER_GITLAB_HOST=YOUR_SERVER_GITLAB_HOST \
mcparmory-gitlab
```

### MCP Client Configuration

Add to your MCP client config (e.g. Claude Desktop, Cursor, Codex):

```json
{
  "mcpServers": {
    "gitlab": {
      "command": "uvx",
      "args": ["mcparmory-gitlab"],
      "env": {
        "OAUTH2_CLIENT_ID": "YOUR_OAUTH2_CLIENT_ID",
        "OAUTH2_CLIENT_SECRET": "YOUR_OAUTH2_CLIENT_SECRET",
        "OAUTH2_SCOPES": "YOUR_OAUTH2_SCOPES",
        "API_KEY": "YOUR_API_KEY",
        "SERVER_GITLAB_HOST": "YOUR_SERVER_GITLAB_HOST"
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
- `API_KEY` — API Key Authentication (Private-Token)
- `SERVER_GITLAB_HOST` — The hostname of your GitLab instance, visible in your browser URL bar.

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

Example (if server is at `/home/user/mcp-servers/gitlab`):
```json
{
  "mcpServers": {
    "gitlab": {
      "command": "python",
      "args": ["/home/user/mcp-servers/gitlab/server.py"]
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
  -e SERVER_GITLAB_HOST=YOUR_SERVER_GITLAB_HOST \
  ghcr.io/mcparmory/gitlab:latest
```

### Build from source

**First**, configure your credentials in `.env` (see [Credentials](#credentials) above).

```bash
docker build -t gitlab .
mkdir -p tokens
docker run -p 8000:8000 -p 9400:9400 -v ./tokens:/app/tokens --env-file .env gitlab
```

**Before running**, make sure ports 8000, 9400 are free. If you changed the callback port in `.env`, update the `-p` port mapping and your OAuth provider's redirect URI to match.

On first run, the server prints an authorization URL — check `docker logs` for the URL. Open it in your browser to complete OAuth consent. Tokens are persisted to `./tokens/` via the volume mount so re-authorization is not needed on subsequent runs.
### MCP client config (Docker)

For Docker, use SSE transport in your MCP client config:
```json
{
  "mcpServers": {
    "gitlab": {
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
