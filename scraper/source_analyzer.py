"""
iamshoemaker.com — Source Analyzer
Ren Shoku 匠 | Where Craftsmanship Meets Intelligence

Reverse-engineers leathernews.org to discover their primary
news sources by analyzing the time gap between leathernews
posts and the original articles they link to.

Run manually when you want to discover new RSS sources:
    python3 source_analyzer.py

Outputs ranked_sources.json to the project root (../).
Add high-ranking sources with RSS feeds to config.py SOURCES.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from dateutil import parser as dateparser
from urllib.parse import urlparse
import feedparser
import json
import time
import re
import os
import sys

# ─── CONFIGURATION ────────────────────────────────────────────────────────

TARGET_SITES = [
    "https://leathernews.org/news/",
    "https://leathernews.org/category/footwear-news/",
]

OUTPUT_FILE   = "../ranked_sources.json"
MAX_PAGES     = 5
REQUEST_DELAY = 2  # seconds between requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; "
        "RenShokuBot/1.0; Research tool)"
    )
}

SKIP_DOMAINS = [
    "facebook.com", "twitter.com", "x.com",
    "linkedin.com", "instagram.com",
    "youtube.com", "google.com",
    "whatsapp.com", "wikipedia.org",
    "leathernews.org",
]


# ─── FUNCTION 1: Scrape leathernews articles ──────────────────────────────

def scrape_leathernews_articles(max_pages=MAX_PAGES):
    """
    Scrape leathernews.org article listings.
    Returns list of dicts:
      {title, url, leathernews_time, outbound_url}
    """
    articles = []

    for site_url in TARGET_SITES:
        print(f"Scraping: {site_url}")

        for page in range(1, max_pages + 1):
            url = site_url
            if page > 1:
                url = f"{site_url}page/{page}/"

            try:
                resp = requests.get(
                    url, headers=HEADERS, timeout=10
                )

                if resp.status_code != 200:
                    print(f"  Page {page}: HTTP {resp.status_code}, stopping")
                    break

                soup = BeautifulSoup(resp.text, "html.parser")

                # WordPress standard article structure
                posts = soup.find_all("article")
                if not posts:
                    posts = soup.find_all(
                        class_=re.compile(
                            r"post|article|entry", re.I
                        )
                    )
                if not posts:
                    posts = soup.find_all(["h2", "h3"])

                found = 0
                for post in posts:
                    link = post.find("a")
                    if not link:
                        continue

                    article_url = link.get("href", "")
                    if not article_url:
                        continue

                    # Skip category / tag / pagination links
                    skip_patterns = [
                        "leathernews.org/category",
                        "leathernews.org/tag",
                        "leathernews.org/page",
                        "#",
                    ]
                    if any(p in article_url for p in skip_patterns):
                        continue

                    title = link.get_text(strip=True)
                    if len(title) < 10:
                        continue

                    # Get publish time from <time datetime="...">
                    time_elem = post.find("time")
                    pub_time = None
                    if time_elem:
                        dt_attr = time_elem.get("datetime")
                        if dt_attr:
                            try:
                                pub_time = dateparser.parse(dt_attr)
                            except Exception:
                                pass

                    articles.append({
                        "title":             title,
                        "url":               article_url,
                        "leathernews_time":  pub_time,
                        "outbound_url":      None,
                        "original_time":     None,
                        "delta_mins":        None,
                    })
                    found += 1

                print(f"  Page {page}: found {found} articles")

                if found == 0:
                    break

                time.sleep(REQUEST_DELAY)

            except Exception as e:
                print(f"  Error on page {page}: {e}")
                break

    print(f"\nTotal articles scraped: {len(articles)}")
    return articles


# ─── FUNCTION 2: Get outbound URL ─────────────────────────────────────────

def extract_outbound_url(article_url):
    """
    Fetch the leathernews article page.
    Find the primary outbound source link
    (the publication they're reporting on).
    Returns URL string or None.
    """
    try:
        resp = requests.get(
            article_url, headers=HEADERS, timeout=10
        )
        soup = BeautifulSoup(resp.text, "html.parser")

        # Find article body
        content = (
            soup.find(class_=re.compile(
                r"entry-content|post-content|article-content|content",
                re.I,
            ))
            or soup.find("article")
        )

        if not content:
            return None

        # Collect all external links
        external_links = []
        for a in content.find_all("a", href=True):
            href = a["href"]
            if href.startswith("http") and \
               "leathernews.org" not in href:
                domain = urlparse(href).netloc.replace("www.", "")
                if not any(s in domain for s in SKIP_DOMAINS):
                    external_links.append(href)

        # The last substantial external link is usually the source
        for link in reversed(external_links):
            return link

        return None

    except Exception as e:
        print(f"  Error extracting outbound URL: {e}")
        return None


# ─── FUNCTION 3: Get original publish time ────────────────────────────────

def get_original_publish_time(url):
    """
    Try multiple methods to get the article's
    original publish timestamp from the source page.
    Returns datetime (UTC-aware) or None.
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        text = resp.text

        # Method 1: JSON-LD schema.org
        for script in soup.find_all(
            "script", type="application/ld+json"
        ):
            try:
                data = json.loads(script.string or "")
                if isinstance(data, list):
                    data = data[0]
                date_str = data.get("datePublished") or \
                           data.get("dateCreated")
                if date_str:
                    return dateparser.parse(date_str)
            except Exception:
                continue

        # Method 2: OpenGraph article:published_time
        og = soup.find("meta", property="article:published_time")
        if og and og.get("content"):
            try:
                return dateparser.parse(og["content"])
            except Exception:
                pass

        # Method 3: Various <meta> name/itemprop tags
        meta_attrs = [
            {"name": "publish-date"},
            {"name": "date"},
            {"name": "pubdate"},
            {"name": "publication_date"},
            {"itemprop": "datePublished"},
            {"name": "dc.date.issued"},
        ]
        for attrs in meta_attrs:
            meta = soup.find("meta", attrs=attrs)
            if meta and meta.get("content"):
                try:
                    return dateparser.parse(meta["content"])
                except Exception:
                    pass

        # Method 4: <time datetime="...">
        time_elem = soup.find("time", attrs={"datetime": True})
        if time_elem:
            try:
                return dateparser.parse(time_elem["datetime"])
            except Exception:
                pass

        # Method 5: Regex fallback on raw HTML
        date_patterns = [
            r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})",
            r"(\w+ \d{1,2},? \d{4})",
            r"(\d{1,2}/\d{1,2}/\d{4})",
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    return dateparser.parse(match.group(1))
                except Exception:
                    pass

        return None

    except Exception:
        return None


