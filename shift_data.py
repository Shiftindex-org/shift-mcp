"""
SHIFT Labour Demand Index (Edition 1) — shared public-margin data + logic.

Used by both shift_mcp_server.py (MCP) and shift_api.py (REST/OpenAPI).

PUBLIC LAYER ONLY: direction + how many markets postings fell in. No SHIFT Pull
magnitude, no occupation x market matrix (that is the paid product at shiftindex.org).

Cite: Covas, J. (2026). SHIFT Labour Demand Index 2024-2026 (Edition 1) [Data set].
SHIFT Research. https://doi.org/10.5281/zenodo.22346056
"""

import csv
import io

_CSV = """occupation_key,occupation_label,ai_exposure_class,world_count_change,direction_status,markets_visible,markets_with_fewer_postings
accounting_finance,Accounting & bookkeeping,AI-exposed,rose,published (robust),22,7
admin_clerical,Administrative & clerical,AI-exposed,rose,not published,20,3
agriculture,Agriculture & landscaping,AI-resilient,rose,published (robust),8,1
sales_b2b,B2B / field sales,AI-exposed,rose,published (robust),21,10
personal_services,"Cleaning, food & security",AI-resilient,rose,published (robust),17,0
construction,Construction & building trades,AI-resilient,rose,published (robust),12,1
customer_support,Customer support & call center,AI-exposed,rose,published (robust),19,6
data_analytics,Data analysts & entry,AI-exposed,fell,published (robust),21,8
transport_driver,Drivers & transport,AI-resilient,rose,published (robust),16,1
electrical,Electricians,AI-resilient,rose,not published,14,3
legal_support,Legal support,AI-exposed,rose,not published,8,2
marketing_content,"Marketing, content & translation",AI-exposed,fell,published (robust),18,13
mechanic_maintenance,Mechanics & maintenance techs,AI-resilient,rose,published (sensitive),18,4
healthcare_frontline,Nurses & care workers,AI-resilient,rose,published (robust),14,1
healthcare_physicians,Physicians & doctors,AI-resilient,rose,published (robust),11,1
plumbing,Plumbers & pipefitters,AI-resilient,rose,published (robust),7,1
production_operator,Production & machine operators,AI-resilient,rose,published (robust),12,2
real_estate_broker,Real-estate agents/brokers,AI-resilient,rose,not published,9,4
retail_sales,Retail & shop assistants,AI-resilient,rose,published (robust),22,1
software_dev,Software developers,AI-exposed,fell,published (robust),24,21
teaching,Teachers,AI-resilient,rose,published (robust),17,2
warehouse_logistics,Warehouse & logistics,AI-resilient,rose,published (robust),11,1
welding_metal,Welders & metalworkers,AI-resilient,rose,published (sensitive),13,3
"""

ROWS = []
for _r in csv.DictReader(io.StringIO(_CSV)):
    _r["markets_visible"] = int(_r["markets_visible"])
    _r["markets_with_fewer_postings"] = int(_r["markets_with_fewer_postings"])
    ROWS.append(_r)

CITATION = ("Covas, J. (2026). SHIFT Labour Demand Index 2024-2026 (Edition 1) "
            "[Data set]. SHIFT Research. https://doi.org/10.5281/zenodo.22346056")
SITE = "https://shiftindex.org/"
PAID_NOTE = ("Per-market breakdown and the SHIFT Pull magnitude (how far each occupation "
             "moved relative to its market) are the paid product at " + SITE)

