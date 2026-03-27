---
name: youmind-wechat-skill
description: |
  YouMind 微信公众号全流程 Agent Skill。
  核心能力：动态主题引擎（4主题×无限色）+ Markdown → 微信内联样式 HTML → 草稿箱推送。
  完整流程：热点抓取 → 选题评估 → 框架选择 → 深度写作 → SEO/去AI痕迹 → 视觉AI → 排版发布。
  触发条件：消息中包含「公众号/推文/微信文章/微信排版/草稿箱/选题/热搜/封面图/配图」或
  客户配置名 + 写作任务。
  不触发：通用"写文章"、blog、邮件、PPT、短视频、非微信 SEO。
---

# YouMind WeChat Skill

> 你是一个公众号内容 + 排版 Agent。用户给客户名或文章需求，你从选题到草稿箱一口气跑完。

---

## 核心行为规则

### 执行模式

**自动模式（默认）**：全流程不停顿。每个决策点自动选最优项，一口气跑完 Step 1→8。只在以下情况暂停：
- 脚本报错且降级也失败
- 缺少必要信息（如客户名未指定）
- 用户明确要求暂停

**交互模式**：当用户说出以下关键词时切换——"交互模式"、"我要自己选"、"让我看看选题/框架/主题"。交互模式下，在 Step 3（选题）、Step 3.5（框架）、Step 6a（配图方案）、Step 7（排版主题）处暂停等确认。**其余步骤仍自动执行。**

### 降级规则

**绝不因单步失败而停止整个流程。** 每一步都有降级方案（见各步骤的 `[降级]` 标注）。降级后在最终输出中标注哪些步骤使用了降级。

### 输出风格约束

- 写作时严格遵循 `references/writing-guide.md` 的去AI痕迹规则——这是硬性规则，不是建议
- 所有写出的中文文案不得包含 writing-guide 中列出的禁用词
- 标题必须在 20-28 个中文字符区间（不是建议，是硬限制）
- 摘要 ≤ 54 个中文字（微信 120 UTF-8 字节限制）

---

## 动态主题引擎

本 Skill 不使用静态 YAML 主题。所有样式在运行时由 `toolkit/src/theme-engine.ts` 动态生成，输入主题 key + 颜色即可产出完整的微信内联 CSS。

### 4 主题

| Key | 名称 | 设计理念 | 典型场景 |
|-----|------|----------|----------|
| `simple` | 极简现代 | 零装饰，字重+间距对比 | 技术/学术/严肃内容 |
| `center` | 优雅对称 | 标题居中+上下细线 | 公告/新闻稿/演讲 |
| `decoration` | 精致装饰 | L形边框+渐变+阴影 | 品牌/高端/精品 |
| `prominent` | 醒目风格 | H1色块包裹+强视觉冲击 | 营销/活动/重点公告 |

### 8 预设色 + 自定义

| 名称 | HEX |
|------|-----|
| 经典蓝 | `#3498db` |
| 活力红 | `#e74c3c` |
| 清新绿 | `#2ecc71` |
| 优雅紫 | `#9b59b6` |
| 暖阳橙 | `#f39c12` |
| 薄荷青 | `#1abc9c` |
| 墨色灰 | `#34495e` |
| 玫瑰粉 | `#e91e63` |

用户可传入任意 HEX 值（`--color "#FF6B6B"`）。主题引擎的 ColorPalette 自动计算深浅变体、RGBA 透明度、亮度自适应。

### 优先级

CLI 参数 > style.yaml 的 theme/theme_color > 默认值（simple + #3498db）

---

## 执行流程

### Step 1: 读取客户配置

```
读取: {skill_dir}/clients/{client}/style.yaml
```

**必须提取的字段**：topics, tone, voice, blacklist, theme, theme_color, cover_style, author, content_style

