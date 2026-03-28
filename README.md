# YouMind WeChat Skill

微信公众号全流程 Agent Skill：热点抓取 → 选题 → 写作 → SEO → 视觉AI → 排版发布。

## 核心特性

- **动态主题引擎**：4 主题 × 无限色，运行时生成微信内联 CSS
- **TypeScript Toolkit**：cheerio + markdown-it，比 Python 更好的 HTML 处理
- **全自动流程**：从热点到草稿箱，一口气完成
- **智能降级**：每步都有 fallback，不会因单步失败停止
- **自校验机制**：校验 skill 元数据、文档、命令入口和目录结构是否漂移

## 快速开始

```bash
# 1. 安装 toolkit 依赖
cd toolkit && npm install

# 2. 构建 deterministic toolkit commands
npm run build

# 3. 安装 Python scripts 依赖
cd ..
pip install -r requirements.txt

# 4. 配置
cp config.example.yaml config.yaml
# 编辑 config.yaml 填入 WeChat API 凭证

# 5. 校验 skill 结构和文档是否一致
cd toolkit && npm run validate-skill

# 6. 预览
node dist/cli.js preview ../article.md --theme decoration --color "#9b59b6"

# 7. 发布
node dist/cli.js publish ../article.md --theme simple --color "#3498db"
```

## 项目结构

```
youmind-wechat-skill/
├── SKILL.md                    # Agent Skill 定义（触发条件 + 主流程）
├── agents/openai.yaml          # UI / marketplace 元数据
├── references/                 # 渐进式披露的参考文档
│   ├── pipeline.md             # 文章主流程
│   ├── operations.md           # 运营与维护操作
│   ├── cli-reference.md        # toolkit 命令参考
│   └── skill-maintenance.md    # 仅维护 skill 本身时才读
├── scripts/                    # Python: 数据抓取与 skill 自校验
│   ├── fetch_hotspots.py       # 多平台热点
│   ├── seo_keywords.py         # SEO 关键词分析
│   └── validate_skill.py       # 结构/文档一致性校验
├── toolkit/                    # TypeScript toolkit 与 deterministic entrypoints
│   ├── src/
│   │   ├── cli.ts              # 预览 / 发布 / 主题命令
│   │   ├── converter.ts        # Markdown → WeChat HTML
│   │   ├── theme-engine.ts     # 主题系统
│   │   ├── image-gen.ts        # 封面与配图生成
│   │   ├── youmind-api.ts      # YouMind 知识库与搜索
│   │   ├── fetch-stats.ts      # 微信文章数据回收
│   │   ├── build-playbook.ts   # 从历史语料生成 playbook
│   │   └── learn-edits.ts      # 从人工修改里抽取经验
│   └── dist/                   # build 后供 skill 调用的 JS 入口
├── clients/                    # 客户配置、历史、语料、经验
│   └── demo/
├── themes/                     # 内置/自定义主题
├── cover/                      # 预置封面 fallback 资源
└── output/                     # 生成产物（git 忽略）
```

## 常用命令

所有命令都在 `toolkit/` 下运行：

```bash
cd toolkit

# 核心流程
npm run preview -- ../article.md --theme simple --color "#3498db"
npm run publish -- ../article.md --theme decoration --color "#9b59b6"
npm run theme-preview -- ../article.md --color "#3498db"

# 配套工具
npm run image-gen -- --search "AI 教育 插画"
npm run youmind-api -- search "高考 志愿"
npm run fetch-stats -- --client demo --days 7
npm run build-playbook -- --client demo
npm run learn-edits -- --client demo --summarize

# Skill 自校验
npm run validate-skill
```

## 架构说明

- `SKILL.md` 只保留高频执行流程和关键护栏，详细规范下沉到 `references/`，符合渐进式披露。
- 高风险或高重复步骤尽量走 `toolkit/src/*.ts` / `scripts/*.py`，减少靠 prompt 复述命令。
- `agents/openai.yaml` 负责分发层元数据，避免把 UI 信息混进主 skill prompt。
- `scripts/validate_skill.py` 用来阻止 `README`、`SKILL.md`、命令入口和文件布局继续漂移。
