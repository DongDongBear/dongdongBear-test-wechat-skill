/**
 * Markdown to WeChat-compatible HTML converter.
 *
 * Uses YouMind's dynamic theme engine + cheerio for robust HTML manipulation.
 * Much better HTML processing than Python's BeautifulSoup.
 */

import * as cheerio from 'cheerio';
import MarkdownIt from 'markdown-it';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

import {
  type FontFamily,
  type HeadingSize,
  type ParagraphSpacing,
  type Theme,
  type ThemeKey,
  type ThemeOptions,
  generateTheme,
} from './theme-engine.js';

export interface ConvertResult {
  html: string;
  title: string;
  digest: string;
  images: string[];
}

export interface ConverterOptions extends ThemeOptions {
  /** 是否显示 YouMind logo 水印 */
  showLogo?: boolean;
}

export class WeChatConverter {
  private theme: Theme;
  private md: MarkdownIt;
  private showLogo: boolean;

  constructor(options: ConverterOptions = {}) {
    this.theme = generateTheme(options);
    this.showLogo = options.showLogo ?? false;
    this.md = new MarkdownIt({
      html: true,
      breaks: true,
      linkify: true,
      typographer: true,
    });
  }

  getTheme(): Theme {
    return this.theme;
  }

  convert(markdownText: string): ConvertResult {
    const title = this.extractTitle(markdownText);
    markdownText = this.stripH1(markdownText);

    let html = this.md.render(markdownText);
    const $ = cheerio.load(html);

    this.enhanceCodeBlocks($);
    const images = this.processImages($);
    this.applyInlineStyles($);
    this.applyWeChatFixes($);

    if (this.showLogo) {
      this.addLogo($);
    }

    html = $('body').html() || '';
    const digest = this.generateDigest(html);

    return { html, title, digest, images };
  }

  convertFile(inputPath: string): ConvertResult {
    const absPath = resolve(inputPath);
    const text = readFileSync(absPath, 'utf-8');
    return this.convert(text);
  }

  // --- Internal Methods ---

  private extractTitle(text: string): string {
    for (const line of text.split('\n')) {
      const stripped = line.trim();
      if (stripped.startsWith('# ') && !stripped.startsWith('## ')) {
        return stripped.slice(2).trim();
      }
    }
    return '';
  }

  private stripH1(text: string): string {
    return text
      .split('\n')
      .filter((line) => {
        const stripped = line.trim();
        return !(stripped.startsWith('# ') && !stripped.startsWith('## '));
      })
      .join('\n');
  }

  private enhanceCodeBlocks($: cheerio.CheerioAPI): void {
    $('pre').each((_, pre) => {
      const code = $(pre).find('code');
      if (code.length) {
        const classes = (code.attr('class') || '').split(/\s+/);
        for (const cls of classes) {
          if (cls.startsWith('language-')) {
            $(pre).attr('data-lang', cls.replace('language-', ''));
            break;
          }
        }
      }
    });
  }

  private processImages($: cheerio.CheerioAPI): string[] {
    const images: string[] = [];
    $('img').each((_, img) => {
      const src = $(img).attr('src') || '';
      if (src) images.push(src);

      const existing = $(img).attr('style') || '';
      if (!existing.includes('max-width')) {
        const additions = 'max-width: 100%; height: auto; display: block; margin: 24px auto';
        $(img).attr('style', existing ? `${existing}; ${additions}` : additions);
      }
    });
    return images;
  }

