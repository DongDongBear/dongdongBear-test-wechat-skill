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
import logging
import sys
from datetime import datetime
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)


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
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

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
        # 汇总所有 lessons
        lesson_files = sorted(lessons_dir.glob("*.yaml"))
        lessons = []
        for f in lesson_files:
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    lesson = yaml.safe_load(fh)
                    if lesson:
                        lessons.append(lesson)
            except yaml.YAMLError as exc:
                logger.warning("跳过无法解析的 YAML 文件 %s: %s", f.name, exc)
            except OSError as exc:
                logger.warning("无法读取文件 %s: %s", f.name, exc)
        print(json.dumps(lessons, ensure_ascii=False, indent=2))
        logger.info("Total lessons: %d", len(lessons))
        if len(lessons) >= 5:
            logger.info("Recommendation: Run playbook update to consolidate patterns.")
        return

    if not args.draft or not args.final:
        logger.error("--draft and --final required (or use --summarize)")
        sys.exit(1)

    # 检查 draft 文件是否存在
    draft_path = Path(args.draft)
    if not draft_path.exists():
        logger.error("Draft 文件不存在: %s", draft_path)
        sys.exit(1)

    # 检查 final 文件是否存在
    final_path = Path(args.final)
    if not final_path.exists():
        logger.error("Final 文件不存在: %s", final_path)
        sys.exit(1)

    try:
        draft_text = draft_path.read_text(encoding="utf-8")
    except OSError as exc:
        logger.error("无法读取 draft 文件 %s: %s", draft_path, exc)
        sys.exit(1)

    try:
        final_text = final_path.read_text(encoding="utf-8")
    except OSError as exc:
        logger.error("无法读取 final 文件 %s: %s", final_path, exc)
        sys.exit(1)

    analysis = analyze_diff(draft_text, final_text)

    # Save lesson
    lesson = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "draft": args.draft,
        "final": args.final,
        "edits": analysis,
        "patterns": [],  # To be filled by Agent analysis
    }

    # 使用 HHmmss 时间戳避免同一天内的文件名冲突
    output_file = lessons_dir / f"{datetime.now().strftime('%Y-%m-%d_%H%M%S')}-diff.yaml"
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            yaml.dump(lesson, f, allow_unicode=True, default_flow_style=False)
    except (OSError, yaml.YAMLError) as exc:
        logger.error("无法写入 lesson 文件 %s: %s", output_file, exc)
        sys.exit(1)

    print(json.dumps(analysis, ensure_ascii=False, indent=2))
    logger.info("Lesson saved to: %s", output_file)

    # Check if playbook update needed
    lesson_count = len(list(lessons_dir.glob("*.yaml")))
    if lesson_count >= 5 and lesson_count % 5 == 0:
        logger.info(
            "%d lessons accumulated. Consider updating playbook:\n"
            "  python3 %s --client %s --summarize",
            lesson_count, __file__, args.client,
        )


if __name__ == "__main__":
    main()
