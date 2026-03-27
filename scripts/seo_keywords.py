#!/usr/bin/env python3
"""
SEO keyword research via search suggestion APIs.

Usage:
    python3 seo_keywords.py --json "AI Agent" "大模型" "效率工具"
"""

import argparse
import json
import sys
from urllib.parse import quote

import requests


def baidu_suggestions(keyword):
    """Get Baidu search suggestions as volume proxy."""
    try:
        resp = requests.get(
            f"https://suggestion.baidu.com/su?wd={quote(keyword)}&action=opensearch",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=5,
        )
        data = resp.json()
        suggestions = data[1] if len(data) > 1 else []
        return {
            "source": "baidu",
            "suggestions": suggestions[:8],
            "count": len(suggestions),
        }
    except Exception:
        return {"source": "baidu", "suggestions": [], "count": 0}


def so_suggestions(keyword):
    """Get 360 search suggestions."""
    try:
        resp = requests.get(
            f"https://sug.so.360.cn/suggest?word={quote(keyword)}&encodein=utf-8&encodeout=utf-8&format=json",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=5,
        )
        data = resp.json()
        items = data.get("result", [])
        suggestions = [item.get("word", "") for item in items]
        return {
            "source": "360",
            "suggestions": suggestions[:8],
            "count": len(suggestions),
        }
    except Exception:
        return {"source": "360", "suggestions": [], "count": 0}


def score_keyword(keyword):
    """Score a keyword's SEO potential (0-10)."""
    baidu = baidu_suggestions(keyword)
    so = so_suggestions(keyword)

    baidu_score = min(10, baidu["count"] * 1.2)
    so_score = min(10, so["count"] * 1.5)
    seo_score = round((baidu_score * 0.6 + so_score * 0.4), 1)

    all_suggestions = list(set(baidu["suggestions"] + so["suggestions"]))

    return {
        "keyword": keyword,
        "seo_score": seo_score,
        "baidu_score": round(baidu_score, 1),
        "so_score": round(so_score, 1),
        "related_keywords": all_suggestions[:10],
    }


def main():
    parser = argparse.ArgumentParser(description="SEO keyword analysis")
    parser.add_argument("keywords", nargs="+", help="Keywords to analyze")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    results = [score_keyword(kw) for kw in args.keywords]

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(f"\n  {r['keyword']}")
            print(f"    SEO Score: {r['seo_score']}/10")
            print(f"    Baidu: {r['baidu_score']}, 360: {r['so_score']}")
            print(f"    Related: {', '.join(r['related_keywords'][:5])}")


if __name__ == "__main__":
    main()