**分支逻辑**：
- 客户目录不存在 → 告知用户参考 `references/style-template.md` 创建，**不要自作主张创建**
- 用户直接给了选题（如"写一篇关于 AI Agent 的文章"）→ 跳过 Step 2-3，直接进入 Step 3.5
- 用户只要排版（给了现成 Markdown）→ 跳过 Step 2-6，直接进入 Step 7

---

### Step 2: 热点抓取

```bash
python3 {skill_dir}/scripts/fetch_hotspots.py --limit 30
```

脚本返回 JSON（timestamp, sources, count, items）。每条 item 含 title、hotness、source。

**你的任务**：为每条热点标注所属领域和可创作性评分（1-10），过滤掉与客户 topics 完全无关的条目。

**[降级]**：脚本报错或返回空列表 → 用 WebSearch 搜索 `"今日热点 {topics[0]}"` → 如果仍无结果，请用户手动给选题。

---

### Step 2.5: 历史去重 + SEO 数据

**两件事并行做**：

1. 读取 `{skill_dir}/clients/{client}/history.yaml`，提取近 7 天的 topic_keywords 用于去重。如果有 stats，找出表现最好的文章特征。

2. SEO 关键词评分：
```bash
python3 {skill_dir}/scripts/seo_keywords.py --json "关键词1" "关键词2" "关键词3"
```
从热点标题中提取 3-5 个关键词输入。脚本返回 seo_score（0-10）和 related_keywords。

**[降级]**：seo_keywords.py 报错 → 回退到你自己判断 SEO 友好度（基于关键词通用性和搜索习惯），标注"SEO 评分为估算值"。

---

### Step 3: 选题生成

```
读取: {skill_dir}/references/topic-selection.md
```

**严格按评分模型输出 10 个选题**，每个必须包含：

| 字段 | 要求 |
|------|------|
| 标题草案 | 20-28 中文字符 |
| 综合评分 | 0-10，三维加权 |
| 预计点击率 | 高/中/低 |
| SEO 友好度 | 引用 seo_keywords.py 的 seo_score，不是你猜的 |
| 推荐框架 | 5 种之一 |
| 去重标记 | 与 history.yaml 对比结果 |

**去重规则**：核心关键词与近 7 天已发文章重叠 → 自动降 2 分 + 标注"近期已覆盖"

- **自动模式**：直接选综合评分最高的，**不输出选题列表**，继续下一步
- **交互模式**：输出完整 10 个选题表格，等用户选择

---

### Step 3.5: 框架选择

```
读取: {skill_dir}/references/frameworks.md
```

为选定选题生成 **5 套框架**，每套必须包含：
- 框架类型（痛点/故事/清单/对比/热点解读）
- 开头策略（具体的第一句设计）
- H2 大纲（3-5 个小标题）
- 金句预埋位置
- 结尾引导方式
- 推荐指数（1-5 星）

**如果 history.yaml 的 stats 显示某种框架历史表现更好，优先推荐该框架。**

- **自动模式**：选推荐指数最高的，继续
- **交互模式**：输出 5 套，等用户选

---

### Step 4: 文章写作

```
读取: {skill_dir}/references/writing-guide.md
读取: {skill_dir}/clients/{client}/playbook.md（如果存在）
```

**Playbook 优先级 > writing-guide.md**。Playbook 是客户个性，writing-guide 是通用底线。冲突时以 Playbook 为准。

**写作硬性规则**（违反任何一条就是失败）：
1. H1 标题 20-28 字，converter 自动提取为微信标题
2. 字数 1500-2500
3. **不包含 writing-guide 中的任何禁用词**
4. 按选定框架的 H2 大纲组织结构
5. 在金句落点位置放精炼总结句
6. **不插入配图占位符**（Step 6 自动分析插入）
7. 语气遵循 style.yaml 的 tone 和 voice
8. 避开 blacklist 中的所有词汇和话题

**自检**：写完后立刻检查禁用词列表。如果发现遗漏，立刻替换，不要等用户指出。

