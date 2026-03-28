# WeChat Theme DSL Specification

> 自定义主题的领域特定语言规范。AI 根据此规范为用户生成微信公众号文章主题，
> 生成结果为完整的 ThemeStyles JSON，存储在本地供复用。

---

## 架构概览

主题由两层组成：

| 层 | 职责 | 约束程度 |
|---|------|---------|
| **Tokens** | 颜色、字体、字号、间距 | 严格约束（微信硬限制） |
| **Styles** | 27 个元素的 CSS 字符串 | 自由创作（仅限安全 CSS 属性） |

```
用户描述 ("赛博朋克风、霓虹绿")
        ↓
  AI 读取本规范
        ↓
  生成 Tokens + Styles
        ↓
  输出 JSON → ${CLAUDE_PLUGIN_DATA}/themes/<name>.json
        ↓
  下次使用时直接加载 styles 对象
```

---

## 一、Tokens 层（严格约束）

### 1.1 颜色

单一主色，系统通过 `ColorPalette` 类自动派生：

| 派生色 | 算法 | 用途 |
|--------|------|------|
| `primary` | 原色 | 标题、强调、链接 |
| `primaryDark` | 暗化 20% | 深色变体 |
| `primaryLight` | 亮化 20% | 浅色变体 |
| `primaryLightest` | 与白色 10% 混合 | 极浅背景 |
| `background` | 与白色 5% 混合 | 容器背景 |
| `rgba(alpha)` | 原色 + 透明度 | 边框、阴影、遮罩 |

**规则：**
- 正文颜色禁止纯黑 `#000000`，使用 `#2c2c2c` 或 `#3f3f3f`
- 辅助文字色（引用、注释）使用 `#555555` 或 `#888888`
- 遵守三色规则：主题色 + 正文色 + 辅助色

### 1.2 字体（白名单，不可自定义）

| Key | Font Stack | 场景 |
|-----|-----------|------|
| `default` | `PingFang SC, system-ui, -apple-system, BlinkMacSystemFont, Helvetica Neue, Hiragino Sans GB, Microsoft YaHei UI, Microsoft YaHei, Arial, sans-serif` | 通用、现代 |
| `optima` | `Georgia, Microsoft YaHei, PingFangSC, serif` | 文艺、杂志 |
| `serif` | `Optima-Regular, Optima, PingFangSC-light, PingFangTC-light, "PingFang SC", Cambria, Cochin, Georgia, Times, "Times New Roman", serif` | 古典、学术 |

**禁止** `@font-face` 或白名单外的任意字体名。

### 1.3 字号

| 元素 | 范围 | 默认 | 备注 |
|------|------|------|------|
| 正文 `fontSize` | 14-18px | 16px | 微信最佳阅读 15-16px |
| h1 | 22-30px | 26px | — |
| h2 | 19-26px | 22px | — |
| h3 | 17-22px | 19px | — |
| h4 | 16-20px | 18px | 不小于正文 |
| h5 | 15-18px | 16px | 可等于正文 |
| h6 | 14-17px | 15px | 可小于正文 |
| 行内代码 | 13-15px 或 0.9em | 14px | — |
| 代码块 | 13-15px | 14px | — |
| 引用块 | 14-16px | 15px | 可略小于正文 |
| 表头 | 14-16px | 15px | — |
| 表格正文 | 14-16px | 15px | — |

可以通过两种方式指定标题字号（二选一）：
- `headingScale`: `minus2 | minus1 | standard | plus1`（按比例缩放）
- `headingSizes`: `{ h1: 26, h2: 22, h3: 19, h4: 18, h5: 16, h6: 15 }`（精确指定）

### 1.4 间距

