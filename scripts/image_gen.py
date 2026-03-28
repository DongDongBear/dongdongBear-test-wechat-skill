#!/usr/bin/env python3
"""
AI 图片生成脚本 — YouMind WeChat Skill 配套工具

支持三个生图 provider + prompt 库搜索 + 预制封面降级:
  1. gemini   — Google Gemini Imagen (Nano Banana Pro 同款引擎)
  2. openai   — GPT Image
  3. doubao   — 豆包 Seedream 5.0

降级链: 指定 provider API → 自动选择有 key 的 provider → Nano Banana Pro 库匹配 → 预制封面 → 输出 prompt

用法:
  # 用默认 provider 生成封面
  python3 image_gen.py --prompt "..." --output cover.jpg --size cover

  # 指定 provider
  python3 image_gen.py --prompt "..." --output img.jpg --provider gemini

  # 从 Nano Banana Pro 库搜索匹配图（无需 API key）
  python3 image_gen.py --search "tech futuristic cityscape" --output img.jpg

  # 匹配预制封面
  python3 image_gen.py --fallback-cover --color "#3498db" --output cover.jpg
"""

import argparse
import base64
import json
import logging
import re
import sys
import time
from pathlib import Path

import requests
import yaml

logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
COVER_DIR = PROJECT_DIR / "cover"
NANO_BANANA_REFS = (
    PROJECT_DIR / "toolkit" / ".claude" / "skills"
    / "nano-banana-pro-prompts-recommend-skill" / "references"
)

# --- 尺寸映射 ---

SIZE_MAP = {
    "cover": {
        "gemini": "16:9",       # Imagen 用比例字符串
        "openai": "1536x1024",
        "doubao": "1280x544",
    },
    "article": {
        "gemini": "16:9",
        "openai": "1536x1024",
        "doubao": "1280x720",
    },
}

# --- 预制封面色调映射 ---

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

COLOR_HUE_MAP = {
    "#3498db": "blue", "#2980b9": "blue", "#1abc9c": "cyan",
    "#e74c3c": "warm", "#c0392b": "warm", "#e91e63": "pink",
    "#2ecc71": "green", "#27ae60": "green",
    "#9b59b6": "purple", "#8e44ad": "purple",
    "#f39c12": "orange", "#f1c40f": "orange",
    "#34495e": "blue", "#2c3e50": "blue",
}


# ============================================================
# 工具函数
# ============================================================

def load_config() -> dict:
    for p in [PROJECT_DIR / "config.yaml", PROJECT_DIR / "config.example.yaml"]:
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
    return {}


def _http(method: str, url: str, retries: int = 3, **kw) -> requests.Response:
    """带重试的 HTTP 请求"""
    for i in range(1, retries + 1):
        try:
            r = requests.request(method, url, **kw)
            r.raise_for_status()
            return r
        except requests.RequestException as e:
            if i == retries:
                raise
            wait = 2 ** (i - 1)
            logger.warning("请求失败 (%d/%d): %s — %ds 后重试", i, retries, e, wait)
            time.sleep(wait)
    raise RuntimeError("unreachable")


def resolve_provider(config: dict, explicit: str | None) -> tuple[str, dict]:
    """
    解析要使用的 provider 和对应配置。
    优先级: --provider 参数 > config.default_provider > 第一个有 key 的
    """
    img = config.get("image", {})
    providers = img.get("providers", {})

    # 兼容旧配置格式 (image.provider + image.api_key)
    if not providers and img.get("api_key"):
        old_provider = img.get("provider", "doubao")
        providers = {old_provider: {"api_key": img["api_key"], "model": img.get("model", ""), "base_url": img.get("base_url", "")}}

    if explicit:
        if explicit in providers and providers[explicit].get("api_key"):
            return explicit, providers[explicit]
        logger.warning("指定的 provider '%s' 未配置 api_key", explicit)
        return explicit, providers.get(explicit, {})

    default = img.get("default_provider", "")
    if default and default in providers and providers[default].get("api_key"):
        return default, providers[default]

    # 自动选第一个有 key 的
    for name, cfg in providers.items():
        if cfg.get("api_key"):
            logger.info("自动选择 provider: %s", name)
            return name, cfg

    return "", {}


