#!/usr/bin/env python3
"""
Fetch WeChat article statistics and update history.yaml.

Usage:
    python3 fetch_stats.py --client demo --days 7
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import requests
import yaml


def get_article_summary(token, begin_date, end_date):
    """Get daily article summary from WeChat Data Analytics API."""
    resp = requests.post(
        f"https://api.weixin.qq.com/datacube/getarticlesummary?access_token={token}",
        json={"begin_date": begin_date, "end_date": end_date},
    )
    data = resp.json()
    if "list" in data:
        return data["list"]
    return []


def get_article_total(token, begin_date, end_date):
    """Get cumulative article stats."""
    resp = requests.post(
        f"https://api.weixin.qq.com/datacube/getarticletotal?access_token={token}",
        json={"begin_date": begin_date, "end_date": end_date},
    )
    data = resp.json()
    if "list" in data:
        return data["list"]
    return []


def main():
    parser = argparse.ArgumentParser(description="Fetch WeChat article stats")
    parser.add_argument("--client", required=True, help="Client name")
    parser.add_argument("--days", type=int, default=7, help="Days to look back")
    parser.add_argument("--token", help="WeChat access token (or reads from config)")
    args = parser.parse_args()

    skill_dir = Path(__file__).parent.parent
    history_path = skill_dir / "clients" / args.client / "history.yaml"

    if not history_path.exists():
        print(f"Error: {history_path} not found", file=sys.stderr)
        sys.exit(1)

    with open(history_path, "r", encoding="utf-8") as f:
        content = f.read()
        history = yaml.safe_load(content)
        if not isinstance(history, list):
            history = []

    if not args.token:
        # Try to load from config
        config_path = skill_dir / "config.yaml"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
            wechat = cfg.get("wechat", {})
            appid = wechat.get("appid")
            secret = wechat.get("secret")
            if appid and secret:
                from wechat_api_helper import get_access_token
                token = get_access_token(appid, secret)
            else:
                print("Error: No access token and no appid/secret in config.yaml", file=sys.stderr)
                sys.exit(1)
        else:
            print("Error: Provide --token or configure config.yaml", file=sys.stderr)
            sys.exit(1)
    else:
        token = args.token

    end = datetime.now()
    begin = end - timedelta(days=args.days)
    begin_str = begin.strftime("%Y-%m-%d")
    end_str = end.strftime("%Y-%m-%d")

    print(f"Fetching stats for {args.client} ({begin_str} to {end_str})...")

    try:
        stats = get_article_total(token, begin_str, end_str)
    except Exception as e:
        print(f"Error fetching stats: {e}", file=sys.stderr)
        sys.exit(1)

    # Match stats to history by title
    updated = 0
    for entry in history:
        if entry.get("stats") is not None:
            continue
        for stat in stats:
            details = stat.get("details", [])
            for d in details:
                if d.get("title") == entry.get("title"):
                    entry["stats"] = {
                        "read_count": d.get("int_page_read_count", 0),
                        "share_count": d.get("share_count", 0),
                        "like_count": d.get("like_count", 0),
                    }
                    updated += 1
                    break

    if updated > 0:
        with open(history_path, "w", encoding="utf-8") as f:
            yaml.dump(history, f, allow_unicode=True, default_flow_style=False)
        print(f"Updated {updated} entries in history.yaml")
    else:
        print("No matching articles found to update.")

    # Output summary
    output = {
        "client": args.client,
        "period": f"{begin_str} to {end_str}",
        "stats_fetched": len(stats),
        "history_updated": updated,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
