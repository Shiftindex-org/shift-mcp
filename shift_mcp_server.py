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

from mcp.server.fastmcp import FastMCP
import shift_data as D

mcp = FastMCP("shift-labour-demand-index")


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
        mcp.run(transport="streamable-http")
    elif transport == "sse":
        mcp.run(transport="sse")
    else:
        mcp.run()