# ─── FUNCTION 4: Calculate time delta ─────────────────────────────────────

def calculate_delta(leathernews_time, original_time):
    """
    Calculate minutes between original publication
    and leathernews post.
    Returns int (minutes) or None.
    Only accepts deltas in the range 0–72 hours.
    """
    if not leathernews_time or not original_time:
        return None

    try:
        # Ensure both are timezone-aware
        if leathernews_time.tzinfo is None:
            leathernews_time = leathernews_time.replace(
                tzinfo=timezone.utc
            )
        if original_time.tzinfo is None:
            original_time = original_time.replace(
                tzinfo=timezone.utc
            )

        delta_mins = int(
            (leathernews_time - original_time).total_seconds() / 60
        )

        # Sanity check: 0 to 72 hours
        if 0 <= delta_mins <= 4320:
            return delta_mins

        return None

    except Exception:
        return None


# ─── FUNCTION 5: Discover RSS feed ────────────────────────────────────────

def discover_rss(domain):
    """
    Try common RSS feed paths for a domain.
    Returns working RSS URL or None.
    """
    common_paths = [
        "/feed",
        "/feed/",
        "/rss",
        "/rss/",
        "/rss.xml",
        "/feed.xml",
        "/atom.xml",
        "/feeds/posts/default",
        "/index.xml",
        "/news/feed",
        "/news/rss",
    ]

    base = f"https://{domain}"

    for path in common_paths:
        url = base + path
        try:
            resp = requests.get(
                url, headers=HEADERS, timeout=5
            )
            if resp.status_code != 200:
                continue

            content_type = resp.headers.get("Content-Type", "")
            if any(t in content_type for t in ["xml", "rss", "atom"]):
                # Verify with feedparser
                feed = feedparser.parse(url)
                if feed.entries:
                    return url

        except Exception:
            continue

    return None


# ─── FUNCTION 6: Analyze sources ──────────────────────────────────────────

