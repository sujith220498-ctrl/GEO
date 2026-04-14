"""
SEO Audit Script — Full Pipeline
Usage:
  python tools/seo_audit_full.py --domain exotel.com --market "India" --competitors "myoperator.com,ozonetel.com,knowlarity.com"

Runs:
  1. Domain overview (organic + paid)
  2. Top 30 pages by organic traffic + keywords per page
  3. Competitor organic/paid overview
  4. Keywords Exotel is losing to each competitor (domain intersection)

Saves output to: audits/{domain}/{YYYY-MM-DD}/seo-benchmark.md
"""

import requests
import argparse
import os
from base64 import b64encode
from datetime import date

# --- Credentials ---
USERNAME = os.getenv("DATAFORSEO_USERNAME", "")
PASSWORD = os.getenv("DATAFORSEO_PASSWORD", "")

def auth_header():
    creds = b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
    return {"Authorization": f"Basic {creds}", "Content-Type": "application/json"}

def post(endpoint, payload):
    url = f"https://api.dataforseo.com/v3/{endpoint}"
    r = requests.post(url, headers=auth_header(), json=payload)
    r.raise_for_status()
    data = r.json()
    task = data["tasks"][0]
    if task["status_code"] != 20000 or not task.get("result"):
        print(f"  ERROR [{endpoint}]: {task.get('status_message','')}")
        return None
    return task["result"]

# --- Step 1: Domain Overview ---
def domain_overview(domain, market, lang="en"):
    print(f"[1] Domain overview — {domain}")
    result = post("dataforseo_labs/google/domain_rank_overview/live", [
        {"target": domain, "location_name": market, "language_code": lang}
    ])
    if not result:
        return None
    items = result[0].get("items", [])
    if not items:
        return None
    return items[0]["metrics"]

# --- Step 2: Top Pages + Keywords ---
def top_pages_with_keywords(domain, market, lang="en", pages_limit=30, kw_limit=500):
    print(f"[2] Top {pages_limit} pages + keywords — {domain}")
    pages_result = post("dataforseo_labs/google/relevant_pages/live", [
        {"target": domain, "location_name": market, "language_code": lang,
         "limit": pages_limit, "order_by": ["metrics.organic.etv,desc"]}
    ])
    kw_result = post("dataforseo_labs/google/ranked_keywords/live", [
        {"target": domain, "location_name": market, "language_code": lang,
         "limit": kw_limit, "order_by": ["keyword_data.keyword_info.search_volume,desc"]}
    ])

    kw_by_page = {}
    if kw_result:
        for item in kw_result[0]["items"]:
            rel_url = item["ranked_serp_element"]["serp_item"].get("relative_url", "/") or "/"
            kw = item["keyword_data"]["keyword"]
            vol = item["keyword_data"]["keyword_info"].get("search_volume") or 0
            rank = item["ranked_serp_element"]["serp_item"].get("rank_group") or 0
            kw_by_page.setdefault(rel_url, []).append((kw, vol, rank))

    pages = pages_result[0]["items"] if pages_result else []
    return pages, kw_by_page

# --- Step 3: Competitor Overview ---
def competitor_overview(domains, market, lang="en"):
    print(f"[3] Competitor overview — {len(domains)} domains")
    results = {}
    for domain in domains:
        result = post("dataforseo_labs/google/domain_rank_overview/live", [
            {"target": domain, "location_name": market, "language_code": lang}
        ])
        if result:
            items = result[0].get("items", [])
            if items:
                results[domain] = items[0]["metrics"]
    return results

# --- Step 4: Domain Intersection (losing keywords) ---
def losing_keywords(target, competitor, market, lang="en", limit=200):
    result = post("dataforseo_labs/google/domain_intersection/live", [
        {"target1": target, "target2": competitor, "location_name": market,
         "language_code": lang, "limit": limit,
         "order_by": ["keyword_data.keyword_info.search_volume,desc"]}
    ])
    if not result:
        return [], 0
    items = result[0].get("items", [])
    total_shared = len(items)
    losing = []
    for item in items:
        kw  = item["keyword_data"]["keyword"]
        vol = item["keyword_data"]["keyword_info"].get("search_volume") or 0
        r1  = item["first_domain_serp_element"].get("rank_group") or 999
        r2  = item["second_domain_serp_element"].get("rank_group") or 999
        if r2 < r1 and vol > 0:
            losing.append((kw, vol, r1, r2))
    losing.sort(key=lambda x: x[1], reverse=True)
    return losing, total_shared

