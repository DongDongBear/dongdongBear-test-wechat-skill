# WeChat 自定义主题设计语言

> 这不是一份 CSS 属性清单。这是一套设计思维框架。
>
> AI 在生成主题时，必须先完成设计思考（第一部分），再翻译为 CSS 实现（第二部分）。
> 跳过设计思考直接写 CSS = 垃圾主题。

---

## 第一部分：设计思考（必须先完成）

### 1. 情绪定位

每个主题的起点是一个情绪。不是"蓝色"，不是"左对齐"，而是：

**这篇文章读起来应该是什么感觉？**

| 情绪方向 | 设计语言特征 | 反面 |
|---------|------------|------|
| 肃穆庄重 | 衬线体、居中、宽字距、上下细线框、大留白 | 不是"什么都没有"，是仪式感 |
| 科技未来 | 无衬线、锐利边角、深色代码块、发光描边、紧凑节奏 | 不是"加 rgba 就行"，是信息密度感 |
| 文艺温暖 | 衬线体、首行缩进、暖灰色调、圆角引用卡片、宽松行高 | 不是"加圆角就行"，是纸质书的触感 |
| 商务专业 | 无衬线、左对齐、粗边框标题、表格强调、紧凑间距 | 不是"无聊"，是信任感和权威感 |
| 活泼轻快 | 大字号标题、色块背景、圆角卡片、紧凑段间距 | 不是"花哨"，是节奏感和能量 |

先用一句话写下情绪定位，再继续。

### 2. 视觉性格

确定主题的"人格"——如果这个排版是一个人，他是什么样的？

需要回答三个问题：

**声量** — 这个主题是在低声说话，还是在演讲？
- 低声：字重 500-600、标题不加背景色、装饰元素半透明
- 正常：字重 600-700、适度装饰、清晰但不抢眼
- 演讲：字重 700-800、标题带色块背景、强对比

**温度** — 暖色系还是冷色系？
- 冷：石板灰、靛蓝、青灰 → 理性、距离、沉思
- 中性：纯灰调、极少彩色 → 克制、专业
- 暖：赭石、琥珀、暖棕 → 亲切、叙事、人文

**密度** — 页面上的元素有多紧凑？
- 疏朗：段间距 24-28px、行高 1.8-2.0、大量留白 → 沉淀、阅读感
- 适中：段间距 18-22px、行高 1.7-1.8 → 平衡
- 紧凑：段间距 12-16px、行高 1.6-1.7 → 信息量、效率感

### 3. 层级策略

标题不只是"大字"。它是文章的骨架，是读者扫读时的导航。

**层级的建立方式**（可组合使用）：

| 手段 | 效果 | 示例 |
|------|------|------|
| 字号差异 | 最直接的层级信号 | H1 24px → H2 20px → H3 18px |
| 字重变化 | 在同字号下制造轻重差 | H1 700 → H3 600 → H5 500 |
| 颜色深浅 | 越高层级颜色越深 | H1 #3a3a3a → H3 #5a6374 |
| 装饰递减 | 装饰从丰富到消失 | H1 双线框 → H2 底部短线 → H3 无装饰 |
| 对齐切换 | 高层级居中，低层级左对齐 | H1-H2 居中 → H3+ 左对齐 |
| 间距节奏 | 层级越高，上方留白越大 | H1 margin-top 48px → H3 32px |

**关键原则：不要只用一种手段。** 最好的层级是多种手段叠加形成的"整体感"。

### 4. 节奏设计

文章的"呼吸"——读者的眼睛什么时候紧张，什么时候放松。

- **标题前的大留白** — 让读者知道"新的一节开始了"
- **段落间的适度间距** — 每段之间的停顿，像说话时的换气
- **引用块的"暂停"** — 视觉上明显不同于正文，让读者放慢速度
- **分割线的"深呼吸"** — 比段落间距更长的停顿，标记大的语境切换
- **列表的"节拍"** — 信息的有序呈现，比段落更紧凑但更结构化

### 5. 装饰哲学

每一个装饰元素都必须回答：**"你为什么在这里？"**

| 装饰 | 好的理由 | 坏的理由 |
|------|---------|---------|
| 标题左边框 | 制造层级信号，引导视线 | "其他主题都有" |
| 标题背景色块 | 制造视觉重心，强调重要性 | "看起来酷" |
| 引用块渐变背景 | 在正文中制造"暂停区"的氛围 | "加点颜色" |
| 代码块深色背景 | 与正文形成"语境切换"的信号 | "程序员喜欢深色" |
| 标题底部居中短线 | 在居中排版中制造收束感 | "装饰一下" |
| 上下双线框 | 制造仪式感、纪念碑铭文感 | "好看" |

**核心原则：装饰是设计意图的表达，不是填充。**

### 6. 色彩情绪

只需要一个主色。ColorPalette 自动派生其他色阶。

但选色不是选一个"好看的颜色"，是选一种**情绪光线**。颜色与情绪的关系不是固定公式，同一个蓝色在不同语境下可以是信任、忧郁或科技感。以下是一些参考方向，不是唯一答案：

