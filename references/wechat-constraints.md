# 微信公众号技术限制

## 不支持的特性

### CSS
- 外部样式表（`<link>`, `<style>`）
- position: fixed / sticky
- CSS transform / animation / transition
- CSS filter / backdrop-filter
- @font-face 自定义字体
- CSS Grid（部分支持）
- Flexbox（部分支持）
- CSS Variables (var(--xxx))
- Media queries

### HTML
- `<script>` 标签
- 事件属性（onclick, onload 等）
- `<video>`, `<audio>` 标签
- `<iframe>`
- `<form>` 表单元素
- SVG（有限支持）

### 图片
- 本地路径（必须是 URL 或上传到微信）
- 单张超过 5MB
- WebP 格式（部分设备不支持）

## 解决方案（converter 已实现）

1. **所有样式必须内联**（style 属性）
2. 只使用微信支持的 CSS 属性
3. 代码块：`<pre><code>` + white-space: pre-wrap
4. 图片：必须上传到微信获取 URL
5. 表格：保持 ≤ 4 列，适配手机屏幕
6. 每个 `<p>` 必须有显式 color 属性（微信不继承）
7. 字体只能用系统字体栈

## 内容限制

- 草稿标题：≤ 64 字节
- 摘要：≤ 120 UTF-8 字节
- 正文 HTML：≤ 2MB
- 图片：单张 ≤ 5MB，正文最多 20 张
- 封面图：建议 900×383（2.35:1）