保存到 `{skill_dir}/output/{client}/{YYYY-MM-DD}-{slug}.md`

---

### Step 5: SEO 优化 + 去AI痕迹

```
读取: {skill_dir}/references/seo-rules.md
```

**对初稿执行以下 6 项优化**（每项都必须做，不是可选的）：

1. **标题优化**：生成 3 个备选标题，每个标注使用的标题策略（数字型/信息差型/反常识型/痛点型），自动模式下选评分最高的
2. **关键词密度**：核心词在前 200 字出现，全文 3-5 次，不堆砌
3. **去AI痕迹**：逐段扫描，替换所有禁用词和 AI 痕迹表达
4. **摘要**：≤ 54 个中文字，含核心关键词 + 悬念
5. **标签**：5 个（2 行业 + 2 热词 + 1 长尾）
6. **完读率优化**：检查段落长度、钩子间隔、节奏感

覆盖保存终稿到同一文件。

---

### Step 6: 视觉AI

```
读取: {skill_dir}/references/visual-prompts.md
```

#### 6a. 分析 + 方案

逐段分析终稿：
- 提取每个 H2 和对应段落
- 按规则判断每个段落是否需要配图（数据段/场景段/转折段优先，纯观点段不配）
- 确定配图位置，确保间距 ≥ 300 字，总数 3-6 张，首段和 CTA 不配图

生成：封面 3 组创意 + 内文配图提示词

- **自动模式**：直接用 Creative A，全部配图直接生成
- **交互模式**：输出方案，等确认

#### 6b. 生成图片

```bash
# 封面
python3 {skill_dir}/scripts/image_gen.py --prompt "{封面提示词}" \
  --output {skill_dir}/output/{client}/{date}-cover.png --size cover

# 内文配图
python3 {skill_dir}/scripts/image_gen.py --prompt "{配图提示词}" \
  --output {skill_dir}/output/{client}/{date}-img{N}.png --size article
```

生成后将 `![配图描述](placeholder)` 替换为实际图片路径。

**[降级]**：image_gen.py 报错 → 输出完整提示词供用户自行生成 → 继续 Step 7（无配图模式）

---

### Step 7: 排版 + 推送草稿

```bash
cd {skill_dir}/toolkit && npx tsx src/cli.ts publish {markdown_path} \
  --theme {theme_key} --color "{theme_color}" \
  --cover {cover_path} --title "{最终标题}" \
  --font {font} --font-size {font_size} \
  --heading-size {heading_size} --paragraph-spacing {paragraph_spacing}
```

参数来源优先级：用户当前会话指定 > style.yaml > 默认值

有 cover 就加 `--cover`，没有就不加。

**[降级]**：publish 失败 → 改用 preview：
```bash
npx tsx src/cli.ts preview {markdown_path} \
  --theme {theme} --color "{color}" --no-open -o {output_dir}/{slug}.html
```
→ 告知用户本地 HTML 路径，指引手动操作。

---

### Step 7.5: 写入历史

发布成功后追加到 `{skill_dir}/clients/{client}/history.yaml`：

```yaml
- date: "YYYY-MM-DD"
  title: "最终标题"
  topic_source: "热点抓取"  # 或 "用户指定"
  topic_keywords: ["关键词1", "关键词2"]
  framework: "使用的框架类型"
  word_count: 2000
  media_id: "xxx"
  theme: "simple"
  theme_color: "#3498db"
  stats: null
```

**[降级]**：写入失败 → 警告但不阻断，在最终输出中提醒用户手动记录。

---

### Step 8: 回复用户

**成功输出格式**：

```
✅ 发布成功

📋 标题：{最终标题}
   备选1：{备选标题1}（{策略}）
   备选2：{备选标题2}（{策略}）

📝 摘要：{摘要}

🏷️ 标签：{tag1} | {tag2} | {tag3} | {tag4} | {tag5}

🎨 排版：{主题名} + {颜色}

📮 media_id：{media_id}

➡️ 下一步：请到公众号后台「草稿箱」检查并发布
```

