"""
build_posts.py
Reads all .md files from content/posts/ and builds posts.json
Runs automatically via GitHub Actions when a post is published.
"""

import os
import json
import re

POSTS_DIR = 'content/posts'
OUTPUT_FILE = 'posts.json'


def parse_frontmatter(text):
    """Extract YAML frontmatter and body from a markdown file."""
    if not text.startswith('---'):
        return {}, text.strip()

    end = text.find('---', 3)
    if end == -1:
        return {}, text.strip()

    front = text[3:end].strip()
    body = text[end + 3:].strip()

    meta = {}
    for line in front.splitlines():
        if ':' in line:
            key, _, value = line.partition(':')
            meta[key.strip()] = value.strip().strip('"').strip("'")

    return meta, body


def clean_markdown(text):
    """Strip basic markdown syntax to plain text paragraphs."""
    # Remove headings
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove bold/italic
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    # Remove links, keep display text
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    # Remove blockquotes
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    return text


def build_posts():
    posts = []

    if not os.path.exists(POSTS_DIR):
        print(f"No posts directory found at {POSTS_DIR}")
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump({"posts": []}, f, indent=2)
        return

    for filename in sorted(os.listdir(POSTS_DIR), reverse=True):
        if not filename.endswith('.md'):
            continue

        filepath = os.path.join(POSTS_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            raw = f.read()

        meta, body = parse_frontmatter(raw)
        if not meta.get('title'):
            print(f"Skipping {filename} — no title found")
            continue

        # Use filename (without .md) as the post ID
        post_id = filename.replace('.md', '')

        # Convert body to array of paragraphs
        body_clean = clean_markdown(body)
        paragraphs = [p.strip() for p in re.split(r'\n\n+', body_clean) if p.strip()]

        posts.append({
            "id": post_id,
            "title": meta.get('title', ''),
            "date": meta.get('date', ''),
            "category": meta.get('category', 'Analysis'),
            "image": meta.get('image', ''),
            "summary": meta.get('summary', ''),
            "content": paragraphs
        })

    # Sort newest first
    posts.sort(key=lambda x: x.get('date', ''), reverse=True)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump({"posts": posts}, f, indent=2, ensure_ascii=False)

    print(f"Built {OUTPUT_FILE} — {len(posts)} post(s)")


if __name__ == '__main__':
    build_posts()
