# YouMind WeChat Skill

微信公众号全流程 Agent Skill：热点抓取 → 选题 → 写作 → SEO → 视觉AI → 排版发布。

## 核心特性

- **动态主题引擎**：4 主题 × 无限色，运行时生成微信内联 CSS
- **TypeScript Toolkit**：cheerio + markdown-it，比 Python 更好的 HTML 处理
- **全自动流程**：从热点到草稿箱，一口气完成
- **智能降级**：每步都有 fallback，不会因单步失败停止

## 快速开始

```bash
# 1. 安装 toolkit 依赖
cd toolkit && npm install

# 2. 安装 scripts 依赖
pip install -r requirements.txt

# 3. 配置
cp config.example.yaml config.yaml
# 编辑 config.yaml 填入 WeChat API 凭证

# 4. 预览
npx tsx src/cli.ts preview article.md --theme decoration --color "#9b59b6"

# 5. 发布
npx tsx src/cli.ts publish article.md --theme simple --color "#3498db"
```

## 项目结构

```
youmind-wechat-skill/
├── SKILL.md              # Agent Skill 定义（核心 prompt）
├── toolkit/              # TypeScript: 转换器 + 主题引擎 + CLI
│   └── src/
│       ├── theme-engine.ts    # 动态主题生成
│       ├── converter.ts       # Markdown → WeChat HTML
│       ├── cli.ts             # CLI 入口
│       ├── publisher.ts       # 微信草稿 API
│       ├── wechat-api.ts      # 微信 token + 图片上传
│       └── index.ts           # 公共 API
├── scripts/              # Python: 数据抓取
│   ├── fetch_hotspots.py      # 多平台热点
│   ├── seo_keywords.py        # SEO 关键词分析
│   ├── fetch_stats.py         # 文章数据回收
│   ├── build_playbook.py      # 语料分析
│   └── learn_edits.py         # 人工修改学习
├── references/           # 写作规范文档
├── clients/              # 客户配置
│   └── demo/
└── output/               # 生成内容
```
