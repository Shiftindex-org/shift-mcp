#!/usr/bin/env python3
"""
SHIFT Labour Demand Index — MCP server (Edition 1).

Makes the SHIFT index *invocable* by AI agents: an agent calls these tools and gets
the answer straight from the dataset, with citation and a link back to shiftindex.org.
Serves only the public occupation margin; the per-market detail and SHIFT Pull
magnitude stay the paid product at https://shiftindex.org/.

Run:
  python3 shift_mcp_server.py          # stdio (local, e.g. Claude Desktop)
  python3 shift_mcp_server.py http     # streamable-HTTP (remote, any MCP agent)
"""

import os

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
import shift_data as D


def _csv(name: str, default: str) -> list[str]:
    """Comma-separated environment variable -> list, blanks dropped."""
    return [v.strip() for v in os.environ.get(name, default).split(",") if v.strip()]


# The MCP SDK ships DNS-rebinding protection ON, and its allow-list is empty, so it
# only accepts a Host header of localhost. Behind any hosting provider every request
# arrives with that provider's hostname and the server answers 421 "Invalid Host
# header" to everything: the deploy looks healthy and no client ever connects.
# Measured with this exact file before the change, and again after.
#
# The protection STAYS ON. What changes is that the allow-list can be declared from
# the environment, so a deployed host is named explicitly instead of the guard being
# switched off. With MCP_ALLOWED_HOSTS unset the behaviour is exactly what it was:
# localhost only.
#
#   MCP_ALLOWED_HOSTS=shift-mcp.onrender.com,mcp.shiftindex.org
#   MCP_ALLOWED_ORIGINS=https://claude.ai        (only needed for browser clients;
#                                                 a request with no Origin passes)
mcp = FastMCP(
    "shift-labour-demand-index",
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=_csv(
            "MCP_ALLOWED_HOSTS", "localhost,localhost:*,127.0.0.1,127.0.0.1:*"
        ),
        allowed_origins=_csv("MCP_ALLOWED_ORIGINS", ""),
    ),
)


@mcp.tool()
def about() -> dict:
    """What the SHIFT Labour Demand Index is, how to cite it, and what is public vs paid."""
    return D.ABOUT


@mcp.tool()
def list_occupations() -> dict:
    """List all 23 kinds of work in SHIFT Edition 1 with AI-exposure class, worldwide posting
    direction (rose/fell), and how many of their visible markets saw fewer postings."""
    return D.list_payload()


@mcp.tool()
def get_occupation(occupation: str) -> dict:
    """Get the SHIFT reading for one kind of work. Accepts a label or key
    (e.g. 'Software developers', 'software_dev', 'nurses', 'marketing'). Returns the public
    margin (exposure class, worldwide direction, markets where postings fell) + a summary + citation."""
    r = D.match(occupation)
    if not r:
        return {"error": f"No single SHIFT occupation matched '{occupation}'. "
                         "Call list_occupations() to see the 23 available kinds of work."}
    return D.occupation_payload(r)


@mcp.tool()
def headline() -> dict:
    """The headline SHIFT findings: which kinds of work saw advertised demand fall worldwide,
    and the AI-exposed vs AI-resilient pattern. Answers 'which kinds of work saw the biggest
    falls in advertised job demand?'."""
    return D.headline_payload()


if __name__ == "__main__":
    import sys

    transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"

    if transport in ("http", "streamable-http"):
        # mcp.run(transport="streamable-http") binds 127.0.0.1:8000, which a hosting
        # provider cannot reach. Build the ASGI app ourselves so we can bind 0.0.0.0,
        # honour $PORT, and put CORS in front of it.
        import uvicorn
        from starlette.middleware.cors import CORSMiddleware

        host = "0.0.0.0"
        port = int(os.environ.get("PORT", 8000))
        mcp.settings.host = host
        mcp.settings.port = port

        # The MCP endpoint is mcp.settings.streamable_http_path, "/mcp" by default.
        app = mcp.streamable_http_app()
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
            # Without this a browser client cannot read the session id, and every
            # call after initialize starts a new session.
            expose_headers=["Mcp-Session-Id"],
        )

        print(
            "SHIFT MCP (streamable-HTTP) on "
            f"http://{host}:{port}{mcp.settings.streamable_http_path}"
        )
        uvicorn.run(app, host=host, port=port)

    elif transport == "sse":
        mcp.run(transport="sse")
    else:
        mcp.run()