def analyze_sources(articles_with_data):
    """
    Group processed articles by source domain.
    Calculate per-source frequency and delta metrics.
    Returns list of source dicts, sorted by reliability.
    """
    source_map = {}

    for article in articles_with_data:
        outbound = article.get("outbound_url")
        if not outbound:
            continue

        domain = urlparse(outbound).netloc.replace("www.", "")
        if not domain:
            continue

        if domain not in source_map:
            source_map[domain] = {
                "domain":   domain,
                "full_url": f"https://{domain}",
                "articles": [],
                "deltas":   [],
            }

        source_map[domain]["articles"].append(article)
        if article.get("delta_mins") is not None:
            source_map[domain]["deltas"].append(
                article["delta_mins"]
            )

    if not source_map:
        return []

    max_count = max(
        len(v["articles"]) for v in source_map.values()
    )

    sources = []
    for domain, data in source_map.items():
        count  = len(data["articles"])
        deltas = data["deltas"]

        avg_delta = int(sum(deltas) / len(deltas)) if deltas else None
        min_delta = min(deltas) if deltas else None

        reliability = round((count / max_count) * 10, 1)
        per_week    = round(count / 4.3, 1)  # assumes ~30 days data

        sources.append({
            "domain":            domain,
            "full_url":          data["full_url"],
            "articles_found":    count,
            "avg_delta_mins":    avg_delta,
            "min_delta_mins":    min_delta,
            "articles_per_week": per_week,
            "reliability_score": reliability,
            "rss_feed_url":      None,
            "rank":              0,
        })

    # Sort: reliability descending, then avg delta ascending
    sources.sort(
        key=lambda x: (
            -x["reliability_score"],
            x["avg_delta_mins"] or 9999,
        )
    )

    for i, source in enumerate(sources):
        source["rank"] = i + 1

    return sources


# ─── FUNCTION 7: Save results ──────────────────────────────────────────────

def save_ranked_sources(sources):
    output = {
        "analyzed_date":       datetime.now(timezone.utc).isoformat(),
        "total_sources_found": len(sources),
        "sources":             sources,
    }

    output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        OUTPUT_FILE,
    )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to {output_path}")


# ─── FUNCTION 8: Print results table ──────────────────────────────────────

def print_results_table(sources):
    print("\n" + "=" * 70)
    print("TOP SOURCES RANKED BY RELIABILITY")
    print("=" * 70)
    print(
        f"{'Rank':<5} {'Domain':<30} "
        f"{'Articles':<10} {'Avg Delta':<12} "
        f"{'Score':<8} {'RSS'}"
    )
    print("-" * 70)

    for s in sources[:15]:
        rss_flag = "Yes" if s["rss_feed_url"] else "No"
        delta    = f"{s['avg_delta_mins']}m" if s["avg_delta_mins"] else "N/A"
        print(
            f"{s['rank']:<5} "
            f"{s['domain']:<30} "
            f"{s['articles_found']:<10} "
            f"{delta:<12} "
            f"{s['reliability_score']:<8} "
            f"{rss_flag}"
        )


# ─── MAIN ─────────────────────────────────────────────────────────────────

def main():
    print("=" * 50)
    print("REN SHOKU — Source Analyzer")
    print("Reverse-engineering leathernews.org")
    print("=" * 50)

    # Step 1: Scrape article listings
    articles = scrape_leathernews_articles()

    if not articles:
        print("No articles found. Exiting.")
        sys.exit(1)

    # Step 2: For each article, get outbound URL + original timestamp
    limit = min(50, len(articles))
    print(f"\nAnalyzing {limit} articles for source patterns...")

    for i, article in enumerate(articles[:limit]):
        print(f"[{i+1}/{limit}] {article['title'][:55]}")

        if not article["url"]:
            continue

        # Get outbound URL from leathernews article body
        outbound = extract_outbound_url(article["url"])
        article["outbound_url"] = outbound

        if outbound:
            # Get original publication time
            orig_time = get_original_publish_time(outbound)
            article["original_time"] = orig_time

            # Calculate time delta
            delta = calculate_delta(
                article["leathernews_time"], orig_time
            )
            article["delta_mins"] = delta

            domain = urlparse(outbound).netloc.replace("www.", "")
            delta_str = f"{delta}m" if delta is not None else "N/A"
            print(f"  → {domain} | delta: {delta_str}")
        else:
            print("  → No outbound URL found")

        time.sleep(REQUEST_DELAY)

    # Step 3: Analyze and rank sources
    print("\nRanking sources by reliability...")
    sources = analyze_sources(articles[:limit])

    if not sources:
        print("No sources identified. Try increasing MAX_PAGES.")
        sys.exit(1)

    # Step 4: Discover RSS feeds for top sources
    print(f"\nDiscovering RSS feeds for top {min(20, len(sources))} sources...")
    for source in sources[:20]:
        domain = source["domain"]
        print(f"  Checking: {domain}")
        rss = discover_rss(domain)
        source["rss_feed_url"] = rss
        if rss:
            print(f"    RSS found: {rss}")
        time.sleep(1)

    # Step 5: Save and display
    save_ranked_sources(sources)
    print_results_table(sources)

    print("\n" + "=" * 50)
    print("Done!")
    print("Review ranked_sources.json")
    print("Add high-scoring sources to config.py SOURCES")
    print("=" * 50)


if __name__ == "__main__":
    main()
