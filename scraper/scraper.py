"""
iamshoemaker.com — News Scraper
Misaki Zuno 造 | Where Craftsmanship Meets Intelligence

Runs 4x/day via GitHub Actions.
Pulls RSS feeds → filters for footwear/leather relevance
→ writes feed.json → pushes to GitHub.

Usage:
    python3 scraper.py

Environment variables required:
    GITHUB_TOKEN  — GitHub personal access token
"""

import feedparser
import requests
from bs4 import BeautifulSoup
import json
import hashlib
import os
import sys
import re
from datetime import datetime, timezone, timedelta
from dateutil import parser as dateparser
import time
from github import Github
from rapidfuzz import fuzz

# Add scraper dir to path so config imports cleanly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    GITHUB_TOKEN,
    GITHUB_REPO, GITHUB_FEED_PATH, GITHUB_BRANCH,
    MAX_ARTICLES, ARTICLES_PER_RUN_MAX,
    ARTICLE_MAX_AGE_DAYS, MIN_RELEVANCE_SCORE,
    SUMMARY_MAX_CHARS, REQUEST_TIMEOUT, RETRY_WAIT_SECONDS,
    SOURCES, PRIMARY_KEYWORDS, BRANDS, CATEGORY_RULES,
)


# ─── LOGGING ──────────────────────────────────────────────────────────────

