#!/usr/bin/env python3
"""
Learn from human edits by analyzing diffs between draft and final.

Usage:
    python3 learn_edits.py --client demo --draft draft.md --final final.md
    python3 learn_edits.py --client demo --summarize
"""

import argparse
import difflib
import json
import sys
from datetime import datetime
from pathlib import Path

import yaml


def analyze_diff(draft_text, final_text):
    """Analyze differences between draft and final versions."""
    draft_lines = draft_text.splitlines(keepends=True)
    final_lines = final_text.splitlines(keepends=True)

    diff = list(difflib.unified_diff(draft_lines, final_lines, lineterm=""))

    categories = {
        "word_replacements": [],
        "paragraph_deletions": [],
        "paragraph_additions": [],
        "structure_changes": [],
        "title_changes": [],
        "tone_adjustments": [],
    }

    added_lines = []
    removed_lines = []

    for line in diff:
        if line.startswith("+") and not line.startswith("+++"):
            added_lines.append(line[1:].strip())
        elif line.startswith("-") and not line.startswith("---"):
            removed_lines.append(line[1:].strip())

    # Detect title changes
    for r in removed_lines:
        if r.startswith("# "):
            for a in added_lines:
                if a.startswith("# "):
                    categories["title_changes"].append({
                        "from": r[2:].strip(),
                        "to": a[2:].strip(),
                    })

    # Detect H2 structure changes
    removed_h2 = [r for r in removed_lines if r.startswith("## ")]
    added_h2 = [a for a in added_lines if a.startswith("## ")]
    if removed_h2 or added_h2:
        categories["structure_changes"].append({
            "removed_headings": [h[3:].strip() for h in removed_h2],
            "added_headings": [h[3:].strip() for h in added_h2],
        })

    return {
        "total_additions": len(added_lines),
        "total_deletions": len(removed_lines),
        "categories": categories,
        "raw_additions": added_lines[:20],
        "raw_deletions": removed_lines[:20],
    }


def main():
    parser = argparse.ArgumentParser(description="Learn from human edits")
    parser.add_argument("--client", required=True, help="Client name")
    parser.add_argument("--draft", help="Draft markdown file")
    parser.add_argument("--final", help="Final markdown file")
    parser.add_argument("--summarize", action="store_true", help="Summarize all lessons")
    args = parser.parse_args()

    skill_dir = Path(__file__).parent.parent
    lessons_dir = skill_dir / "clients" / args.client / "lessons"
    lessons_dir.mkdir(parents=True, exist_ok=True)

    if args.summarize:
        # List all lessons
        lesson_files = sorted(lessons_dir.glob("*.yaml"))
        lessons = []
        for f in lesson_files:
            with open(f, "r", encoding="utf-8") as fh:
                lesson = yaml.safe_load(fh)
                if lesson:
                    lessons.append(lesson)
        print(json.dumps(lessons, ensure_ascii=False, indent=2))
        print(f"\nTotal lessons: {len(lessons)}")
        if len(lessons) >= 5:
            print("Recommendation: Run playbook update to consolidate patterns.")
        return

    if not args.draft or not args.final:
        print("Error: --draft and --final required (or use --summarize)")
        sys.exit(1)

    draft_text = Path(args.draft).read_text(encoding="utf-8")
    final_text = Path(args.final).read_text(encoding="utf-8")

    analysis = analyze_diff(draft_text, final_text)

    # Save lesson
    lesson = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "draft": args.draft,
        "final": args.final,
        "edits": analysis,
        "patterns": [],  # To be filled by Agent analysis
    }

    output_file = lessons_dir / f"{datetime.now().strftime('%Y-%m-%d')}-diff.yaml"
    with open(output_file, "w", encoding="utf-8") as f:
        yaml.dump(lesson, f, allow_unicode=True, default_flow_style=False)

    print(json.dumps(analysis, ensure_ascii=False, indent=2))
    print(f"\nLesson saved to: {output_file}")

    # Check if playbook update needed
    lesson_count = len(list(lessons_dir.glob("*.yaml")))
    if lesson_count >= 5 and lesson_count % 5 == 0:
        print(f"\n{lesson_count} lessons accumulated. Consider updating playbook:")
        print(f"  python3 {__file__} --client {args.client} --summarize")


if __name__ == "__main__":
    main()