| 色彩倾向 | 可能传递的情绪 | 参考色值（仅举例） |
|---------|--------------|------------------|
| 低饱和蓝灰 | 沉思、克制、专业 | #5a6374 附近 |
| 暖棕/赭石 | 叙事、人文、怀旧 | #8b6f47 附近 |
| 深绿 | 沉稳、自然、生长 | #2c5f2d 附近 |
| 暗紫 | 神秘、创意、深邃 | #6b4c9a 附近 |
| 深红/暗红 | 力量、紧迫、警醒 | #c0392b 附近 |
| 深蓝/墨蓝 | 科技、前沿、深邃 | #1a1a2e 附近 |
| 琥珀/暖金 | 温情、秋日、回忆 | #d4a373 附近 |

实际选色时，应该根据文章的具体内容和情绪自由选择。同一篇科技文章，如果偏冷峻分析可以用墨蓝，如果偏温暖叙事也可以用暖灰。不要被表格限制住。

**三色规则：** 主题色（标题、装饰）+ 正文色（深灰区间，如 #2c2c2c ~ #3f3f3f）+ 辅助色（引用、注释用的中灰）。超过三个色系容易失控，但具体值根据主题自由调配。

---

## 第二部分：CSS 实现

完成设计思考后，将设计决策翻译为 32 个 ThemeStyles CSS 字符串。

### 1. 32 个 ThemeStyles Key

| Key | 对应元素 | 设计职责 |
|-----|---------|---------|
| `container` | 最外层容器 | 设定全局字体、字号、行高、最大宽度 |
| `h1` | 一级标题 | 文章的"门面"，承载最强的设计表达 |
| `h2` | 二级标题 | 章节分隔，层级递减但风格延续 |
| `h3` | 三级标题 | 小节标记，装饰继续递减 |
| `h4` - `h6` | 更低层级标题 | 通常纯文字，靠字号和字重区分 |
| `p` | 段落 | 阅读的主体，行高和间距决定舒适度 |
| `strong` | 加粗 | 行内强调，颜色和字重要与正文有区分 |
| `em` | 斜体 | 行内弱强调 |
| `strike` | 删除线 | 标记废弃内容 |
| `u` | 下划线 | 行内标记 |
| `a` | 链接 | 可点击信号，通常用主色+底线 |
| `ul` / `ol` | 列表容器 | 列表标记颜色通常用主色（淡化） |
| `li` / `liText` | 列表项 | 控制行内间距和缩进 |
| `taskList` / `taskListItem` / `taskListItemCheckbox` | 任务列表 | 交互元素，accent-color 用主色 |
| `blockquote` | 引用块 | 阅读节奏中的"暂停区"，核心设计元素 |
| `code` | 行内代码 | 小型语境切换信号 |
| `pre` | 代码块外层 | 大型语境切换 |
| `hr` | 分割线 | 文章节奏中的"深呼吸" |
| `img` | 图片 | 视觉焦点，通常居中+适度留白 |
| `tableWrapper` / `table` / `th` / `td` / `tr` | 表格 | 结构化数据展示 |
| `codeBlockPre` / `codeBlockCode` | 代码块 | 与正文完全不同的视觉领地 |

### 2. 字体白名单

微信不支持 `@font-face`。只能从以下三个字体栈中选择：

| Key | 字体栈 | 性格 |
|-----|-------|------|
| `default` | PingFang SC, system-ui, -apple-system, BlinkMacSystemFont, Helvetica Neue, Hiragino Sans GB, Microsoft YaHei UI, Microsoft YaHei, Arial, sans-serif | 现代、清晰、中性 |
| `optima` | Georgia, Microsoft YaHei, PingFangSC, serif | 文艺、杂志、温润 |
| `serif` | Optima-Regular, Optima, PingFangSC-light, PingFangTC-light, "PingFang SC", Cambria, Cochin, Georgia, Times, "Times New Roman", serif | 古典、庄重、时间感 |

字体选择应该与情绪定位匹配。庄重用衬线，现代用无衬线，文艺用 optima。

### 3. 字号约束

| 元素 | 安全范围 | 备注 |
|------|---------|------|
| 正文 | 14-18px | 微信最佳 15-16px |
| H1 | 22-30px | 不宜过大，克制 > 张扬 |
| H2 | 19-26px | — |
| H3 | 17-22px | — |
| H4-H6 | 14-18px | 可等于或略小于正文 |
| 代码 | 13-15px | 等宽字体用 SF Mono/Consolas/Monaco |
| 引用/表格 | 14-16px | 可略小于正文 |

### 4. 设计手法速查

以下是可在微信安全 CSS 范围内实现的常用设计手法：

