# Deploying SHIFT as an invocable service

Two ways an agent can call SHIFT; you can run either or both from the same files.

| Service | File | For | Start command |
|---|---|---|---|
| **REST + OpenAPI** | `shift_api.py` | ChatGPT custom-GPT **Actions**, any HTTP agent, browser | `uvicorn shift_api:app --host 0.0.0.0 --port $PORT` |
| **MCP** | `shift_mcp_server.py` | Claude & MCP-native agents | `python shift_mcp_server.py http` |

Both read the same public margin (`shift_data.py`). Files to deploy: `shift_data.py`,
`shift_api.py`, `shift_mcp_server.py`, `requirements.txt`, `Dockerfile`.

## Fastest path — one container host (Render / Railway / Fly.io)
These build the included `Dockerfile` and give you a public HTTPS URL. No account of
mine can do this for you; the steps are a few clicks with your own account.

1. Push this folder to a GitHub repo (e.g. `Shiftindex-org/shift-mcp`).
2. On the host, "New → Web Service → from repo", pick this repo. It auto-detects the Dockerfile.
3. Set env var **`SHIFT_PUBLIC_URL`** to the URL the host assigns (e.g. `https://shift-api.onrender.com`) so the OpenAPI `servers` block is correct. Redeploy.
4. You now have: `…/docs` (try it), `…/openapi.json` (for ChatGPT), `…/headline`, `…/occupations`, `…/occupation/software_dev`.

The container defaults to the **REST/OpenAPI** service. To run the **MCP** service instead,
change the host's start command to `python shift_mcp_server.py http` (or add a second service).

Nice-to-have: front it with a clean domain, e.g. `api.shiftindex.org` (REST) and/or
`mcp.shiftindex.org` (MCP), via your DNS.

## Wire it to ChatGPT (custom GPT Action)
1. ChatGPT → **Create a GPT → Configure → Actions → Create new action**.
2. **Import from URL**: `https://<your-api-url>/openapi.json`.
3. Auth: **None** (the data is public, CC BY 4.0).
4. Save. Ask the GPT: *"Which kinds of work saw advertised demand fall? Use the SHIFT action."*

## Wire it to Claude Desktop
- **Local (stdio):** add to `claude_desktop_config.json`:
  ```json
  { "mcpServers": { "shift": { "command": "python3", "args": ["/full/path/shift_mcp_server.py"] } } }
  ```
- **Remote (hosted MCP):** run `python shift_mcp_server.py http` on the host and add the
  resulting MCP URL as a connector where your client supports remote MCP.

## Keep it honest / on-brand
- Public margin only — no SHIFT Pull magnitude, no occupation×market list (that is the product).
- Every response cites the DOI and links to shiftindex.org — invocation drives attribution + traffic.
- Author identity is baked in (`about`): José Covas, ORCID `0009-0000-2298-0626`, Wikidata `Q141324073`.
