"""
DataForSEO Audit Script
Usage: python dataforseo_audit.py --domain example.com --markets "United States,India"

Pulls:
- Domain rank overview (per market)
- Top 50 ranked keywords (per market)
- Top 15 pages by organic traffic
- Organic competitors
- Keyword overview for custom keyword lists
"""

import requests
import json
import argparse
import os
from base64 import b64encode

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
    if task["status_code"] != 20000:
        print(f"  ERROR [{endpoint}]: {task['status_message']}")
        return None
    return task["result"]

# --- 1. Domain Rank Overview ---
def domain_rank_overview(domain, market="United States", lang="en"):
    print(f"\n[1] Domain Rank Overview — {market}")
    result = post("dataforseo_labs/google/domain_rank_overview/live", [
        {"target": domain, "location_name": market, "language_code": lang}
    ])
    if not result:
        return
    m = result[0]["items"][0]["metrics"]["organic"]
    print(f"  Keywords ranking: {m['count']}")
    print(f"  Est. monthly traffic (ETV): {round(m['etv'], 1)}")
    print(f"  Est. traffic value: ${round(m['estimated_paid_traffic_cost'], 0):,.0f}/mo")
    print(f"  Top 10: {m['pos_1'] + m['pos_2_3'] + m['pos_4_10']}")
    print(f"  Momentum — New: {m['is_new']}  Up: {m['is_up']}  Down: {m['is_down']}  Lost: {m['is_lost']}")

# --- 2. Ranked Keywords ---
def ranked_keywords(domain, market="United States", lang="en", limit=50):
    print(f"\n[2] Top Ranked Keywords — {market}")
    result = post("dataforseo_labs/google/ranked_keywords/live", [
        {
            "target": domain,
            "location_name": market,
            "language_code": lang,
            "limit": limit,
            "order_by": ["keyword_data.keyword_info.search_volume,desc"]
        }
    ])
    if not result:
        return
    items = result[0]["items"]
    print(f"  {'Keyword':<50} {'Vol':>8} {'Rank':>6} {'CPC':>7} {'KD':>5}")
    print("  " + "-" * 80)
    for item in items:
        kw = item["keyword_data"]["keyword"]
        vol = item["keyword_data"]["keyword_info"].get("search_volume") or 0
        cpc = item["keyword_data"]["keyword_info"].get("cpc") or 0
        kd = item["keyword_data"]["keyword_properties"].get("keyword_difficulty") or 0
        rank = item["ranked_serp_element"]["serp_item"].get("rank_group") or 0
        url = item["ranked_serp_element"]["serp_item"].get("relative_url", "")
        print(f"  {kw:<50} {vol:>8,} {rank:>6} {cpc:>7.2f} {kd:>5}  {url}")

# --- 3. Top Pages ---
def top_pages(domain, market="United States", lang="en", limit=15):
    print(f"\n[3] Top Pages by Organic Traffic — {market}")
    result = post("dataforseo_labs/google/relevant_pages/live", [
        {
            "target": domain,
            "location_name": market,
            "language_code": lang,
            "limit": limit,
            "order_by": ["metrics.organic.etv,desc"]
        }
    ])
    if not result:
        return
    items = result[0]["items"]
    print(f"  {'Page':<65} {'KWs':>5} {'ETV':>8} {'Top10':>6}")
    print("  " + "-" * 90)
    for item in items:
        url = item["page_address"].replace(f"https://www.{domain}", "").replace(f"https://{domain}", "") or "/"
        m = item["metrics"]["organic"]
        kws = m["count"]
        etv = round(m["etv"], 1)
        top10 = m["pos_1"] + m["pos_2_3"] + m["pos_4_10"]
        print(f"  {url:<65} {kws:>5} {etv:>8} {top10:>6}")

# --- 4. Competitors ---
def competitors(domain, market="United States", lang="en", limit=10):
    print(f"\n[4] Organic Competitors — {market}")
    result = post("dataforseo_labs/google/competitors_domain/live", [
        {
            "target": domain,
            "location_name": market,
            "language_code": lang,
            "limit": limit,
            "order_by": ["intersections,desc"]
        }
    ])
    if not result:
        return
    items = result[0]["items"]
    print(f"  {'Domain':<40} {'Shared KWs':>12} {'Avg Pos':>9}")
    print("  " + "-" * 65)
    for item in items:
        if item["domain"] == domain:
            continue
        print(f"  {item['domain']:<40} {item['intersections']:>12,} {round(item['avg_position'], 1):>9}")

# --- 5. Keyword Overview ---
def keyword_overview(keywords, market="United States", lang="en"):
    print(f"\n[5] Keyword Overview — {market}")
    result = post("dataforseo_labs/google/keyword_overview/live", [
        {"keywords": keywords, "location_name": market, "language_code": lang}
    ])
    if not result:
        return
    items = result[0]["items"]
    print(f"  {'Keyword':<50} {'Vol':>8} {'CPC':>7} {'KD':>5} {'Intent':<15}")
    print("  " + "-" * 90)
    for item in sorted(items, key=lambda x: x.get("keyword_info", {}).get("search_volume") or 0, reverse=True):
        kw = item["keyword"]
        vol = item.get("keyword_info", {}).get("search_volume") or 0
        cpc = item.get("keyword_info", {}).get("cpc") or 0
        kd = item.get("keyword_properties", {}).get("keyword_difficulty") or 0
        intent = item.get("search_intent_info", {}).get("main_intent", "") or ""
        if vol > 0:
            print(f"  {kw:<50} {vol:>8,} {cpc:>7.2f} {kd:>5} {intent:<15}")

# --- Main ---
def main():
    parser = argparse.ArgumentParser(description="DataForSEO Audit")
    parser.add_argument("--domain", required=True, help="Domain to audit (e.g. workongrid.com)")
    parser.add_argument("--markets", default="United States,India", help="Comma-separated markets")
    parser.add_argument("--keywords", default="", help="Comma-separated keywords for keyword overview")
    parser.add_argument("--limit", type=int, default=50, help="Max keywords to return")
    args = parser.parse_args()

    markets = [m.strip() for m in args.markets.split(",")]

    print(f"\n{'='*60}")
    print(f"  DataForSEO Audit: {args.domain}")
    print(f"  Markets: {', '.join(markets)}")
    print(f"{'='*60}")

    for market in markets:
        domain_rank_overview(args.domain, market)
        ranked_keywords(args.domain, market, limit=args.limit)
        top_pages(args.domain, market)

    # Competitors — primary market only
    competitors(args.domain, markets[0])

    # Optional keyword overview
    if args.keywords:
        kw_list = [k.strip() for k in args.keywords.split(",")]
        for market in markets:
            keyword_overview(kw_list, market)

    print(f"\n{'='*60}")
    print("  Audit complete.")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