  private applyInlineStyles($: cheerio.CheerioAPI): void {
    const s = this.theme.styles;

    // 标签 -> 样式映射
    const tagMap: Record<string, string> = {
      h1: s.h1,
      h2: s.h2,
      h3: s.h3,
      h4: s.h4,
      h5: s.h5,
      h6: s.h6,
      p: s.p,
      strong: s.strong,
      em: s.em,
      s: s.strike,
      del: s.strike,
      u: s.u,
      a: s.a,
      ul: s.ul,
      ol: s.ol,
      li: s.li,
      blockquote: s.blockquote,
      code: s.code,
      hr: s.hr,
      img: s.img,
      table: s.table,
      th: s.th,
      td: s.td,
    };

    for (const [tag, style] of Object.entries(tagMap)) {
      if (!style) continue;
      $(tag).each((_, elem) => {
        // 代码块内的 code 单独处理
        if (tag === 'code' && $(elem).parent('pre').length) return;

        const existing = $(elem).attr('style') || '';
        $(elem).attr('style', existing ? `${existing}; ${style}` : style);
      });
    }

    // 代码块: pre > code
    $('pre').each((_, pre) => {
      const code = $(pre).find('code');
      if (code.length) {
        $(pre).attr('style', s.codeBlockPre);
        code.attr('style', s.codeBlockCode);
      } else {
        const existing = $(pre).attr('style') || '';
        if (!existing) {
          $(pre).attr('style', s.pre);
        }
      }
    });

    // 表格包裹
    if (s.tableWrapper) {
      $('table').each((_, table) => {
        $(table).wrap(`<div style="${s.tableWrapper}"></div>`);
      });
    }
  }

  private applyWeChatFixes($: cheerio.CheerioAPI): void {
    const textColor = '#333333';

    // 确保所有 p 标签有显式颜色
    $('p').each((_, p) => {
      const style = $(p).attr('style') || '';
      if (!style.includes('color')) {
        $(p).attr('style', style ? `${style}; color: ${textColor}` : `color: ${textColor}`);
      }
    });

    // 确保 pre 保留空白
    $('pre').each((_, pre) => {
      const style = $(pre).attr('style') || '';
      if (!style.includes('white-space')) {
        const ws = 'white-space: pre-wrap; word-wrap: break-word';
        $(pre).attr('style', style ? `${style}; ${ws}` : ws);
      }
    });

    // 移除微信不支持的属性
    $('[class]').each((_, elem) => {
      // 保留 class 以防有用，但微信会忽略它们
    });
  }

  private addLogo($: cheerio.CheerioAPI): void {
    const logoHtml = `
      <div style="text-align: center; padding: 24px 0 8px; opacity: 0.4; font-size: 12px; color: #999;">
        Powered by YouMind
      </div>`;
    $('body').append(logoHtml);
  }

  private generateDigest(html: string, maxBytes = 120): string {
    const $ = cheerio.load(html);
    let text = $.text().replace(/\s+/g, ' ').trim();

    const ellipsis = '...';
    const encoded = Buffer.from(text, 'utf-8');
    if (encoded.length <= maxBytes) return text;

    const targetBytes = maxBytes - Buffer.byteLength(ellipsis, 'utf-8');
    // 按字符逐个裁剪，确保不截断 UTF-8 字符
    let result = '';
    let bytes = 0;
    for (const char of text) {
      const charBytes = Buffer.byteLength(char, 'utf-8');
      if (bytes + charBytes > targetBytes) break;
      result += char;
      bytes += charBytes;
    }

    return result.trimEnd() + ellipsis;
  }
}

/**
 * 生成完整 HTML 用于浏览器预览（仅本地预览，非微信发布用）
 */
export function previewHtml(bodyHtml: string, theme: Theme): string {
  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Preview - ${theme.name}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            ${theme.styles.container}
            background: #f5f5f5;
        }
        .preview-container {
            background: #ffffff;
            max-width: 720px;
            margin: 20px auto;
            padding: 32px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            border-radius: 8px;
        }
        .preview-header {
            text-align: center;
            padding: 16px 0 24px;
            border-bottom: 1px solid #eee;
            margin-bottom: 24px;
        }
        .preview-header h3 {
            margin: 0; color: #666; font-size: 14px; font-weight: 400;
        }
        .preview-header .theme-badge {
            display: inline-block;
            background: ${theme.color};
            color: #fff;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            margin-top: 8px;
        }
    </style>
</head>
<body>
    <div class="preview-container">
        <div class="preview-header">
            <h3>${theme.name} | ${theme.color}</h3>
            <span class="theme-badge">${theme.key}</span>
        </div>
        ${bodyHtml}
    </div>
</body>
</html>`;
}