| 参数 | 范围 | 默认 | 说明 |
|------|------|------|------|
| `paragraphSpacing` | 8-32px | 20px | 段落间距 (`compact`=12 / `normal`=20 / `loose`=28) |
| `lineHeight` | 1.5-2.0 | 1.75 | 正文行高 |
| `headingLineHeight` | 1.2-1.6 | 1.4 | 标题行高 |
| `containerPadding` | 4-16px | 8px | 外层容器内边距 |
| `listItemSpacing` | 0-10px | 4px | 列表项间距 |
| `codeBlockMargin` | 16-36px | 28px | 代码块上下外边距 |
| `imageMargin` | 16-36px | 28px | 图片上下外边距 |
| `hrMargin` | 24-64px | 40px | 分割线上下外边距 (px 或 rem) |
| `tableMargin` | 8-20px | 12px | 表格上下外边距 |
| `blockquotePadding` | 8-24px | 16px | 引用块内边距 |

---

## 二、Styles 层（自由创作）

### 2.1 ThemeStyles 完整 Key 列表

生成的主题必须包含以下 **全部 32 个 key**，每个 key 的值为一个 CSS 内联样式字符串：

| Key | 对应元素 | 说明 |
|-----|---------|------|
| `container` | 最外层容器 | max-width, padding, font-family, font-size, line-height |
| `h1` | 一级标题 | 字号、颜色、字重、间距、装饰 |
| `h2` | 二级标题 | 同上，通常比 h1 小一级 |
| `h3` | 三级标题 | 同上 |
| `h4` | 四级标题 | 同上 |
| `h5` | 五级标题 | 同上 |
| `h6` | 六级标题 | 同上 |
| `p` | 段落 | 间距、行高、字号、颜色 |
| `strong` | 加粗 | 字重、颜色 |
| `em` | 斜体 | font-style、颜色 |
| `strike` | 删除线 | text-decoration、透明度 |
| `u` | 下划线 | text-decoration 样式 |
| `a` | 链接 | 颜色、装饰样式 |
| `ul` | 无序列表 | padding、list-style |
| `ol` | 有序列表 | padding、list-style |
| `li` | 列表项 | 间距、行高 |
| `liText` | 列表项文字 | 颜色继承 |
| `taskList` | 任务列表容器 | padding、list-style: none |
| `taskListItem` | 任务列表项 | 行高 |
| `taskListItemCheckbox` | 复选框 | 尺寸、accent-color |
| `blockquote` | 引用块 | 边框、背景、字体样式 |
| `code` | 行内代码 | 字体、背景、圆角 |
| `pre` | 代码块外层 | 背景、边距、边框 |
| `hr` | 分割线 | 样式、宽度、高度 |
| `img` | 图片 | max-width、圆角、阴影 |
| `tableWrapper` | 表格外层 | padding、overflow |
| `table` | 表格 | border-collapse、字号 |
| `th` | 表头单元格 | 背景、字重、边框 |
| `td` | 表格单元格 | padding、边框 |
| `tr` | 表格行 | 可为空字符串 |
| `codeBlockPre` | 代码块 pre | 背景色、圆角、阴影 |
| `codeBlockCode` | 代码块 code | 字体、颜色、行高 |

### 2.2 微信安全 CSS 属性

生成 styles 时**只能使用**以下属性：

**可用：**
```
color, background-color, background-image (仅 linear-gradient)
background-size, background-position, background-repeat
font-size, font-weight, font-style, font-family (白名单内)
margin, margin-top, margin-bottom, margin-left, margin-right
padding, padding-top, padding-bottom, padding-left, padding-right
border, border-left, border-right, border-top, border-bottom
border-radius, border-collapse, border-color, border-style, border-width
text-align, text-decoration, text-decoration-color, text-indent
text-underline-offset, text-shadow
letter-spacing, line-height, word-break, word-wrap, white-space
display (block / inline / inline-block), overflow, overflow-x, overflow-y
max-width, max-height, width, height
opacity, box-shadow
list-style-type, list-style, vertical-align
accent-color, cursor
```

**禁止：**
```
position: fixed / sticky
transform, animation, transition, @keyframes
filter, backdrop-filter
CSS Variables (var(--xxx))
CSS Grid (display: grid)
Flexbox (display: flex)
@font-face
media queries
::before, ::after (不可靠)
float (微信行为不一致)
```

