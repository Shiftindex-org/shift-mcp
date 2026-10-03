# SHIFT Labour Demand Index — MCP server (prototype)

Makes the **SHIFT Labour Demand Index** *invocable* by AI agents. Instead of hoping an
agent finds and cites the dataset, this turns SHIFT into a **tool the agent calls** and
gets the answer from — with citation and a link back to shiftindex.org.

It serves **only the public occupation margin** (direction + how many markets postings
fell in). The per-market breakdown and the SHIFT Pull magnitude stay the **paid product**
at https://shiftindex.org/ — every answer points there.

## Tools exposed
- **`about()`** — what SHIFT is, coverage, author (José Covas, ORCID + Wikidata), DOI, licence, how to cite.
- **`list_occupations()`** — all 23 kinds of work with AI-exposure class, worldwide direction, and markets where postings fell.
- **`get_occupation(occupation)`** — the reading for one kind of work (accepts a label or key, e.g. `"Software developers"`, `"software_dev"`, `"nurses"`, `"marketing"`), with a plain-language summary and citation.
- **`headline()`** — the headline finding ("which kinds of work saw the biggest falls in advertised job demand?") — the exact topic-probe question.

Every response carries: `citation` (Covas, J. 2026 + DOI), `source` (shiftindex.org), and the paid-detail pointer.

## Run it locally (stdio) — e.g. in Claude Desktop
```bash
pip install mcp
python3 shift_mcp_server.py        # stdio (default)
```
Claude Desktop config (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "shift": { "command": "python3", "args": ["/full/path/to/shift_mcp_server.py"] }
  }
}
```
Then ask Claude: *"Using the shift tools, which kinds of work saw advertised demand fall?"*

## Make it remote (so ANY agent can reach it over a URL)
```bash
python3 shift_mcp_server.py http   # serves a streamable-HTTP MCP endpoint
```
To put it in front of the world, deploy this one file (+ `pip install mcp`) to any small
always-on host — Render / Railway / Fly.io / a tiny VPS — and front it with a clean URL
(e.g. `https://mcp.shiftindex.org`). That URL is what you register with MCP-capable agents.

## Design notes (why it's built this way)
- **Public layer only.** No SHIFT Pull magnitude, no occupation×market matrix (that is the product). `markets_with_fewer_postings` is a *count*, never the list of which markets — so nothing paid leaks.
- **Anti-disintermediation.** Every answer cites the DOI and links to shiftindex.org, so being invoked still drives attribution and traffic to the product.
- **Honest semantics.** `rose/fell` is the change in *advertised postings*, not employment/wages, and not a causal AI claim; the 4 "not published" occupations carry no ahead/behind direction.

## Data provenance
Public margin `shift_ldi_2026_e1_by_occupation.csv` from
`github.com/Shiftindex-org/shift-labour-demand-index`, embedded verbatim.
SHIFT Labour Demand Index 2024–2026 (Edition 1), CC BY 4.0.
**Cite:** Covas, J. (2026). *SHIFT Labour Demand Index 2024–2026 (Edition 1)* [Data set]. SHIFT Research. https://doi.org/10.5281/zenodo.22346056
