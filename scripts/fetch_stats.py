#!/usr/bin/env python3
"""
Fetch WeChat article statistics and update history.yaml.

Usage:
    python3 fetch_stats.py --client demo --days 7
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import requests
import yaml

logger = logging.getLogger(__name__)

# 最大重试次数
MAX_RETRIES = 3
# 重试退避基数（秒）
BACKOFF_BASE = 2


def _request_with_retry(method, url, **kwargs):
    """带重试和指数退避的 HTTP 请求封装。"""
    last_exc = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.request(method, url, **kwargs)
            resp.raise_for_status()
            return resp
        except requests.RequestException as exc:
            last_exc = exc
            if attempt < MAX_RETRIES:
                wait = BACKOFF_BASE ** attempt
                logger.warning(
                    "请求失败 (第 %d/%d 次): %s — %d 秒后重试",
                    attempt, MAX_RETRIES, exc, wait,
                )
                time.sleep(wait)
            else:
                logger.error("请求失败，已达最大重试次数: %s", exc)
    raise last_exc  # type: ignore[misc]


def get_access_token(appid, secret):
    """通过微信 API 获取 access_token（对应 toolkit/src/wechat-api.ts 中的 getAccessToken）。"""
    url = (
        "https://api.weixin.qq.com/cgi-bin/token"
        f"?grant_type=client_credential&appid={appid}&secret={secret}"
    )
    resp = _request_with_retry("GET", url)
    data = resp.json()

    if "access_token" not in data:
        errcode = data.get("errcode", "unknown")
        errmsg = data.get("errmsg", "unknown")
        raise RuntimeError(
            f"WeChat API error: errcode={errcode}, errmsg={errmsg}"
        )

    return data["access_token"]


def get_article_total(token, begin_date, end_date):
    """获取文章累计统计数据。"""
    url = f"https://api.weixin.qq.com/datacube/getarticletotal?access_token={token}"
    resp = _request_with_retry("POST", url, json={
        "begin_date": begin_date,
        "end_date": end_date,
    })
    data = resp.json()

    # 校验返回结构
    if "errcode" in data and data["errcode"] != 0:
        errcode = data.get("errcode", "unknown")
        errmsg = data.get("errmsg", "unknown")
        raise RuntimeError(
            f"WeChat datacube error: errcode={errcode}, errmsg={errmsg}"
        )

    if not isinstance(data.get("list"), list):
        logger.warning("API 返回中缺少 'list' 字段或格式异常: %s", data)
        return []

    return data["list"]


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    parser = argparse.ArgumentParser(description="Fetch WeChat article stats")
    parser.add_argument("--client", required=True, help="Client name")
    parser.add_argument("--days", type=int, default=7, help="Days to look back")
    parser.add_argument("--token", help="WeChat access token (or reads from config)")
    args = parser.parse_args()

    skill_dir = Path(__file__).parent.parent
    history_path = skill_dir / "clients" / args.client / "history.yaml"

    if not history_path.exists():
        logger.error("文件不存在: %s", history_path)
        sys.exit(1)

    with open(history_path, "r", encoding="utf-8") as f:
        content = f.read()
        history = yaml.safe_load(content)
        if not isinstance(history, list):
            history = []

    if not args.token:
        # 尝试从配置文件读取
        config_path = skill_dir / "config.yaml"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
            wechat = cfg.get("wechat", {})
            appid = wechat.get("appid")
            secret = wechat.get("secret")
            if appid and secret:
                token = get_access_token(appid, secret)
            else:
                logger.error("配置文件中缺少 appid/secret，且未提供 --token")
                sys.exit(1)
        else:
            logger.error("请提供 --token 或配置 config.yaml")
            sys.exit(1)
    else:
        token = args.token

    end = datetime.now()
    begin = end - timedelta(days=args.days)
    begin_str = begin.strftime("%Y-%m-%d")
    end_str = end.strftime("%Y-%m-%d")

    logger.info("正在获取 %s 的统计数据 (%s to %s)...", args.client, begin_str, end_str)

    try:
        stats = get_article_total(token, begin_str, end_str)
    except Exception as e:
        logger.error("获取统计数据失败: %s", e)
        sys.exit(1)

    # 按标题匹配统计数据到历史记录
    updated = 0
    for entry in history:
        if entry.get("stats") is not None:
            continue
        for stat in stats:
            details = stat.get("details")
            if not isinstance(details, list):
                continue
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

    # 输出摘要
    output = {
        "client": args.client,
        "period": f"{begin_str} to {end_str}",
        "stats_fetched": len(stats),
        "history_updated": updated,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