ABOUT = {
    "name": "SHIFT Labour Demand Index 2024-2026 (Edition 1)",
    "what_it_measures": ("Change in advertised (online job-posting) demand for 23 kinds of "
                         "work across 24 markets, comparing the 12 months to June 2024 with "
                         "the 12 months to June 2026. It counts job advertisements, not hires, "
                         "employment, or wages."),
    "coverage": {"kinds_of_work": 23, "markets": 24, "languages": 9,
                 "ads_base_window_to_Jun2024": 4241295, "ads_recent_window_to_Jun2026": 9323023},
    "author": "José Covas", "publisher": "SHIFT Research",
    "orcid": "https://orcid.org/0009-0000-2298-0626",
    "wikidata": "https://www.wikidata.org/wiki/Q141324073",
    "license": "CC BY 4.0", "doi": "https://doi.org/10.5281/zenodo.22346056",
    "site": SITE, "citation": CITATION, "note": PAID_NOTE,
    "public_layer_only": ("This serves only the public occupation margin. The occupation x "
                          "market matrix and SHIFT Pull magnitude are paid."),
}


def match(occupation: str):
    """Resolve a label/key/substring to one row, or None (0 or >1 matches)."""
    q = (occupation or "").strip().lower()
    if not q:
        return None
    for r in ROWS:
        if q == r["occupation_key"].lower() or q == r["occupation_label"].lower():
            return r
    cand = [r for r in ROWS if q in r["occupation_label"].lower() or q in r["occupation_key"].lower()]
    return cand[0] if len(cand) == 1 else None


def describe(r: dict) -> str:
    moved = "rose" if r["world_count_change"] == "rose" else "fell"
    ds = r["direction_status"]
    if ds.startswith("published"):
        conf = "robust" if "robust" in ds else "sensitive"
        dir_line = (f"SHIFT publishes a {conf} direction for this occupation relative to its "
                    f"market (the magnitude/SHIFT Pull is in the paid product).")
    else:
        dir_line = ("SHIFT does NOT publish a market-relative direction for this occupation "
                    "(the robustness checks disagreed), so no 'ahead/behind' claim should be made.")
    return (f"{r['occupation_label']} ({r['ai_exposure_class']}). "
            f"Worldwide advertised postings {moved} between the year to Jun-2024 and the year to Jun-2026. "
            f"Postings fell in {r['markets_with_fewer_postings']} of the "
            f"{r['markets_visible']} markets where this work is visible. {dir_line}")


def occupation_payload(r: dict) -> dict:
    return {"occupation": r["occupation_label"], "key": r["occupation_key"],
            "ai_exposure_class": r["ai_exposure_class"],
            "worldwide_count_change": r["world_count_change"],
            "markets_visible": r["markets_visible"],
            "markets_with_fewer_postings": r["markets_with_fewer_postings"],
            "direction_status": r["direction_status"],
            "summary": describe(r),
            "citation": CITATION, "source": SITE, "note": PAID_NOTE}


def list_payload() -> dict:
    items = [{k: r[k] for k in ("occupation_label", "occupation_key", "ai_exposure_class",
                                "world_count_change", "markets_visible",
                                "markets_with_fewer_postings", "direction_status")} for r in ROWS]
    return {"edition": "SHIFT Labour Demand Index 2024-2026 (Edition 1)",
            "count": len(items), "occupations": items,
            "citation": CITATION, "source": SITE, "note": PAID_NOTE}


def headline_payload() -> dict:
    fell = [r["occupation_label"] for r in ROWS if r["world_count_change"] == "fell"]
    sw = next(r for r in ROWS if r["occupation_key"] == "software_dev")
    return {
        "worldwide_declines": fell,
        "detail": {"note": "These three AI-exposed kinds of work saw worldwide advertised postings fall.",
                   "software_developers": f"fell in {sw['markets_with_fewer_postings']} of {sw['markets_visible']} markets"},
        "pattern": ("AI-exposed office/knowledge work (software developers, data analysts & entry, "
                    "marketing/content/translation) is where advertised demand fell worldwide; "
                    "AI-resilient manual, care and skilled-trade work broadly held up or grew."),
        "robustness": "Edition 1 publishes 17 robust + 2 sensitive directions; 4 are not published.",
        "caveat": ("'rose/fell' here is the change in advertised postings, not employment or wages, "
                   "and not a causal AI claim. Market-relative magnitude (SHIFT Pull) is paid."),
        "citation": CITATION, "source": SITE,
    }
