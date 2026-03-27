#!/usr/bin/env python3
"""
Build writing playbook from historical corpus.

Usage:
    python3 build_playbook.py --client demo
"""

import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Extract writing patterns from corpus")
    parser.add_argument("--client", required=True, help="Client name")
    args = parser.parse_args()

    skill_dir = Path(__file__).parent.parent
    corpus_dir = skill_dir / "clients" / args.client / "corpus"

    if not corpus_dir.exists():
        print(f"Error: Corpus directory not found: {corpus_dir}")
        print(f"Create it and add .md files: mkdir -p {corpus_dir}")
        sys.exit(1)

    files = sorted(corpus_dir.glob("*.md"))
    if not files:
        print(f"Error: No .md files found in {corpus_dir}")
        print("Add at least 20 historical articles (50+ recommended).")
        sys.exit(1)

    # Compute corpus stats
    total_chars = 0
    total_titles = 0
    title_lengths = []
    h2_counts = []
    articles = []

    for f in files:
        text = f.read_text(encoding="utf-8")
        chars = len(text)
        total_chars += chars

        lines = text.split("\n")
        title = ""
        h2_count = 0
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("# ") and not stripped.startswith("## "):
                title = stripped[2:].strip()
                total_titles += 1
                title_lengths.append(len(title))
            elif stripped.startswith("## "):
                h2_count += 1

        h2_counts.append(h2_count)
        articles.append({
            "file": f.name,
            "chars": chars,
            "title": title,
            "h2_count": h2_count,
        })

    avg_chars = total_chars // len(files) if files else 0
    avg_title_len = sum(title_lengths) // len(title_lengths) if title_lengths else 0
    avg_h2 = sum(h2_counts) // len(h2_counts) if h2_counts else 0

    stats = {
        "total_articles": len(files),
        "avg_chars": avg_chars,
        "avg_title_length": avg_title_len,
        "avg_h2_count": avg_h2,
        "articles": articles,
    }

    print(json.dumps(stats, ensure_ascii=False, indent=2))

    # Output batch analysis prompts
    print("\n--- Batch Analysis Instructions ---")
    print(f"Total articles: {len(files)}")
    print(f"Average length: {avg_chars} chars")
    print(f"Average title length: {avg_title_len} chars")
    print(f"Average H2 sections: {avg_h2}")
    print()
    print("Read each article and extract the following patterns:")
    print("1. Title patterns (character count range, common strategies)")
    print("2. Opening patterns (hook types, first sentence styles)")
    print("3. Paragraph rhythm (sentence count distribution)")
    print("4. Word fingerprints (forbidden words, catchphrases)")
    print("5. H2 naming habits")
    print("6. Ending patterns (CTA types)")
    print("7. Emotional tone (formal/casual/humorous spectrum)")
    print("8. Image style preferences")
    print()
    print(f"Save results to: {skill_dir}/clients/{args.client}/playbook.md")


if __name__ == "__main__":
    main()
