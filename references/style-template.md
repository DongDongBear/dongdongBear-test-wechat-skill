# 客户配置模板

创建新客户时，复制 `clients/demo/style.yaml` 并修改以下字段：

```yaml
name: "客户名称"
industry: "行业领域"
target_audience: "目标受众画像"

topics:
  - 核心垂类1
  - 核心垂类2
  - 核心垂类3

tone: "语气描述（如：专业但不学术，有观点但不偏激）"
voice: "人称和角色（如：第一人称，像朋友在分享）"
word_count: "1500-2500"
content_style: "干货/故事/观点/混合"

blacklist:
  words: [禁用词1, 禁用词2]
  topics: [禁止话题1, 禁止话题2]

reference_accounts: [参考公众号1, 参考公众号2]

# YouMind 主题设置
theme: "simple"           # simple | center | decoration | prominent
theme_color: "#3498db"    # HEX 颜色

cover_style: "封面风格描述"
author: "作者名"
```

## 目录结构

```
clients/{client}/
├── style.yaml      # 必填：客户风格配置
├── history.yaml    # 自动生成：发布历史
├── playbook.md     # 可选：从语料分析生成的写作手册
├── corpus/         # 可选：历史推文（用于生成 playbook）
└── lessons/        # 自动生成：人工修改的学习记录
```
