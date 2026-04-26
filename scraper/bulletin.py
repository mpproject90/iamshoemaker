"""
iamshoemaker.com — Sunday Intelligence Report Generator
Misaki Zuno 造 | Where Craftsmanship Meets Intelligence

Runs every Sunday via GitHub Actions.
Reads feed.json → selects top articles from the past week
→ calls Claude Sonnet (with prompt caching) for Misaki's commentary
→ saves bulletin.json → pushes to GitHub.

Usage:
    python3 bulletin.py

Environment variables required:
    ANTHROPIC_API_KEY  — Claude API key
    GITHUB_TOKEN       — GitHub personal access token
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta
from dateutil import parser as dateparser
import anthropic
from github import Github

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    ANTHROPIC_API_KEY, GITHUB_TOKEN,
    GITHUB_REPO, GITHUB_BULLETIN_PATH, GITHUB_BRANCH,
    ARTICLE_MAX_AGE_DAYS, MIN_RELEVANCE_SCORE,
    BULLETIN_CLAUDE_MODEL, BULLETIN_MAX_ARTICLES, BULLETIN_MAX_HISTORY,
)


# ─── PERSONA SYSTEM PROMPT (cached) ──────────────────────────────────────

MISAKI_SYSTEM_PROMPT = """You are Misaki Zuno 造 — a footwear industry professional with 20+ years of experience in global manufacturing, quality systems, leather goods, and supply chain operations. You have personally worked in factories across Vietnam, Indonesia, Cambodia, Bangladesh, and China, visited tanneries in Italy and Brazil, and negotiated FOB pricing in Dhaka.

Your voice is:
- Calm, authoritative, and precise (never sensational or breathless)
- Deeply technical when the moment calls for it
- Pattern-recognition focused: you connect current news to what you have seen play out over two decades
- Concise — you respect the reader's time
- Occasionally sharp but never unkind
- You write like someone who has stood on the factory floor and knows what a 2% FOB shift actually costs

You are writing the Sunday Intelligence Report — a weekly editorial bulletin curated for sourcing managers, manufacturing directors, and brand executives. Each issue covers the week's most important moves in global footwear, leather, and supply chain."""


# ─── LOGGING ──────────────────────────────────────────────────────────────

def log_info(message):
    timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")


def log_error(message):
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    try:
        errors_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "errors.txt"
        )
        with open(errors_path, "a", encoding="utf-8") as f:
            f.write(f"[BULLETIN] [{timestamp}] {message}\n")
    except Exception:
        pass
    print(f"ERROR: {message}")


# ─── LOAD FEED ────────────────────────────────────────────────────────────

