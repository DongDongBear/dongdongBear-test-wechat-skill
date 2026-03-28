#!/usr/bin/env python3
"""
Build writing playbook from historical corpus.

Usage:
    python3 build_playbook.py --client demo
    python3 build_playbook.py --client demo --verbose
"""

import argparse
import json
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Extract writing patterns from corpus")
    parser.add_argument("--client", required=True, help="Client name")
    parser.add_argument("--verbose", action="store_true", help="输出每篇文章的调试详情")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    skill_dir = Path(__file__).parent.parent
    corpus_dir = skill_dir / "clients" / args.client / "corpus"

    if not corpus_dir.exists():
        logger.error("Corpus directory not found: %s", corpus_dir)
        logger.error("Create it and add .md files: mkdir -p %s", corpus_dir)
        sys.exit(1)

    files = sorted(corpus_dir.glob("*.md"))
    if not files:
        logger.error("No .md files found in %s", corpus_dir)
        logger.error("Add at least 20 historical articles (50+ recommended).")
        sys.exit(1)

    # Compute corpus stats
    total_chars = 0
    total_titles = 0
    title_lengths = []
    h2_counts = []
    articles = []
    skipped = 0

    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except OSError as exc:
            logger.warning("无法读取文件 %s: %s", f.name, exc)
            skipped += 1
            continue

        # 跳过空文件
        if not text.strip():
            logger.warning("跳过空文件: %s", f.name)
            skipped += 1
            continue

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

        logger.debug(
            "  %s — %d chars, title=%r, h2=%d",
            f.name, chars, title, h2_count,
        )

    if not articles:
        logger.error("所有 corpus 文件均无效，无法生成统计信息。")
        sys.exit(1)

    if skipped:
        logger.warning("跳过 %d 个无效或空文件", skipped)

    avg_chars = total_chars // len(articles)
    avg_title_len = sum(title_lengths) // len(title_lengths) if title_lengths else 0
    avg_h2 = sum(h2_counts) // len(h2_counts) if h2_counts else 0

    stats = {
        "total_articles": len(articles),
        "avg_chars": avg_chars,
        "avg_title_length": avg_title_len,
        "avg_h2_count": avg_h2,
        "articles": articles,
    }

    print(json.dumps(stats, ensure_ascii=False, indent=2))

    # Output batch analysis prompts
    print("\n--- Batch Analysis Instructions ---")
    print(f"Total articles: {len(articles)}")
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
