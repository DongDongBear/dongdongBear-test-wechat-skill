#!/usr/bin/env python3
"""
AI 图片生成脚本
支持 doubao (Seedream 5.0) 和 openai (GPT Image) 两个 provider
无 API key 时从 cover/ 目录中按颜色匹配预制封面

用法:
  # 生成封面 (2.35:1)
  python3 image_gen.py --prompt "..." --output cover.jpg --size cover

  # 生成配图 (16:9)
  python3 image_gen.py --prompt "..." --output img1.jpg --size article

  # 指定 provider
  python3 image_gen.py --prompt "..." --output img.jpg --provider openai

  # 匹配预制封面（无需 API key）
  python3 image_gen.py --fallback-cover --color "#3498db" --output cover.jpg
"""

import argparse
import base64
import json
import logging
import os
import sys
import time
from pathlib import Path

import requests
import yaml

logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
COVER_DIR = PROJECT_DIR / "cover"

# 封面尺寸映射
SIZE_MAP = {
    "cover": {
        "doubao": "1280x544",   # 2.35:1
        "openai": "1536x1024",  # 接近 2.35:1 的最近支持尺寸
    },
    "article": {
        "doubao": "1280x720",   # 16:9
        "openai": "1536x1024",  # 16:9 近似
    },
}

# 预制封面 -> 颜色/色调映射
COVER_PALETTE = {
    "blue-clouds-oil.jpg": {"hue": "blue", "tone": "warm", "mood": "artistic"},
    "blue-light-wave.jpg": {"hue": "blue", "tone": "cool", "mood": "tech"},
    "city-skyline-painting.jpg": {"hue": "warm", "tone": "warm", "mood": "atmospheric"},
    "cyan-gradient.jpg": {"hue": "cyan", "tone": "cool", "mood": "clean"},
    "green-gradient.jpg": {"hue": "green", "tone": "cool", "mood": "fresh"},
    "lavender-silk.jpg": {"hue": "purple", "tone": "cool", "mood": "elegant"},
    "orange-warm.jpg": {"hue": "orange", "tone": "warm", "mood": "energetic"},
    "pink-blue-diagonal.jpg": {"hue": "pink", "tone": "cool", "mood": "modern"},
    "purple-teal-diagonal.jpg": {"hue": "purple", "tone": "cool", "mood": "tech"},
    "sunset-watercolor.jpg": {"hue": "orange", "tone": "warm", "mood": "artistic"},
    "warm-colorful-blur.jpg": {"hue": "warm", "tone": "warm", "mood": "energetic"},
}

# HEX 颜色 -> 色调映射
COLOR_HUE_MAP = {
    "#3498db": "blue", "#2980b9": "blue", "#1abc9c": "cyan",
    "#e74c3c": "warm", "#c0392b": "warm", "#e91e63": "pink",
    "#2ecc71": "green", "#27ae60": "green",
    "#9b59b6": "purple", "#8e44ad": "purple",
    "#f39c12": "orange", "#f1c40f": "orange",
    "#34495e": "blue", "#2c3e50": "blue",
}


def load_config() -> dict:
    """加载项目配置"""
    config_path = PROJECT_DIR / "config.yaml"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def request_with_retry(method: str, url: str, max_retries: int = 3, **kwargs) -> requests.Response:
    """带重试的 HTTP 请求"""
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.request(method, url, **kwargs)
            resp.raise_for_status()
            return resp
        except requests.RequestException as e:
            if attempt == max_retries:
                raise
            wait = 2 ** (attempt - 1)
            logger.warning("请求失败 (第 %d/%d 次): %s — %.0f秒后重试", attempt, max_retries, e, wait)
            time.sleep(wait)
    raise RuntimeError("不应到达此处")


def generate_doubao(prompt: str, api_key: str, size: str,
                    model: str = "doubao-seedream-5-0-260128",
                    base_url: str = "https://ark.cn-beijing.volces.com/api/v3") -> bytes:
    """使用豆包 Seedream 生成图片"""
    url = f"{base_url}/images/generations"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "prompt": prompt,
        "size": size,
        "n": 1,
        "response_format": "b64_json",
    }

    logger.info("调用豆包 Seedream: model=%s, size=%s", model, size)
    resp = request_with_retry("POST", url, headers=headers, json=payload, timeout=60)
    data = resp.json()

    if "data" not in data or len(data["data"]) == 0:
        raise RuntimeError(f"豆包 API 返回异常: {json.dumps(data, ensure_ascii=False)}")

    b64 = data["data"][0].get("b64_json") or data["data"][0].get("url")
    if b64 and not b64.startswith("http"):
        return base64.b64decode(b64)

    # 如果返回的是 URL，下载图片
    if b64 and b64.startswith("http"):
        img_resp = request_with_retry("GET", b64, timeout=30)
        return img_resp.content

    raise RuntimeError("豆包 API 未返回有效图片数据")