### 2.3 创作指南

生成 styles 时的核心原则：

1. **每个 `<p>` 必须有显式 `color`** — 微信不从父级继承颜色
2. **所有值为内联样式字符串** — 不能用 class、不能用 `<style>` 块
3. **`!important` 的使用** — margin、line-height、color 等容易被微信覆盖的属性建议加 `!important`
4. **颜色使用 ColorPalette** — 用 `${p.primary}`, `${p.rgba(0.1)}` 等引用方式描述，生成时计算为真实值
5. **font-family 必须带完整 fallback** — 直接引用白名单中的完整字体栈字符串
6. **表格不超过 4 列** — 移动端屏幕限制
7. **box-shadow 谨慎使用** — 部分老旧微信客户端渲染异常，建议值保持较小

---

## 三、输出 JSON 格式

```jsonc
{
  // 元信息
  "meta": {
    "id": "magazine-elegant",           // 唯一标识, kebab-case
    "name": "优雅杂志",                  // 显示名称
    "description": "衬线字体，居中标题带上下细线，适合长文深度阅读",
    "tags": ["elegant", "magazine", "serif", "centered"],
    "createdAt": "2026-03-28",
    "version": 1
  },

  // Tokens 层 — 严格约束
  "tokens": {
    "color": "#9b59b6",
    "fontFamily": "serif",
    "fontSize": 16,
    "headingSizes": { "h1": 26, "h2": 22, "h3": 19, "h4": 17, "h5": 16, "h6": 15 },
    "lineHeight": 1.75,
    "paragraphSpacing": 20,
    "containerPadding": 8
  },

  // Styles 层 — 完整的 32 个 CSS 字符串
  "styles": {
    "container": "max-width: 720px; margin: 0 auto; padding: 8px; font-family: ...; font-size: 16px; line-height: 1.75 !important; word-wrap: break-word;",
    "h1": "...",
    "h2": "...",
    "h3": "...",
    "h4": "...",
    "h5": "...",
    "h6": "...",
    "p": "...",
    "strong": "...",
    "em": "...",
    "strike": "...",
    "u": "...",
    "a": "...",
    "ul": "...",
    "ol": "...",
    "li": "...",
    "liText": "...",
    "taskList": "...",
    "taskListItem": "...",
    "taskListItemCheckbox": "...",
    "blockquote": "...",
    "code": "...",
    "pre": "...",
    "hr": "...",
    "img": "...",
    "tableWrapper": "...",
    "table": "...",
    "th": "...",
    "td": "...",
    "tr": "...",
    "codeBlockPre": "...",
    "codeBlockCode": "..."
  }
}
```

---

## 四、Gotchas

1. **字体陷阱** — 不要写 `font-family: "Noto Sans SC"` 这种用户设备上可能没有的字体，只用白名单三选一
2. **颜色继承** — 微信的 `<p>` 不继承父级 color，必须每个 p 都写 `color: #xxx !important`
3. **背景渐变** — 只支持 `linear-gradient`，不支持 `radial-gradient`、`conic-gradient`
4. **圆角 + 溢出** — `border-radius` 配合 `overflow: hidden` 在微信中偶有渲染问题，代码块慎用大圆角
5. **行高覆盖** — 微信编辑器可能注入行高，务必加 `!important`
6. **深色背景 + 浅色文字** — 如果 container 用深色背景，所有子元素必须显式设置浅色 `color`（不会继承）
7. **shadow 兼容性** — `box-shadow` 在微信 Android 7.x 以下可能无效，作为装饰增强而非核心设计元素
8. **表格宽度** — 移动端表格必须 `min-width: 100%`，不能固定 px 宽度
9. **img max-height** — 建议限制 `max-height: 600px` 防止超长图片撑破布局
10. **代码字体** — 等宽字体栈用 `"SF Mono", Consolas, Monaco, monospace`，不可自定义