def log_error(message):
    """Append timestamped error to errors.txt and print."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    try:
        errors_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "errors.txt",
        )
        with open(errors_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass
    print(f"ERROR: {message}")


def log_info(message):
    """Print timestamped info message."""
    timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")


# ─── FUNCTION 1: Load existing feed ──────────────────────────────────────

def load_existing_feed():
    """
    Load current feed.json from project root.
    Returns list of existing article dicts.
    """
    feed_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "feed.json",
    )

    try:
        with open(feed_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        articles = data.get("articles", [])
        log_info(f"Loaded {len(articles)} existing articles from feed.json")
        return articles

    except FileNotFoundError:
        log_info("No existing feed.json found — starting fresh")
        return []

    except json.JSONDecodeError as e:
        log_error(f"feed.json is corrupted ({e}) — starting fresh")
        return []


# ─── FUNCTION 2: Fetch RSS source ─────────────────────────────────────────

def fetch_rss_source(source):
    """
    Fetch and parse an RSS feed.
    Returns list of feedparser entry objects (may be empty).
    """
    try:
        log_info(f"Fetching: {source['name']}")

        feed = feedparser.parse(
            source["rss"],
            request_headers={"User-Agent": "MisakiZunoBot/1.0"},
        )

        # bozo = malformed XML, but entries may still be present
        if feed.bozo and not feed.entries:
            log_error(
                f"RSS parse error for {source['name']}: "
                f"{getattr(feed, 'bozo_exception', 'unknown')}"
            )
            return []

        log_info(f"  Got {len(feed.entries)} entries from {source['name']}")
        return feed.entries

    except Exception as e:
        log_error(f"Failed to fetch {source['name']}: {e}")
        return []


# ─── FUNCTION 3: Parse RSS entry ──────────────────────────────────────────

def parse_entry(entry, source_name, source_domain):
    """
    Extract clean article data from a feedparser entry.
    Returns article dict or None if the entry is invalid.
    """
    try:
        # Title
        title = getattr(entry, "title", "").strip()
        if not title or len(title) < 10:
            return None

        # URL
        url = getattr(entry, "link", "").strip()
        if not url:
            return None

        # Published time
        pub_time = None
        if getattr(entry, "published_parsed", None):
            pub_time = datetime(
                *entry.published_parsed[:6], tzinfo=timezone.utc
            )
        elif getattr(entry, "updated_parsed", None):
            pub_time = datetime(
                *entry.updated_parsed[:6], tzinfo=timezone.utc
            )
        else:
            pub_time = datetime.now(timezone.utc)

        pub_iso = pub_time.isoformat()

        # Summary — strip all HTML tags
        raw_summary = (
            getattr(entry, "summary", "")
            or getattr(entry, "description", "")
            or ""
        )
        soup = BeautifulSoup(raw_summary, "html.parser")
        clean_summary = soup.get_text(separator=" ", strip=True)
        clean_summary = re.sub(r"\s+", " ", clean_summary)
        clean_summary = clean_summary[:SUMMARY_MAX_CHARS]

        return {
            "id":                     generate_id(url),
            "title":                  title,
            "source_name":            source_name,
            "source_domain":          source_domain,
            "source_url":             url,
            "original_publish_time":  pub_iso,
            "scraped_time":           datetime.now(timezone.utc).isoformat(),
            "time_delta_mins":        0,
            "category":               "Retail",
            "brands_mentioned":       [],
            "keywords_matched":       [],
            "relevance_score":        0,
            "summary":                clean_summary,
            "ren_take":               "",
            "image_url":              extract_image(entry),
        }

    except Exception as e:
        log_error(f"Entry parse error: {e}")
        return None


# ─── FUNCTION 4: Extract image URL ────────────────────────────────────────

def extract_image(entry):
    """
    Try to find an image URL in feedparser entry metadata.
    Returns URL string or empty string.
    """
    # media:content
    media_content = getattr(entry, "media_content", [])
    for media in media_content:
        if isinstance(media, dict) and \
           media.get("type", "").startswith("image"):
            return media.get("url", "")

    # enclosures
    for enc in getattr(entry, "enclosures", []):
        if isinstance(enc, dict) and \
           "image" in enc.get("type", ""):
            return enc.get("href", "")

    # links
    for link in getattr(entry, "links", []):
        if isinstance(link, dict) and \
           "image" in link.get("type", ""):
            return link.get("href", "")

    return ""


# ─── FUNCTION 5: Score article relevance ─────────────────────────────────

def score_article(article):
    """
    Score an article for footwear/leather relevance.
    Title matches score higher than summary matches.
    Returns (score: int, matched_keywords: list[str]).
    """
    title_lower   = article["title"].lower()
    summary_lower = article["summary"].lower()
    score   = 0
    matched = set()

    for keyword in PRIMARY_KEYWORDS:
        kw = keyword.lower()
        if kw in title_lower:
            score += 3
            matched.add(keyword)
        elif kw in summary_lower:
            score += 1
            matched.add(keyword)

    for brand in BRANDS:
        brand_lower = brand.lower()
        if brand_lower in title_lower:
            score += 2
        elif brand_lower in summary_lower:
            score += 1

    return score, sorted(matched)


# ─── FUNCTION 6: Categorize article ──────────────────────────────────────

def categorize_article(article):
    """
    Assign category based on article content.
    Checks CATEGORY_RULES in order; returns first match.
    Defaults to 'Retail'.
    """
    text = (article["title"] + " " + article["summary"]).lower()

    for category, keywords in CATEGORY_RULES.items():
        for keyword in keywords:
            if keyword.lower() in text:
                return category

    return "Retail"


# ─── FUNCTION 7: Extract brand mentions ──────────────────────────────────

def extract_brands(article):
    """
    Find whole-word brand mentions in title + summary.
    Returns list of matching brand names.
    """
    text  = article["title"] + " " + article["summary"]
    found = []

    for brand in BRANDS:
        pattern = r"\b" + re.escape(brand) + r"\b"
        if re.search(pattern, text, re.IGNORECASE):
            found.append(brand)

    return found


# ─── FUNCTION 8: Deduplicate ──────────────────────────────────────────────

def is_duplicate(new_article, existing_articles):
    """
    Check whether a new article already exists in the feed.
    Detects both exact URL matches and near-duplicate titles.
    Returns True if duplicate.
    """
    new_url   = new_article["source_url"]
    new_title = new_article["title"].lower()

    for existing in existing_articles:
        # Exact URL
        if existing["source_url"] == new_url:
            return True

        # Fuzzy title match (>80% similarity)
        similarity = fuzz.ratio(
            new_title, existing["title"].lower()
        )
        if similarity > 80:
            return True

    return False


# ─── FUNCTION 9: Generate article ID ─────────────────────────────────────

def generate_id(url):
    """MD5 hash of URL — first 12 hex characters."""
    return hashlib.md5(url.encode()).hexdigest()[:12]


# ─── FUNCTION 10: Remove old articles ────────────────────────────────────

def clean_old_articles(articles):
    """
    Remove articles older than ARTICLE_MAX_AGE_DAYS.
    Articles with unparseable dates are kept.
    """
    cutoff  = datetime.now(timezone.utc) - timedelta(days=ARTICLE_MAX_AGE_DAYS)
    cleaned = []
    removed = 0

    for article in articles:
        try:
            pub_time = dateparser.parse(article["original_publish_time"])
            if pub_time.tzinfo is None:
                pub_time = pub_time.replace(tzinfo=timezone.utc)

            if pub_time > cutoff:
                cleaned.append(article)
            else:
                removed += 1

        except Exception:
            # Keep articles with unparseable dates
            cleaned.append(article)

    if removed > 0:
        log_info(f"Removed {removed} articles older than {ARTICLE_MAX_AGE_DAYS} days")

    return cleaned


# ─── FUNCTION 11: Save feed.json ─────────────────────────────────────────

def save_feed(articles, sources_checked):
    """
    Sort articles newest-first, trim to MAX_ARTICLES,
    and write feed.json to the project root.
    Returns the absolute path to the saved file.
    """

    def _get_time(a):
        try:
            t = dateparser.parse(a["original_publish_time"])
            if t.tzinfo is None:
                t = t.replace(tzinfo=timezone.utc)
            return t
        except Exception:
            return datetime.min.replace(tzinfo=timezone.utc)

    articles.sort(key=_get_time, reverse=True)
    articles = articles[:MAX_ARTICLES]

    feed = {
        "last_updated":    datetime.now(timezone.utc).isoformat(),
        "total_articles":  len(articles),
        "sources_checked": sources_checked,
        "articles":        articles,
    }

    output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "feed.json",
    )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(feed, f, indent=2, ensure_ascii=False)

    log_info(f"Saved {len(articles)} articles to feed.json")
    return output_path


# ─── FUNCTION 12: Push to GitHub ─────────────────────────────────────────

def push_to_github(filepath):
    """
    Push feed.json to the GitHub repository.
    Requires GITHUB_TOKEN environment variable.
    Returns True on success, False on failure.
    """
    if not GITHUB_TOKEN:
        log_info("No GITHUB_TOKEN set — skipping GitHub push")
        return False

    try:
        g    = Github(GITHUB_TOKEN)
        repo = g.get_repo(GITHUB_REPO)

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        timestamp      = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        commit_message = f"Auto-update: feed.json [{timestamp}]"

        try:
            # File exists — update it
            existing = repo.get_contents(
                GITHUB_FEED_PATH, ref=GITHUB_BRANCH
            )
            repo.update_file(
                GITHUB_FEED_PATH,
                commit_message,
                content,
                existing.sha,
                branch=GITHUB_BRANCH,
            )
            log_info("GitHub: feed.json updated successfully")

        except Exception:
            # File does not exist yet — create it
            repo.create_file(
                GITHUB_FEED_PATH,
                commit_message,
                content,
                branch=GITHUB_BRANCH,
            )
            log_info("GitHub: feed.json created successfully")

        return True

    except Exception as e:
        log_error(f"GitHub push failed: {e}")
        return False


# ─── MAIN ─────────────────────────────────────────────────────────────────

def main():
    start_time = datetime.now(timezone.utc)

    log_info("=" * 50)
    log_info("MISAKI ZUNO — News Scraper Starting")
    log_info("=" * 50)

    # 1. Load what we already have
    existing_articles = load_existing_feed()
    new_articles      = []
    sources_checked   = 0

    active_sources = [s for s in SOURCES if s.get("active", True)]
    log_info(f"Processing {len(active_sources)} active sources")

    # 2. Process each source
    for source in active_sources:
        sources_checked += 1

        # Fetch RSS (with one retry on failure)
        entries = fetch_rss_source(source)
        if not entries:
            log_info(
                f"  Retrying {source['name']} "
                f"in {RETRY_WAIT_SECONDS}s..."
            )
            time.sleep(RETRY_WAIT_SECONDS)
            entries = fetch_rss_source(source)

        if not entries:
            log_info(f"  Skipping {source['name']} — no entries after retry")
            continue

        source_domain = source.get("domain", source["name"].lower())
        source_new    = 0

        # Process up to 20 entries per source per run
        for entry in entries[:20]:
            article = parse_entry(entry, source["name"], source_domain)
            if not article:
                continue

            # Relevance filter
            score, keywords = score_article(article)
            if score < MIN_RELEVANCE_SCORE:
                continue

            article["relevance_score"]  = score
            article["keywords_matched"] = keywords

            # Deduplication
            all_so_far = existing_articles + new_articles
            if is_duplicate(article, all_so_far):
                continue

            # Categorize
            article["category"] = categorize_article(article)

            # Brand extraction
            article["brands_mentioned"] = extract_brands(article)

            new_articles.append(article)
            source_new += 1

            # Stop if we've reached the per-run cap
            if len(new_articles) >= ARTICLES_PER_RUN_MAX:
                break

        log_info(
            f"  {source['name']}: +{source_new} new articles"
        )

        if len(new_articles) >= ARTICLES_PER_RUN_MAX:
            log_info("Per-run article cap reached — stopping source loop")
            break

    # 3. Merge, clean, save
    all_articles = new_articles + existing_articles
    all_articles = clean_old_articles(all_articles)

    filepath = save_feed(all_articles, sources_checked)

    # 4. Push to GitHub
    push_to_github(filepath)

    # 5. Log summary
    duration = (datetime.now(timezone.utc) - start_time).seconds
    log_info("=" * 50)
    log_info(
        f"Complete in {duration}s | "
        f"New: {len(new_articles)} | "
        f"Total: {len(all_articles)} | "
        f"Sources: {sources_checked}"
    )
    log_info("=" * 50)


if __name__ == "__main__":
    main()