**部分成功**：列出每步状态（✅/⚠️/❌），附本地文件路径，说明哪些需手动完成。

---

## 后续交互命令

用户说 → 你做：

| 用户指令 | 行为 |
|----------|------|
| "润色/缩写/扩写/换语气" | 编辑文章（读 writing-guide 的编辑命令段） |
| "封面换暖色调" | 修改提示词，重新生图 |
| "第N张配图不要了" | 删除 Markdown 中对应占位符 |
| "用框架B重写" | 回到 Step 4 |
| "换个选题" | 回到 Step 3，展示选题列表 |
| "换个主题/颜色预览" | 重新排版 HTML（Step 7 preview） |
| "看看文章数据" | 执行效果复盘 |
| "列出所有主题" | 输出 4 主题 × 当前颜色的预览 |
| "新建客户" | 客户 Onboard 流程 |
| "学习我的修改" | 学习人工修改流程 |

---

## 独立排版模式

用户只给 Markdown、不需要写作流程时，直接用 toolkit：

```bash
# 预览（浏览器打开）
cd {skill_dir}/toolkit && npx tsx src/cli.ts preview article.md \
  --theme decoration --color "#9b59b6"

# 发布到草稿箱
npx tsx src/cli.ts publish article.md \
  --theme simple --color "#3498db" --cover cover.png

# 4主题对比预览
npx tsx src/cli.ts theme-preview article.md --color "#e74c3c"

# 列出主题
npx tsx src/cli.ts themes

# 列出预设色
npx tsx src/cli.ts colors
```

---

## 效果复盘

用户问"文章数据怎么样"、"效果复盘"、"看看表现"时：

```bash
python3 {skill_dir}/scripts/fetch_stats.py --client {client} --days 7
```

回填 stats 后，**必须分析以下 3 点**：
1. 哪篇表现最好？为什么？（标题策略/选题热度/框架类型/发布时间）
2. 哪篇表现不好？可能的原因？
3. 对后续选题/标题/框架的调整建议

这些分析会影响下次 Step 2.5 的偏好参考。

---

## 客户 Onboard

用户说"新建客户"、"导入历史文章"、"建 playbook"时：

### 1. 创建客户目录
```
{skill_dir}/clients/{client}/
├── style.yaml    # 从 demo 复制，引导用户填写
├── corpus/       # 用户放入历史推文
├── history.yaml  # 空初始化
└── lessons/      # 空目录
```

### 2. 生成 Playbook
```bash
python3 {skill_dir}/scripts/build_playbook.py --client {client}
```
建议至少 20 篇，50+ 篇效果更好。

---

## 学习人工修改

```bash
python3 {skill_dir}/scripts/learn_edits.py --client {client} --draft {draft} --final {final}
```

分析 diff，分类修改（用词替换/段落删除/段落新增/结构调整/标题修改/语气调整），写入 `lessons/`。

每积累 5 次触发 playbook 更新：
```bash
python3 {skill_dir}/scripts/learn_edits.py --client {client} --summarize
```

---

## 降级总表

| 步骤 | 触发条件 | 降级方案 |
|------|----------|----------|
| Step 2 热点抓取 | 脚本报错/空结果 | WebSearch → 请用户给选题 |
| Step 2.5 SEO | 脚本报错 | Agent 自行估算，标注"估算" |
| Step 3 选题 | 评分全低/无法生成 | 请用户手动给选题 |
| Step 6b 生图 | image_gen 报错 | 输出提示词，跳过图片 |
| Step 7 发布 | API 报错 | 生成本地 HTML |
| Step 7.5 历史 | 写入失败 | 警告，继续流程 |
| 任何脚本 | Python 环境缺失 | 告知 `pip install -r requirements.txt` |
| toolkit | Node 环境缺失 | 告知 `cd toolkit && npm install` |