**标题装饰：**
- 居中 + 上下双细线（仪式感）：`text-align: center; border-top: 1px solid; border-bottom: 1px solid; padding: 20px 16px;`
- 居中 + 底部短线（章节感）：`text-align: center; padding-bottom: 14px; background-image: linear-gradient(...); background-size: 32px 1px; background-position: center bottom; background-repeat: no-repeat;`
- 左侧粗边框（力量感）：`border-left: 4px solid; padding-left: 14px;`
- 左侧渐变背景（科技感）：`background: linear-gradient(90deg, rgba(...,0.08) 0%, transparent 70%); border-left: 3px solid; padding-left: 14px;`
- 满色背景卡片（冲击力）：`background-color: <color>; color: #ffffff; padding: 16px 24px; border-radius: 16px;`
- 纯文字（极简/肃穆）：只靠字号、字重、letter-spacing 说话

**引用块设计：**
- 上下细线 + 淡背景 + 居中（书页摘引）：`border-top: 1px solid; border-bottom: 1px solid; background-color: rgba(...,0.03); text-align: center;`
- 左粗边框 + 斜体（经典引用）：`border-left: 3px solid; font-style: italic;`
- 渐变背景 + 圆角（卡片引用）：`background: linear-gradient(135deg, rgba(...,0.05), rgba(...,0.02)); border-radius: 0 8px 8px 0;`

**分割线设计：**
- 居中淡线（叹息）：`width: 40%; margin: 3rem auto; height: 1px; background-color: rgba(...,0.2);`
- 居中三短线（省略号式）：用 `background-image` 的 `linear-gradient` 多段实现
- 渐变淡出（优雅消失）：`background: linear-gradient(to right, transparent, rgba(...,0.3), transparent);`

**段落设计：**
- 首行缩进（文学感）：`text-indent: 2em;`
- 正常段落（通用）：无缩进，靠段间距分隔

**图片设计：**
- 微透明（旧照片感）：`opacity: 0.92;`
- 阴影边框（精致感）：`border: 1px solid rgba(...,0.1); box-shadow: 0 2px 8px rgba(...,0.06);`
- 圆角（柔和感）：`border-radius: 6px;`
- 纯净（不干预）：只设 `max-width: 100%; display: block; margin: auto;`

---

## 第三部分：输出格式

```json
{
  "meta": {
    "id": "kebab-case-id",
    "name": "中文名",
    "description": "一句话描述设计意图和适用场景",
    "tags": ["emotion", "style", "font-type"],
    "createdAt": "YYYY-MM-DD",
    "version": 1
  },
  "tokens": {
    "color": "#hex",
    "fontFamily": "default | optima | serif",
    "fontSize": 16,
    "headingSizes": { "h1": 24, "h2": 20, "h3": 18, "h4": 17, "h5": 16, "h6": 15 },
    "lineHeight": 1.75,
    "paragraphSpacing": 20,
    "containerPadding": 8
  },
  "styles": {
    "container": "...",
    "h1": "...", "h2": "...", "h3": "...", "h4": "...", "h5": "...", "h6": "...",
    "p": "...", "strong": "...", "em": "...", "strike": "...", "u": "...", "a": "...",
    "ul": "...", "ol": "...", "li": "...", "liText": "...",
    "taskList": "...", "taskListItem": "...", "taskListItemCheckbox": "...",
    "blockquote": "...", "code": "...", "pre": "...", "hr": "...", "img": "...",
    "tableWrapper": "...", "table": "...", "th": "...", "td": "...", "tr": "...",
    "codeBlockPre": "...", "codeBlockCode": "..."
  }
}
```

存储路径：`{skill_dir}/clients/{client}/themes/<id>.json`，同时更新 `clients/{client}/themes/_index.json` 索引。

---

## 附录：微信 CSS 安全边界

### 可用属性

```
color, background-color, background-image (仅 linear-gradient)
background-size, background-position, background-repeat
font-size, font-weight, font-style, font-family (白名单内)
margin, padding (及其四向展开)
border (及其四向展开), border-radius, border-collapse
text-align, text-decoration, text-decoration-color, text-indent
text-underline-offset, text-shadow, letter-spacing
line-height, word-break, word-wrap, white-space
display (block/inline/inline-block), overflow, overflow-x, overflow-y
max-width, max-height, width, height
opacity, box-shadow
list-style-type, list-style, vertical-align, accent-color, cursor
```

### 禁止

```
position: fixed/sticky, transform, animation, transition
filter, backdrop-filter, CSS Variables, Grid, Flexbox
@font-face, media queries, ::before/::after, float
radial-gradient, conic-gradient
```

### 关键 Gotchas

1. **每个 `<p>` 必须有显式 `color`** — 微信不继承父级颜色
2. **正文色禁止纯黑 `#000`** — 使用 `#2c2c2c` 或 `#3a3a3a`
3. **所有样式必须是 inline style** — 不能用 class
4. **`!important`** — margin、line-height、color 建议加，防止微信覆盖
5. **font-family 必须带完整 fallback** — 直接用白名单中的完整字符串
6. **表格不超过 4 列** — 移动端屏幕限制
7. **box-shadow 谨慎** — Android 旧微信客户端可能不渲染
8. **img max-height 600px** — 防止超长图片撑破布局
9. **代码等宽字体** — 固定用 `"SF Mono", Consolas, Monaco, monospace`
10. **三色规则** — 主题色 + 正文色 + 辅助色，不要更多
