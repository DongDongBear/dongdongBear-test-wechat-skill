#!/usr/bin/env python3
"""
Fetch trending hotspots from multiple Chinese platforms.
Aggregates: Weibo, Toutiao, Baidu.

Usage:
    python3 fetch_hotspots.py --limit 30
"""

import argparse
import json
import sys
import time
from datetime import datetime

import requests


def fetch_weibo(limit=30):
    """Fetch Weibo hot search."""
    try:
        resp = requests.get(
            "https://weibo.com/ajax/side/hotSearch",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )
        data = resp.json()
        items = []
        for item in (data.get("data", {}).get("realtime", []))[:limit]:
            items.append({
                "title": item.get("word", ""),
                "hotness": item.get("num", 0),
                "source": "weibo",
                "url": f"https://s.weibo.com/weibo?q={item.get('word', '')}",
            })
        return items
    except Exception as e:
        print(f"Warning: Weibo fetch failed: {e}", file=sys.stderr)
        return []


def fetch_toutiao(limit=30):
    """Fetch Toutiao hot board."""
    try:
        resp = requests.get(
            "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )
        data = resp.json()
        items = []
        for item in (data.get("data", []))[:limit]:
            items.append({
                "title": item.get("Title", ""),
                "hotness": item.get("HotValue", 0),
                "source": "toutiao",
                "url": item.get("Url", ""),
            })
        return items
    except Exception as e:
        print(f"Warning: Toutiao fetch failed: {e}", file=sys.stderr)
        return []


def fetch_baidu(limit=30):
    """Fetch Baidu hot search."""
    try:
        resp = requests.get(
            "https://top.baidu.com/api/board?platform=wise&tab=realtime",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )
        data = resp.json()
        items = []
        cards = data.get("data", {}).get("cards", [])
        if cards:
            for item in (cards[0].get("content", []))[:limit]:
                items.append({
                    "title": item.get("word", ""),
                    "hotness": int(item.get("hotScore", 0)),
                    "source": "baidu",
                    "url": item.get("url", ""),
                })
        return items
    except Exception as e:
        print(f"Warning: Baidu fetch failed: {e}", file=sys.stderr)
        return []


def deduplicate(items):
    """Remove duplicates by title similarity."""
    seen = set()
    result = []
    for item in items:
        key = item["title"].strip().lower()
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def main():
    parser = argparse.ArgumentParser(description="Fetch trending hotspots from Chinese platforms")
    parser.add_argument("--limit", type=int, default=30, help="Max items per source")
    args = parser.parse_args()

    all_items = []
    all_items.extend(fetch_weibo(args.limit))
    all_items.extend(fetch_toutiao(args.limit))
    all_items.extend(fetch_baidu(args.limit))

    all_items = deduplicate(all_items)
    all_items.sort(key=lambda x: int(x.get("hotness", 0) or 0), reverse=True)

    output = {
        "timestamp": datetime.now().isoformat(),
        "sources": ["weibo", "toutiao", "baidu"],
        "count": len(all_items),
        "items": all_items,
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
