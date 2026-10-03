#!/usr/bin/env python3
"""
SHIFT Labour Demand Index — REST + OpenAPI service (Edition 1).

Same public-margin data as the MCP server, exposed as a plain HTTP/JSON API so it can
be used as a ChatGPT custom-GPT "Action" (OpenAPI) or by any HTTP agent. FastAPI serves
the OpenAPI schema at /openapi.json and interactive docs at /docs.

Run locally:
  pip install fastapi "uvicorn[standard]"
  uvicorn shift_api:app --host 0.0.0.0 --port 8000
Then: http://localhost:8000/docs  and  http://localhost:8000/openapi.json

For a ChatGPT Action: deploy this, set SHIFT_PUBLIC_URL to the public base URL so the
OpenAPI `servers` block points at it, then import <url>/openapi.json into the GPT builder.
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shift_data as D

PUBLIC_URL = os.environ.get("SHIFT_PUBLIC_URL", "http://localhost:8000")

app = FastAPI(
    title="SHIFT Labour Demand Index API",
    description=("Public margin of the SHIFT Labour Demand Index 2024-2026 (Edition 1): how "
                 "advertised job demand changed for 23 kinds of work across 24 European-plus "
                 "markets. Counts job advertisements (not hires/wages). Author: Jose Covas. "
                 "CC BY 4.0. DOI: 10.5281/zenodo.22346056. Paid detail at https://shiftindex.org/."),
    version="1.0.0",
    servers=[{"url": PUBLIC_URL}],
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET"], allow_headers=["*"])


@app.get("/about", operation_id="getAbout", summary="About SHIFT: coverage, author, DOI, how to cite")
def about():
    return D.ABOUT


@app.get("/occupations", operation_id="listOccupations",
         summary="List all 23 kinds of work with direction and markets where postings fell")
def occupations():
    return D.list_payload()


@app.get("/headline", operation_id="getHeadline",
         summary="Headline: which kinds of work saw advertised demand fall worldwide")
def headline():
    return D.headline_payload()


@app.get("/occupation/{occupation}", operation_id="getOccupation",
         summary="SHIFT reading for one kind of work (label, key, or substring)")
def occupation(occupation: str):
    r = D.match(occupation)
    if not r:
        raise HTTPException(status_code=404, detail=(
            f"No single SHIFT occupation matched '{occupation}'. "
            "GET /occupations to see the 23 available kinds of work."))
    return D.occupation_payload(r)


@app.get("/", include_in_schema=False)
def root():
    return {"service": "SHIFT Labour Demand Index API", "docs": "/docs",
            "openapi": "/openapi.json", "source": D.SITE, "citation": D.CITATION}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