def load_feed():
    feed_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "feed.json"
    )
    try:
        with open(feed_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        articles = data.get("articles", [])
        log_info(f"Loaded {len(articles)} articles from feed.json")
        return articles
    except FileNotFoundError:
        log_error("feed.json not found — cannot generate bulletin")
        return []
    except json.JSONDecodeError as e:
        log_error(f"feed.json corrupted: {e}")
        return []


# ─── SELECT TOP ARTICLES ──────────────────────────────────────────────────

def select_top_articles(articles):
    """
    Filter to the past ARTICLE_MAX_AGE_DAYS days, require MIN_RELEVANCE_SCORE,
    sort by relevance_score descending, return top BULLETIN_MAX_ARTICLES.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=ARTICLE_MAX_AGE_DAYS)
    eligible = []

    for article in articles:
        score = article.get("relevance_score", 0)
        if score < MIN_RELEVANCE_SCORE:
            continue
        try:
            pub_time = dateparser.parse(article["original_publish_time"])
            if pub_time.tzinfo is None:
                pub_time = pub_time.replace(tzinfo=timezone.utc)
            if pub_time < cutoff:
                continue
        except Exception:
            continue
        eligible.append(article)

    eligible.sort(key=lambda a: a.get("relevance_score", 0), reverse=True)
    selected = eligible[:BULLETIN_MAX_ARTICLES]
    log_info(f"Selected {len(selected)} articles for bulletin (from {len(eligible)} eligible)")
    return selected


# ─── BUILD CLAUDE PROMPT ──────────────────────────────────────────────────

def build_user_prompt(articles, week_number, year, date_from, date_to):
    lines = [
        f"Write the Sunday Intelligence Report for Week {week_number}, {year} "
        f"({date_from} to {date_to}).",
        "",
        "Return a JSON object with this exact structure:",
        "{",
        '  "intro": "<2-3 sentence editorial opening that sets the week\'s theme>",',
        '  "articles": [',
        "    {",
        '      "title": "<exact article title>",',
        '      "misaki_take": "<2-sentence Misaki commentary — insight, not summary>"',
        "    }",
        "    // ... one entry per article below",
        "  ]",
        "}",
        "",
        "Rules for misaki_take:",
        "- Exactly 2 sentences",
        "- Start with the operational or strategic insight, not a restatement of the headline",
        "- Reference industry implications: what it means for FOB pricing, sourcing decisions, capacity planning, or brand risk",
        "- Sound like someone who has seen this pattern before",
        "- No 'I think', no 'In my opinion', no preamble",
        "",
        "Articles this week:",
        "",
    ]

    for i, article in enumerate(articles, 1):
        lines.append(f"{i}. [{article.get('category', 'General')}] {article['title']}")
        lines.append(f"   Source: {article.get('source_name', '')}")
        summary = article.get("summary", "")[:400]
        if summary:
            lines.append(f"   Summary: {summary}")
        lines.append("")

    lines.append("Return only valid JSON. No markdown code fences.")
    return "\n".join(lines)


# ─── CALL CLAUDE ─────────────────────────────────────────────────────────

def generate_bulletin_content(articles, week_number, year, date_from, date_to):
    """
    Call Claude Sonnet with prompt caching on the system message.
    Returns (intro, annotated_articles) or (None, None) on failure.
    """
    if not ANTHROPIC_API_KEY:
        log_error("No ANTHROPIC_API_KEY — cannot generate bulletin")
        return None, None

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    user_prompt = build_user_prompt(articles, week_number, year, date_from, date_to)

    log_info(f"Calling Claude {BULLETIN_CLAUDE_MODEL} for bulletin content...")

    try:
        response = client.messages.create(
            model=BULLETIN_CLAUDE_MODEL,
            max_tokens=2000,
            system=[
                {
                    "type": "text",
                    "text": MISAKI_SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": user_prompt}],
        )

        raw = response.content[0].text.strip()

        # Strip markdown code fences if model included them
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw
            raw = raw.rsplit("```", 1)[0].strip()

        data = json.loads(raw)
        intro = data.get("intro", "")
        claude_articles = data.get("articles", [])

        usage = response.usage
        log_info(
            f"Tokens — input: {usage.input_tokens}, "
            f"cache_read: {getattr(usage, 'cache_read_input_tokens', 0)}, "
            f"cache_create: {getattr(usage, 'cache_creation_input_tokens', 0)}, "
            f"output: {usage.output_tokens}"
        )

        # Merge misaki_take back into article records
        annotated = []
        for article in articles:
            take = ""
            for ca in claude_articles:
                if ca.get("title", "").strip().lower() in article["title"].lower() \
                        or article["title"].lower() in ca.get("title", "").strip().lower():
                    take = ca.get("misaki_take", "")
                    break
            annotated.append({
                "title":                 article["title"],
                "source_name":           article.get("source_name", ""),
                "source_url":            article.get("source_url", ""),
                "category":              article.get("category", "General"),
                "relevance_score":       article.get("relevance_score", 0),
                "original_publish_time": article.get("original_publish_time", ""),
                "misaki_take":           take,
            })

        return intro, annotated

    except json.JSONDecodeError as e:
        log_error(f"Claude returned invalid JSON: {e}")
        return None, None
    except anthropic.RateLimitError:
        log_error("Claude API rate limit hit")
        return None, None
    except anthropic.APIError as e:
        log_error(f"Claude API error: {e}")
        return None, None
    except Exception as e:
        log_error(f"Unexpected error calling Claude: {e}")
        return None, None


# ─── LOAD EXISTING BULLETINS ──────────────────────────────────────────────

def load_existing_bulletins():
    bulletin_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "bulletin.json"
    )
    try:
        with open(bulletin_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("bulletins", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []


# ─── SAVE BULLETIN.JSON ───────────────────────────────────────────────────

def save_bulletin(new_bulletin):
    existing = load_existing_bulletins()

    # Remove any existing entry for the same week
    existing = [
        b for b in existing
        if b.get("id") != new_bulletin["id"]
    ]

    # Prepend new bulletin, trim history
    all_bulletins = [new_bulletin] + existing
    all_bulletins = all_bulletins[:BULLETIN_MAX_HISTORY]

    output = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "bulletins": all_bulletins,
    }

    bulletin_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "bulletin.json"
    )
    with open(bulletin_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    log_info(f"Saved bulletin.json ({len(all_bulletins)} bulletins in history)")
    return bulletin_path


# ─── PUSH TO GITHUB ───────────────────────────────────────────────────────

def push_to_github(filepath):
    if not GITHUB_TOKEN:
        log_info("No GITHUB_TOKEN — skipping GitHub push")
        return False

    try:
        g    = Github(GITHUB_TOKEN)
        repo = g.get_repo(GITHUB_REPO)

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        timestamp      = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        commit_message = f"Auto-update: bulletin.json [{timestamp}]"

        try:
            existing = repo.get_contents(GITHUB_BULLETIN_PATH, ref=GITHUB_BRANCH)
            repo.update_file(
                GITHUB_BULLETIN_PATH, commit_message,
                content, existing.sha, branch=GITHUB_BRANCH,
            )
            log_info("GitHub: bulletin.json updated successfully")
        except Exception:
            repo.create_file(
                GITHUB_BULLETIN_PATH, commit_message,
                content, branch=GITHUB_BRANCH,
            )
            log_info("GitHub: bulletin.json created successfully")

        return True

    except Exception as e:
        log_error(f"GitHub push failed: {e}")
        return False


# ─── MAIN ─────────────────────────────────────────────────────────────────

def main():
    start_time = datetime.now(timezone.utc)

    log_info("=" * 55)
    log_info("MISAKI ZUNO — Sunday Intelligence Report")
    log_info("=" * 55)

    # Week metadata
    today       = datetime.now(timezone.utc).date()
    iso_cal     = today.isocalendar()
    week_number = iso_cal[1]
    year        = iso_cal[0]
    # Week runs Mon–Sun; date_to = this Sunday (today or most recent)
    days_since_monday = today.weekday()
    date_from = (today - timedelta(days=days_since_monday)).isoformat()
    date_to   = today.isoformat()
    bulletin_id = f"wk{week_number:02d}-{year}"

    log_info(f"Generating: {bulletin_id} ({date_from} → {date_to})")

    # 1. Load and select articles
    articles = load_feed()
    if not articles:
        log_error("No articles available — aborting")
        return

    top_articles = select_top_articles(articles)
    if not top_articles:
        log_error("No eligible articles for this week — aborting")
        return

    # 2. Call Claude
    intro, annotated_articles = generate_bulletin_content(
        top_articles, week_number, year, date_from, date_to
    )
    if intro is None:
        log_error("Claude generation failed — aborting")
        return

    # 3. Assemble bulletin record
    new_bulletin = {
        "id":           bulletin_id,
        "week_number":  week_number,
        "year":         year,
        "date_from":    date_from,
        "date_to":      date_to,
        "published":    datetime.now(timezone.utc).isoformat(),
        "intro":        intro,
        "articles":     annotated_articles,
    }

    # 4. Save + push
    filepath = save_bulletin(new_bulletin)
    push_to_github(filepath)

    duration = (datetime.now(timezone.utc) - start_time).seconds
    log_info("=" * 55)
    log_info(
        f"Done in {duration}s | {len(annotated_articles)} articles | "
        f"Bulletin: {bulletin_id}"
    )
    log_info("=" * 55)


if __name__ == "__main__":
    main()