# --- Build Markdown Report ---
def build_report(domain, market, overview, pages, kw_by_page, comp_overview, competitors_list, comp_losing):
    lines = []
    lines.append(f"# SEO Benchmark — {domain}")
    lines.append(f"**Date:** {date.today().isoformat()}")
    lines.append(f"**Market:** {market}")
    lines.append(f"**Tool:** DataForSEO API via tools/seo_audit_full.py\n")

    # Step 1
    lines.append("---\n## Step 1 — Domain Overview\n")
    if overview:
        org  = overview.get("organic", {})
        paid = overview.get("paid", {})
        lines.append("| Metric | Value |")
        lines.append("|---|---|")
        lines.append(f"| Organic Keywords | {org.get('count', 0):,} |")
        lines.append(f"| Organic ETV | {round(org.get('etv', 0)):,} |")
        top10 = org.get('pos_1', 0) + org.get('pos_2_3', 0) + org.get('pos_4_10', 0)
        lines.append(f"| Top-10 Keywords | {top10:,} |")
        lines.append(f"| Paid Keywords | {paid.get('count', 0):,} |")
        lines.append(f"| Paid ETV | {round(paid.get('etv', 0)):,} |")

    # Step 2
    lines.append("\n---\n## Step 2 — Top Pages by Organic Traffic\n")
    lines.append("| # | Page | ETV | KWs | Top-10 |")
    lines.append("|---|------|-----|-----|--------|")
    for i, item in enumerate(pages, 1):
        raw_url = item["page_address"]
        rel_url = raw_url.replace(f"https://www.{domain}", "").replace(f"https://{domain}", "") or "/"
        m = item["metrics"]["organic"]
        etv   = round(m["etv"], 1)
        kws   = m["count"]
        top10 = m["pos_1"] + m["pos_2_3"] + m["pos_4_10"]
        lines.append(f"| {i} | {rel_url} | {etv:,.1f} | {kws} | {top10} |")

    lines.append("\n### Keywords per Page\n")
    for i, item in enumerate(pages, 1):
        raw_url = item["page_address"]
        rel_url = raw_url.replace(f"https://www.{domain}", "").replace(f"https://{domain}", "") or "/"
        m = item["metrics"]["organic"]
        etv   = round(m["etv"], 1)
        top10 = m["pos_1"] + m["pos_2_3"] + m["pos_4_10"]
        lines.append(f"#### [{i:02d}] {rel_url}")
        lines.append(f"ETV: {etv:,} | Top-10: {top10} | Total KWs: {m['count']}\n")
        page_kws = sorted(kw_by_page.get(rel_url, []), key=lambda x: x[2])
        if page_kws:
            lines.append("| Keyword | Volume | Rank |")
            lines.append("|---------|--------|------|")
            for kw, vol, rank in page_kws[:15]:
                lines.append(f"| {kw} | {vol:,} | {rank} |")
        else:
            lines.append("_(no keywords matched)_")
        lines.append("")

    # Step 3
    lines.append("---\n## Step 3 — Competitor Overview\n")
    lines.append("| Domain | Org KWs | Org ETV | Top-10 | Paid KWs | Paid ETV |")
    lines.append("|---|---|---|---|---|---|")
    if overview:
        org  = overview.get("organic", {})
        paid = overview.get("paid", {})
        top10 = org.get('pos_1', 0) + org.get('pos_2_3', 0) + org.get('pos_4_10', 0)
        lines.append(f"| **{domain}** | {org.get('count',0):,} | {round(org.get('etv',0)):,} | {top10:,} | {paid.get('count',0):,} | {round(paid.get('etv',0)):,} |")
    for comp_domain, metrics in comp_overview.items():
        org  = metrics.get("organic", {})
        paid = metrics.get("paid", {})
        top10 = org.get('pos_1', 0) + org.get('pos_2_3', 0) + org.get('pos_4_10', 0)
        lines.append(f"| {comp_domain} | {org.get('count',0):,} | {round(org.get('etv',0)):,} | {top10:,} | {paid.get('count',0):,} | {round(paid.get('etv',0)):,} |")

    # Step 4
    lines.append("\n---\n## Step 4 — Keywords Losing to Competitors\n")
    for comp_domain, (losing, total_shared) in comp_losing.items():
        lines.append(f"### vs {comp_domain} — {len(losing)} losing keywords (of {total_shared} shared)\n")
        if losing:
            lines.append("| Keyword | Volume | Target Rank | Competitor Rank |")
            lines.append("|---------|--------|-------------|-----------------|")
            for kw, vol, r1, r2 in losing[:30]:
                lines.append(f"| {kw} | {vol:,} | {r1} | {r2} |")
        else:
            lines.append("_No losing keywords found._")
        lines.append("")

    return "\n".join(lines)

# --- Main ---
def main():
    parser = argparse.ArgumentParser(description="Full SEO Audit")
    parser.add_argument("--domain",      required=True, help="Domain to audit (e.g. exotel.com)")
    parser.add_argument("--market",      default="India", help="Market (default: India)")
    parser.add_argument("--competitors", default="", help="Comma-separated competitor domains")
    args = parser.parse_args()

    domain      = args.domain
    market      = args.market
    competitors = [c.strip() for c in args.competitors.split(",") if c.strip()]

    print(f"\n{'='*60}")
    print(f"  SEO Audit: {domain} | {market}")
    print(f"{'='*60}\n")

    overview              = domain_overview(domain, market)
    pages, kw_by_page     = top_pages_with_keywords(domain, market)
    comp_overview         = competitor_overview(competitors, market) if competitors else {}
    comp_losing           = {}
    if competitors:
        print(f"[4] Domain intersection vs {len(competitors)} competitors")
        for comp in competitors:
            print(f"    vs {comp}...")
            losing, total = losing_keywords(domain, comp, market)
            comp_losing[comp] = (losing, total)

    report = build_report(domain, market, overview, pages, kw_by_page, comp_overview, competitors, comp_losing)

    # Save
    out_dir = f"audits/{domain.replace('.', '-')}/{date.today().isoformat()}"
    os.makedirs(out_dir, exist_ok=True)
    out_path = f"{out_dir}/seo-benchmark.md"
    with open(out_path, "w") as f:
        f.write(report)

    print(f"\nSaved: {out_path}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