def generate_openai(prompt: str, api_key: str, size: str,
                    model: str = "gpt-image-1",
                    base_url: str = "https://api.openai.com/v1") -> bytes:
    """使用 OpenAI GPT Image 生成图片"""
    url = f"{base_url}/images/generations"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "prompt": prompt,
        "size": size,
        "n": 1,
        "quality": "medium",
    }

    logger.info("调用 OpenAI Image: model=%s, size=%s", model, size)
    resp = request_with_retry("POST", url, headers=headers, json=payload, timeout=120)
    data = resp.json()

    if "data" not in data or len(data["data"]) == 0:
        raise RuntimeError(f"OpenAI API 返回异常: {json.dumps(data, ensure_ascii=False)}")

    item = data["data"][0]
    if "b64_json" in item:
        return base64.b64decode(item["b64_json"])
    if "url" in item:
        img_resp = request_with_retry("GET", item["url"], timeout=30)
        return img_resp.content

    raise RuntimeError("OpenAI API 未返回有效图片数据")


def select_fallback_cover(color: str = "#3498db", mood: str = "") -> Path | None:
    """从 cover/ 目录按颜色匹配预制封面"""
    if not COVER_DIR.exists():
        return None

    target_hue = COLOR_HUE_MAP.get(color.lower(), "blue")

    # 按匹配度排序
    candidates = []
    for filename, meta in COVER_PALETTE.items():
        filepath = COVER_DIR / filename
        if not filepath.exists():
            continue
        score = 0
        if meta["hue"] == target_hue:
            score += 3
        if mood and meta["mood"] == mood:
            score += 2
        if meta["tone"] == ("warm" if target_hue in ("orange", "warm") else "cool"):
            score += 1
        candidates.append((score, filepath))

    if not candidates:
        return None

    candidates.sort(key=lambda x: -x[0])
    selected = candidates[0][1]
    logger.info("匹配预制封面: %s (score=%d)", selected.name, candidates[0][0])
    return selected


def main():
    parser = argparse.ArgumentParser(description="AI 图片生成")
    parser.add_argument("--prompt", type=str, help="图片生成提示词")
    parser.add_argument("--output", "-o", type=str, required=True, help="输出文件路径")
    parser.add_argument("--size", choices=["cover", "article"], default="cover", help="图片用途/尺寸")
    parser.add_argument("--provider", choices=["doubao", "openai"], help="覆盖配置的 provider")
    parser.add_argument("--fallback-cover", action="store_true", help="使用预制封面（不调用 API）")
    parser.add_argument("--color", type=str, default="#3498db", help="主题色（用于匹配预制封面）")
    parser.add_argument("--mood", type=str, default="", help="氛围 (tech/artistic/elegant/energetic/clean)")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        stream=sys.stderr,
    )

    config = load_config()
    img_config = config.get("image", {})
    provider = args.provider or img_config.get("provider", "doubao")
    api_key = img_config.get("api_key", "")
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 模式 1: 预制封面匹配
    if args.fallback_cover:
        cover = select_fallback_cover(args.color, args.mood)
        if cover:
            import shutil
            shutil.copy2(cover, output_path)
            print(json.dumps({"status": "ok", "source": "fallback", "file": str(output_path)}))
        else:
            print(json.dumps({"status": "error", "message": "无匹配的预制封面"}))
            sys.exit(1)
        return

    # 模式 2: API 生图
    if not args.prompt:
        logger.error("--prompt 为必填参数（除非使用 --fallback-cover）")
        sys.exit(1)

    if not api_key:
        logger.warning("未配置 image.api_key，回退到预制封面匹配")
        if args.size == "cover":
            cover = select_fallback_cover(args.color, args.mood)
            if cover:
                import shutil
                shutil.copy2(cover, output_path)
                print(json.dumps({
                    "status": "ok",
                    "source": "fallback",
                    "file": str(output_path),
                    "prompt": args.prompt,
                    "message": "未配置 API key，已使用预制封面。如需 AI 生图，请在 config.yaml 中设置 image.api_key",
                }))
                return
        # 配图无法 fallback，输出 prompt 供用户手动生成
        print(json.dumps({
            "status": "prompt_only",
            "prompt": args.prompt,
            "size": args.size,
            "message": "未配置 API key，请使用以下 prompt 手动生成图片",
        }))
        sys.exit(0)

    size = SIZE_MAP[args.size][provider]
    model = img_config.get("model")
    base_url = img_config.get("base_url")

    try:
        gen_kwargs = {"prompt": args.prompt, "api_key": api_key, "size": size}
        if model:
            gen_kwargs["model"] = model
        if base_url:
            gen_kwargs["base_url"] = base_url

        if provider == "doubao":
            image_bytes = generate_doubao(**gen_kwargs)
        else:
            image_bytes = generate_openai(**gen_kwargs)

        output_path.write_bytes(image_bytes)
        logger.info("图片已保存: %s (%.1f KB)", output_path, len(image_bytes) / 1024)
        print(json.dumps({"status": "ok", "source": provider, "file": str(output_path)}))

    except Exception as e:
        logger.error("图片生成失败: %s", e)
        # 封面尝试 fallback
        if args.size == "cover":
            logger.info("尝试回退到预制封面...")
            cover = select_fallback_cover(args.color, args.mood)
            if cover:
                import shutil
                shutil.copy2(cover, output_path)
                print(json.dumps({
                    "status": "ok",
                    "source": "fallback",
                    "file": str(output_path),
                    "error": str(e),
                }))
                return
        print(json.dumps({
            "status": "error",
            "message": str(e),
            "prompt": args.prompt,
        }))
        sys.exit(1)


if __name__ == "__main__":
    main()