# ============================================================
# Provider: Google Gemini / Imagen (Nano Banana Pro 同款引擎)
# ============================================================

def generate_gemini(prompt: str, api_key: str, aspect_ratio: str,
                    model: str = "imagen-3.0-generate-002") -> bytes:
    """使用 Google Imagen API 生成图片"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:predict?key={api_key}"
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": aspect_ratio,
        },
    }
    logger.info("调用 Gemini Imagen: model=%s, ratio=%s", model, aspect_ratio)
    resp = _http("POST", url, json=payload, timeout=90)
    data = resp.json()

    predictions = data.get("predictions", [])
    if not predictions:
        raise RuntimeError(f"Gemini API 无返回: {json.dumps(data, ensure_ascii=False)[:200]}")

    b64 = predictions[0].get("bytesBase64Encoded", "")
    if b64:
        return base64.b64decode(b64)
    raise RuntimeError("Gemini API 未返回图片数据")


# ============================================================
# Provider: OpenAI GPT Image
# ============================================================

def generate_openai(prompt: str, api_key: str, size: str,
                    model: str = "gpt-image-1",
                    base_url: str = "https://api.openai.com/v1") -> bytes:
    """使用 OpenAI GPT Image 生成图片"""
    url = f"{base_url}/images/generations"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model, "prompt": prompt, "size": size, "n": 1, "quality": "medium"}

    logger.info("调用 OpenAI Image: model=%s, size=%s", model, size)
    resp = _http("POST", url, headers=headers, json=payload, timeout=120)
    data = resp.json()

    items = data.get("data", [])
    if not items:
        raise RuntimeError(f"OpenAI API 无返回: {json.dumps(data, ensure_ascii=False)[:200]}")

    if "b64_json" in items[0]:
        return base64.b64decode(items[0]["b64_json"])
    if "url" in items[0]:
        return _http("GET", items[0]["url"], timeout=30).content
    raise RuntimeError("OpenAI API 未返回图片数据")


# ============================================================
# Provider: 豆包 Seedream
# ============================================================

def generate_doubao(prompt: str, api_key: str, size: str,
                    model: str = "doubao-seedream-5-0-260128",
                    base_url: str = "https://ark.cn-beijing.volces.com/api/v3") -> bytes:
    """使用豆包 Seedream 生成图片"""
    url = f"{base_url}/images/generations"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model, "prompt": prompt, "size": size, "n": 1, "response_format": "b64_json"}

    logger.info("调用豆包 Seedream: model=%s, size=%s", model, size)
    resp = _http("POST", url, headers=headers, json=payload, timeout=60)
    data = resp.json()

    items = data.get("data", [])
    if not items:
        raise RuntimeError(f"豆包 API 无返回: {json.dumps(data, ensure_ascii=False)[:200]}")

    if items[0].get("b64_json"):
        return base64.b64decode(items[0]["b64_json"])
    if items[0].get("url", "").startswith("http"):
        return _http("GET", items[0]["url"], timeout=30).content
    raise RuntimeError("豆包 API 未返回图片数据")


GENERATORS = {
    "gemini": generate_gemini,
    "openai": generate_openai,
    "doubao": generate_doubao,
}


# ============================================================
# Nano Banana Pro 库搜索 — 从 12000+ prompt 的示例图中直接取图
# ============================================================

def search_nano_banana(keywords: str, max_results: int = 3) -> list[dict]:
    """
    搜索 Nano Banana Pro prompt 库，返回匹配的 prompt + 示例图 URL。
    无需 API key，直接从本地 references/*.json 中搜索。
    """
    if not NANO_BANANA_REFS.exists():
        logger.warning("Nano Banana Pro 库未安装: %s", NANO_BANANA_REFS)
        return []

    manifest_path = NANO_BANANA_REFS / "manifest.json"
    if not manifest_path.exists():
        return []

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    terms = [t.lower() for t in keywords.split() if len(t) > 1]
    if not terms:
        return []

    results: list[tuple[int, dict]] = []

    for cat in manifest.get("categories", []):
        cat_file = NANO_BANANA_REFS / cat["file"]
        if not cat_file.exists():
            continue
        try:
            with open(cat_file, "r", encoding="utf-8") as f:
                prompts = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        for p in prompts:
            if not isinstance(p, dict):
                continue
            # 必须有示例图
            media = p.get("sourceMedia", [])
            if not media:
                continue

            # 计算匹配分数
            searchable = f"{p.get('content', '')} {p.get('title', '')} {p.get('description', '')}".lower()
            score = sum(2 if t in searchable else 0 for t in terms)
            if score > 0:
                results.append((score, p))

    results.sort(key=lambda x: -x[0])
    return [r[1] for r in results[:max_results]]


def download_nano_banana_image(url: str, output: Path) -> bool:
    """下载 Nano Banana Pro 示例图"""
    try:
        resp = _http("GET", url, timeout=30)
        output.write_bytes(resp.content)
        logger.info("从 Nano Banana Pro 库下载图片: %s (%.1f KB)", output.name, len(resp.content) / 1024)
        return True
    except Exception as e:
        logger.warning("下载 Nano Banana Pro 图片失败: %s", e)
        return False


# ============================================================
# 预制封面匹配
# ============================================================

def select_fallback_cover(color: str = "#3498db", mood: str = "") -> Path | None:
    if not COVER_DIR.exists():
        return None
    target_hue = COLOR_HUE_MAP.get(color.lower(), "blue")

    candidates = []
    for filename, meta in COVER_PALETTE.items():
        fp = COVER_DIR / filename
        if not fp.exists():
            continue
        score = 0
        if meta["hue"] == target_hue:
            score += 3
        if mood and meta["mood"] == mood:
            score += 2
        if meta["tone"] == ("warm" if target_hue in ("orange", "warm") else "cool"):
            score += 1
        candidates.append((score, fp))

    if not candidates:
        return None
    candidates.sort(key=lambda x: -x[0])
    return candidates[0][1]


# ============================================================
# 主流程
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="AI 图片生成 — YouMind WeChat Skill")
    parser.add_argument("--prompt", type=str, help="图片生成提示词")
    parser.add_argument("--search", type=str, help="从 Nano Banana Pro 库搜索关键词匹配图片（无需 API key）")
    parser.add_argument("--output", "-o", type=str, required=True, help="输出文件路径")
    parser.add_argument("--size", choices=["cover", "article"], default="cover", help="图片用途/尺寸")
    parser.add_argument("--provider", choices=["gemini", "openai", "doubao"], help="指定 provider")
    parser.add_argument("--fallback-cover", action="store_true", help="使用预制封面")
    parser.add_argument("--color", type=str, default="#3498db", help="主题色")
    parser.add_argument("--mood", type=str, default="", help="氛围 (tech/artistic/elegant/energetic)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", stream=sys.stderr)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    config = load_config()

    # --- 模式 1: 预制封面 ---
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

    # --- 模式 2: Nano Banana Pro 库搜索 ---
    if args.search:
        results = search_nano_banana(args.search)
        if results:
            best = results[0]
            url = best["sourceMedia"][0]
            if download_nano_banana_image(url, output_path):
                print(json.dumps({
                    "status": "ok",
                    "source": "nano-banana-library",
                    "file": str(output_path),
                    "prompt_title": best.get("title", ""),
                    "prompt_id": best.get("id"),
                    "original_prompt": best.get("content", "")[:200],
                    "browse": f"https://youmind.com/nano-banana-pro-prompts?id={best.get('id', '')}",
                }))
                return
            # 下载失败，继续用其他结果
            for r in results[1:]:
                if download_nano_banana_image(r["sourceMedia"][0], output_path):
                    print(json.dumps({"status": "ok", "source": "nano-banana-library", "file": str(output_path), "prompt_id": r.get("id")}))
                    return
        logger.warning("Nano Banana Pro 库未找到匹配结果: %s", args.search)
        # 降级到预制封面
        if args.size == "cover":
            cover = select_fallback_cover(args.color, args.mood)
            if cover:
                import shutil
                shutil.copy2(cover, output_path)
                print(json.dumps({"status": "ok", "source": "fallback", "file": str(output_path)}))
                return
        print(json.dumps({"status": "no_match", "search": args.search, "message": "库中无匹配，请尝试 --prompt 配合 API 生图"}))
        sys.exit(0)

    # --- 模式 3: API 生图 ---
    if not args.prompt:
        logger.error("需要 --prompt 或 --search 参数")
        sys.exit(1)

    provider_name, provider_cfg = resolve_provider(config, args.provider)

    if not provider_cfg.get("api_key"):
        logger.warning("无可用的 API key，尝试降级方案...")
        # 降级 1: 用 prompt 关键词搜索 Nano Banana Pro 库
        search_terms = re.sub(r'[,，。.!！?？"\'\-—()（）\[\]]', ' ', args.prompt)
        results = search_nano_banana(search_terms)
        if results:
            best = results[0]
            if download_nano_banana_image(best["sourceMedia"][0], output_path):
                print(json.dumps({
                    "status": "ok",
                    "source": "nano-banana-library",
                    "file": str(output_path),
                    "message": "无 API key，已从 Nano Banana Pro 库匹配示例图",
                    "prompt_id": best.get("id"),
                    "browse": f"https://youmind.com/nano-banana-pro-prompts?id={best.get('id', '')}",
                }))
                return

        # 降级 2: 预制封面
        if args.size == "cover":
            cover = select_fallback_cover(args.color, args.mood)
            if cover:
                import shutil
                shutil.copy2(cover, output_path)
                print(json.dumps({"status": "ok", "source": "fallback", "file": str(output_path), "prompt": args.prompt}))
                return

        # 降级 3: 输出 prompt
        print(json.dumps({
            "status": "prompt_only",
            "prompt": args.prompt,
            "message": "无可用 API key。请在 config.yaml 的 image.providers 中配置 gemini/openai/doubao 的 api_key，或使用 --search 搜索 Nano Banana Pro 库",
            "manual_generate": "https://youmind.com/nano-banana-pro-prompts",
        }))
        sys.exit(0)

    # 调用对应 provider
    gen_fn = GENERATORS.get(provider_name)
    if not gen_fn:
        logger.error("未知 provider: %s (支持: gemini, openai, doubao)", provider_name)
        sys.exit(1)

    size_val = SIZE_MAP[args.size].get(provider_name, SIZE_MAP[args.size]["openai"])
    gen_kwargs: dict = {"prompt": args.prompt, "api_key": provider_cfg["api_key"]}

    if provider_name == "gemini":
        gen_kwargs["aspect_ratio"] = size_val
    else:
        gen_kwargs["size"] = size_val

    if provider_cfg.get("model"):
        gen_kwargs["model"] = provider_cfg["model"]
    if provider_cfg.get("base_url"):
        gen_kwargs["base_url"] = provider_cfg["base_url"]

    try:
        image_bytes = gen_fn(**gen_kwargs)
        output_path.write_bytes(image_bytes)
        logger.info("图片已保存: %s (%.1f KB)", output_path, len(image_bytes) / 1024)
        print(json.dumps({"status": "ok", "source": provider_name, "file": str(output_path)}))

    except Exception as e:
        logger.error("%s 生图失败: %s", provider_name, e)
        # 降级到 Nano Banana Pro 库
        search_terms = re.sub(r'[,，。.!！?？"\'\-—()（）\[\]]', ' ', args.prompt)
        results = search_nano_banana(search_terms)
        if results and download_nano_banana_image(results[0]["sourceMedia"][0], output_path):
            print(json.dumps({"status": "ok", "source": "nano-banana-library", "file": str(output_path), "api_error": str(e)}))
            return

        if args.size == "cover":
            cover = select_fallback_cover(args.color, args.mood)
            if cover:
                import shutil
                shutil.copy2(cover, output_path)
                print(json.dumps({"status": "ok", "source": "fallback", "file": str(output_path), "api_error": str(e)}))
                return

        print(json.dumps({"status": "error", "message": str(e), "prompt": args.prompt}))
        sys.exit(1)


if __name__ == "__main__":
    main()
