---
title: "深度解读 | Anthropic 内部如何使用 Claude Code Skills：9 类模式、写作技巧与分发策略"
description: "Thariq（Anthropic Claude Code 团队）分享了 Anthropic 内部数百个 Skills 的实战经验：9 种 Skill 分类体系、7 条写作最佳实践、分发与市场管理策略。这是目前最权威的 Agent Skill 工程实践指南。"
---

## 速查卡

| 项目 | 内容 |
|------|------|
| **标题** | Lessons from Building Claude Code: How We Use Skills |
| **作者** | Thariq（@trq212），Anthropic Claude Code 团队成员 |
| **发布日期** | 2026-03-17 |
| **来源** | [X/Twitter 长文](https://x.com/trq212/status/2033949937936085378) |
| **热度** | 16K likes · 2.2K retweets · 43.7K bookmarks · 663 万 views |
| **关键词** | Claude Code, Skills, Agent 工程, 上下文工程, 渐进式披露, Hook, Plugin Marketplace |
| **核心论点** | Skills 不是"只是 markdown 文件"——它们是包含脚本、资产、数据的完整文件夹，是 Agent 编程的核心基础设施。Anthropic 内部有数百个在活跃使用。 |
| **文中引用链接** | [Skills 官方文档](https://code.claude.com/docs/en/skills) · [Skilljar Agent Skills 课程](https://anthropic.skilljar.com/introduction-to-agent-skills) · [Frontmatter 配置参考](https://code.claude.com/docs/en/skills#frontmatter-reference) · [frontend-design Skill 源码](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md) · [Skill Creator 博客](https://claude.com/blog/improving-skill-creator-test-measure-and-refine-agent-skills) · [Plugin Marketplace 文档](https://code.claude.com/docs/en/plugin-marketplaces) · [Skill 使用度量 Gist](https://gist.github.com/ThariqS/24defad423d701746e23dc19aace4de5) |

---

## 零、为什么必须认真读这篇文章

### 0.1 作者背景

Thariq（@trq212）不是一个普通的技术博主。他的 Twitter 简介写的是 "Claude Code @anthropicai. prev YC W20, MIT Media Lab."——他是 **Anthropic Claude Code 团队的核心成员**，直接参与了 Skills 系统的设计、开发和内部推广。

这意味着这篇文章不是外部观察者的猜测，而是**系统设计者基于内部数百个 Skill 的一手实践总结**。当他说"我们发现最好的 Skill 是这样的"，那个"我们"指的是 Anthropic 自己的工程团队——全世界最重度的 Claude Code 用户。

### 0.2 文章热度的含义

43,700 次收藏（bookmarks）——这个数字值得注意。X 上收藏一篇文章意味着"我要回来反复看"。对比之下，16K 的点赞是"我觉得不错"，而 43.7K 的收藏是"这是我的工作参考资料"。663 万的阅读量说明这篇文章触达了整个 AI 工程社区。

### 0.3 我们能从中学到什么

这篇文章回答了三个关键问题：
1. **Skill 到底是什么？**——不是 markdown 文件，是包含脚本和数据的文件夹
2. **应该做什么类型的 Skill？**——9 种分类覆盖企业 AI 编程的全部场景
3. **怎么把 Skill 做好？**——7 条来自数百个实践的写作建议 + 分发策略

---

## 一、开篇：Skills 的现状与挑战

原文开头三段设定了整篇文章的基调：

> "Skills have become one of the most used extension points in Claude Code. They're flexible, easy to make, and simple to distribute."

第一句话确立了一个事实：**Skills 已经成为 Claude Code 最常用的扩展机制**。不是 MCP 工具，不是自定义命令——是 Skills。这告诉我们，在 Anthropic 的技术栈中，Skills 的优先级比很多人想象的要高。

> "But this flexibility also makes it hard to know what works best. What type of skills are worth making? What's the secret to writing a good skill? When do you share them with others?"

第二句话提出了问题：灵活性是双刃剑。你可以做任何东西，但这恰恰让人不知道该做什么。这三个问题——做什么类型的、怎么写好、什么时候分享——对应了文章的三大部分。

> "We've been using skills in Claude Code extensively at Anthropic with hundreds of them in active use. These are the lessons we've learned about using skills to accelerate our development."

第三句话给出了数据：**Anthropic 内部有数百个 Skills 在活跃使用**。注意 "hundreds" 和 "active use" 两个词——不是写了数百个在那放着，而是数百个在日常工作中真的在被使用。这个规模说明 Skills 不是实验性功能，而是 Anthropic 工程团队的核心工作方式。

---

## 二、纠偏：Skill 到底是什么

### 2.1 "不只是 Markdown 文件"

> "A common misconception we hear about skills is that they are 'just markdown files', but the most interesting part of skills is that they're not just text files. They're folders that can include scripts, assets, data, etc. that the agent can discover, explore and manipulate."

这是全文最重要的一句话之一。Thariq 明确说"我们听到的一个常见误解"——这意味着大量 Claude Code 用户把 Skill 当成了一段增强版 system prompt。但实际上：

**Skill 是一个文件夹（folder）**，不是一个文件（file）。这个文件夹可以包含：
- **脚本（scripts）**：可执行的 Python/Shell/JS 文件，Claude 可以直接调用
- **资产（assets）**：模板文件、配置文件、示例文件
- **数据（data）**：JSON 文件、日志文件、甚至 SQLite 数据库
- 而且 Agent 可以**发现、探索和操作**这些内容

这个区分的深层含义是：一个好的 Skill 更像一个**微型应用程序**，而不是一份说明书。它给 Claude 的不只是知识（该怎么做），还包括工具（用什么做）和资源（参照什么做）。

### 2.2 配置选项和动态 Hook

> "In Claude Code, skills also have a wide variety of configuration options including registering dynamic hooks."

Thariq 在这里链接了 [Frontmatter 配置参考文档](https://code.claude.com/docs/en/skills#frontmatter-reference)。这个文档描述了 Skill 的 SKILL.md 文件头部可以配置的各种元数据，其中最强大的是 **Hook 注册**机制——允许 Skill 在特定的工具调用前后执行自定义逻辑。

> "We've found that some of the most interesting skills in Claude Code use these configuration options and folder structure creatively."

"最有趣的 Skill" = "配置选项 + 文件夹结构用得有创意的 Skill"。这句话直接告诉我们：如果你只在 SKILL.md 里写文字说明，你只利用了 Skill 能力的一小部分。

### 2.3 推荐资源

Thariq 推荐了两个入门资源：
- [Claude Code Skills 官方文档](https://code.claude.com/docs/en/skills)——技术参考
- [Skilljar 上的 Agent Skills 课程](https://anthropic.skilljar.com/introduction-to-agent-skills)——视频教程

他说"这篇文章假设你已经有一些 Skill 的基础"——这篇文章不是入门教程，而是进阶实践指南。

---

## 三、9 种 Skill 分类体系（完整逐条拆解）

### 3.0 分类的意义

> "After cataloging all of our skills, we noticed they cluster into a few recurring categories. The best skills fit cleanly into one; the more confusing ones straddle several. This isn't a definitive list, but it is a good way to think about if you're missing any inside of your org."

这段话有三个关键信息：

1. **他们对所有 Skill 做了编目（cataloging）**——这不是拍脑袋的分类，而是对数百个实际 Skill 做了系统性的梳理。这种"从实践中提炼模式"的方法论本身就值得学习。

2. **最好的 Skill 清晰地属于一个类别**——这暗示了 Skill 设计的第一原则：**单一职责**。如果你的 Skill 同时像 Library Reference 又像 Verification 又像 Automation，它大概率会让人困惑、难以维护。

3. **"这是一个好方法来检查你的组织里是否有遗漏"**——这 9 个类别可以当作一个 **检查清单（checklist）**。对照你的团队现有的 Skill，看看哪些类别还是空白——那可能就是最大的改善机会。

---

### 3.1 类型一：Library & API Reference（库和 API 参考）

> "Skills that explain how to correctly use a library, CLI, or SDKs. These could be both for internal libraries or common libraries that Claude Code sometimes has trouble with. These skills often included a folder of reference code snippets and a list of gotchas for Claude to avoid when writing a script."

**定义拆解：**
- **适用对象**：库（Library）、命令行工具（CLI）、SDK
- **两种场景**：内部库（Claude 完全没见过的）和公共库（Claude 见过但容易出错的）
- **典型内容**：参考代码片段文件夹 + gotchas 列表

"common libraries that Claude Code sometimes has trouble with"这个细节很重要——即使是公共库，Claude 也会犯错。可能是因为训练数据中的版本过旧、API 已更新、或者某些边界行为不直观。Library Reference Skill 的价值就是**纠正这些偏差**。

**三个示例的详细分析：**

**`billing-lib`** — "your internal billing library: edge cases, footguns, etc."
- 计费逻辑是典型的"看起来简单但到处是坑"的领域
- edge cases（边界情况）：比如退款、按比例计费、货币精度、时区问题
- footguns（容易自伤的陷阱）：比如误用浮点数做金额计算、忘了幂等性检查
- Claude 对这些坑一无所知，因为这是你公司的内部库

**`internal-platform-cli`** — "every subcommand of your internal CLI wrapper with examples on when to use them"
- 注意 "every subcommand" + "examples on **when** to use them"
- 不只是告诉 Claude 有哪些命令，还要告诉它**什么场景用什么命令**
- 这是一种决策知识，不是 API 文档能覆盖的

**`frontend-design`** — "make Claude better at your design system"
- 这个 Skill 在后文被反复提及，是全文的一个核心示例
- 目标是让 Claude 理解你的设计系统（组件、间距、色彩、布局规则）
- 这类 Skill 的挑战在于设计知识很难用代码表达——它是"品味"级别的知识

**底层洞察：** Library Reference Skill 解决的是**组织特有知识的注入**问题。每家公司都有大量只存在于工程师脑子里的 API 使用经验——"这个函数别在循环里调"、"那个参数的文档写错了，实际上是这样"——这些知识如果不 Skill 化，Claude 就只能靠猜。

---

### 3.2 类型二：Product Verification（产品验证）

> "Skills that describe how to test or verify that your code is working. These are often paired with an external tool like playwright, tmux, etc. for doing the verification."

**定义拆解：**
- **目的**：测试或验证代码是否正常工作
- **特点**：通常与外部工具配对使用
- **提到的工具**：Playwright（浏览器自动化）、tmux（终端多路复用器）

> "Verification skills are extremely useful for ensuring Claude's output is correct. **It can be worth having an engineer spend a week just making your verification skills excellent.**"

这是 Thariq 在全文中语气最强的一句话。在 9 种类型中，他唯独对 Verification Skill 说了"值得一个工程师花一整周来做"。这个权重暗示了一个关键判断：**在 Anthropic 的实践中，验证能力是限制 Agent 产出质量的最大瓶颈。**

为什么？因为 Claude 写代码的能力已经很强了（特别是有了 Skill 提供的上下文之后），但它的输出是不确定的——同样的 prompt 可能产生不同质量的代码。唯一能把"不确定"变成"可靠"的方法就是自动化验证。而好的验证 Skill 能让 Claude **自己验证自己的输出**，形成一个自我修正的闭环。

> "Consider techniques like having Claude record a video of its output so you can see exactly what it tested, or enforcing programmatic assertions on state at each step. These are often done by including a variety of scripts in the skill."

两个具体技巧：

1. **让 Claude 录制测试视频**：这不是比喻——是真的录屏。通过 Playwright 或其他工具录制测试过程的视频，你可以事后回看 Claude 到底测了什么。这解决了"Agent 说测了但你不知道它真的测了什么"的信任问题。

2. **在每一步强制编程断言**：不是在最后检查结果，而是在流程的每一步都写断言。比如注册流程的验证 Skill 里，不只是"注册成功了吗"，而是"表单渲染了吗？邮箱验证发出了吗？验证码对了吗？跳转到引导页了吗？"每一步都检查。

"These are often done by including a variety of scripts in the skill" 再次强调了 Skill 是文件夹而非文件——验证逻辑通常是一组脚本。

**三个示例的详细分析：**

**`signup-flow-driver`** — "runs through signup → email verify → onboarding in a headless browser, with hooks for asserting state at each step"
- 完整的注册流程端到端测试
- headless browser = Playwright
- "hooks for asserting state at each step" = 每一步都有检查点
- 这个 Skill 里大概率包含：启动浏览器的脚本、每个页面的断言函数、模拟邮箱的工具

**`checkout-verifier`** — "drives the checkout UI with Stripe test cards, verifies the invoice actually lands in the right state"
- 不只测 UI 交互，还**验证后端状态**（发票状态）
- Stripe test cards = 使用 Stripe 的测试信用卡号
- "actually lands in the right state" = 通过 API 检查数据库中的实际状态，不是只看 UI 显示

**`tmux-cli-driver`** — "for interactive CLI testing where the thing you're verifying needs a TTY"
- 有些命令行工具需要真正的终端（TTY）才能运行——比如交互式安装程序、TUI 应用
- tmux 可以创建一个虚拟终端让 Claude 操作
- 这说明 Anthropic 内部有需要测试 CLI 工具的场景（可能是 Claude Code 自身的测试？）

**底层洞察：** Verification Skill 是整个 Skill 生态的"质量门禁"。没有它，其他类型的 Skill 产出的代码质量无法保证。Thariq 愿意让工程师花一整周来做，说明这是最高 ROI 的投入——做好一个 Verification Skill，所有使用它的场景都受益。

---

### 3.3 类型三：Data Fetching & Analysis（数据获取与分析）

> "Skills that connect to your data and monitoring stacks. These skills might include libraries to fetch your data with credentials, specific dashboard ids, etc. as well as instructions on common workflows or ways to get data."

**定义拆解：**
- **连接对象**：数据栈（databases, data warehouses）和监控栈（Grafana, DataDog 等）
- **包含内容**：
  - 带凭证的数据获取库
  - 特定的 dashboard ID
  - 常见的数据获取工作流和方法

"with credentials"这个细节很关键——数据访问通常需要认证，Skill 可以把凭证管理也包含进来（可能通过 config.json 或环境变量引用），让 Claude 能直接查询数据而不需要用户每次手动输入密码。

**三个示例的详细分析：**

**`funnel-query`** — "which events do I join to see signup → activation → paid" plus "the table that actually has the canonical user_id"
- 这个例子极其真实。在任何有一定规模的公司里，"注册→激活→付费"的漏斗分析涉及多个事件表的 JOIN
- 最痛的点是 "the table that actually has the canonical user_id"——几乎每个数据团队都有这个问题：user_id 在三个不同的表里有三种不同的格式，到底该用哪个？
- 这种知识通常只有数据团队的老员工知道，Skill 把它编码化后，任何工程师通过 Claude 都能正确查询

**`cohort-compare`** — "compare two cohorts' retention or conversion, flag statistically significant deltas, link to the segment definitions"
- 群体对比分析：A 组用户 vs B 组用户的留存率/转化率
- "flag statistically significant deltas" = 不只是数字对比，还要做**统计显著性检验**
- "link to the segment definitions" = 每个用户群的定义在哪里、怎么生成的
- 这个 Skill 里可能包含统计分析的 Python 脚本

**`grafana`** — "datasource UIDs, cluster names, problem → dashboard lookup table"
- 这是一个运维导航 Skill
- "problem → dashboard lookup table" = "遇到什么问题，看哪个监控面板"的映射表
- datasource UIDs 和 cluster names 是 Grafana 特有的配置——手工记忆这些是不可能的

**底层洞察：** Data Fetching Skill 解决的是**组织暗知识的壁垒**问题。每个公司都有大量"你得问老张才知道这个数据怎么查"的隐性知识。新人入职可能要花几周才能摸清数据在哪里、怎么查。Skill 把这些知识变成了可执行的工具，消除了信息不对称。

---

### 3.4 类型四：Business Process & Team Automation（业务流程与团队自动化）

> "Skills that automate repetitive workflows into one command. These skills are usually fairly simple instructions but might have more complicated dependencies on other skills or MCPs. For these skills, saving previous results in log files can help the model stay consistent and reflect on previous executions of the workflow."

**定义拆解：**
- **目标**：把重复性工作流自动化为一条命令
- **特点**：指令本身往往简单，但依赖复杂（可能依赖其他 Skill 或 MCP 工具）
- **关键技巧**：**把历次执行结果保存到日志文件中**

最后一点值得特别展开。"saving previous results in log files can help the model stay consistent and reflect on previous executions"——这意味着 Skill 可以有**累积状态**。每次执行的输出被保存，下次执行时模型读取历史，从而：
1. **保持一致性**：今天的站会报告和昨天的格式、用词保持一致
2. **反思历史**：模型知道上次做了什么，能计算增量变化

**三个示例的详细分析：**

**`standup-post`** — "aggregates your ticket tracker, GitHub activity, and prior Slack → formatted standup, delta-only"
- 输入来源：ticket tracker（Jira/Linear）+ GitHub（commits/PRs）+ 之前的 Slack 消息
- 输出格式：格式化的站会报告
- "delta-only" = 只展示**增量**，不重复说昨天已经报过的内容
- 实现增量的关键就是上面提到的日志——读取上次的站会报告，对比今天的数据，只写差异

**`create-<ticket-system>-ticket`** — "enforces schema (valid enum values, required fields) plus post-creation workflow (ping reviewer, link in Slack)"
- `<ticket-system>` 是模板化写法——每个团队的 ticket 系统不同（Jira、Linear、GitHub Issues）
- "enforces schema" = 强制符合格式要求（优先级只能是 P0-P4、类型只能是 bug/feature 等）
- "post-creation workflow" = 创建完 ticket 后的自动化动作：通知 reviewer、在 Slack 里发链接
- 这是一个很好的"简单指令 + 复杂依赖"的例子——创建 ticket 的逻辑很简单，但后续的通知链条涉及多个工具

**`weekly-recap`** — "merged PRs + closed tickets + deploys → formatted recap post"
- 自动汇总一周的工作成果：合并的 PR、关闭的 ticket、部署记录
- 生成一篇格式化的周报
- 这个 Skill 可能依赖 Data Fetching 类的 Skill 来获取数据

**底层洞察：** Business Process Skill 的核心价值是**消灭重复性脑力劳动**。站会报告、周报、ticket 创建——这些都是每个工程师每天/每周都在做的事，但每次都需要手动聚合信息、格式化输出。自动化后每人每天节省 10-30 分钟，一个百人团队一年就是上千小时。

---

### 3.5 类型五：Code Scaffolding & Templates（代码脚手架与模板）

> "Skills that generate framework boilerplate for a specific function in codebase. You might combine these skills with scripts that can be composed. They are especially useful when your scaffolding has natural language requirements that can't be purely covered by code."

**定义拆解：**
- **目标**：为代码库中特定功能生成框架样板代码
- **方法**：可以将 Skill 与可组合的脚本结合
- **独特价值**：特别适用于**脚手架中有自然语言需求、无法纯粹用代码覆盖的场景**

最后一句话是关键。传统的脚手架工具（yeoman, cookiecutter, plop）只能处理结构化的模板替换——它们能生成文件结构、替换变量名，但不能理解"这个服务是面向客户的，需要额外的安全审计"。而 Skill 驱动的 Claude 可以理解自然语言需求，在生成代码时做出**语义级别的决策**。

比如同样是 `new-api-endpoint` 脚手架：
- 传统工具：生成固定模板，填入 endpoint name
- Skill + Claude：理解"这是一个支付相关 endpoint"后，自动加入请求签名验证、幂等性检查、审计日志——这些决策不是模板能表达的

**三个示例的详细分析：**

**`new-<framework>-workflow`** — "scaffolds a new service/workflow/handler with your annotations"
- `<framework>` 是占位符——每个公司的技术栈不同
- "with your annotations" = 使用你公司特定的注解/装饰器
- 比如你的微服务框架要求每个 handler 都有 `@RateLimit`、`@Auth` 注解，Skill 确保 Claude 不会忘

**`new-migration`** — "your migration file template plus common gotchas"
- 数据库迁移是一个特别容易出错的领域
- "common gotchas" 可能包括：别在大表上加 NOT NULL 列（会锁表）、先 backfill 再加约束、注意外键顺序
- 这些 gotchas 通常是团队踩过坑后的血泪教训

**`create-app`** — "new internal app with your auth, logging, and deploy config pre-wired"
- "pre-wired" = 预先接好
- 新建一个内部应用时，认证（auth）、日志（logging）、部署配置（deploy config）这三件事每次都要做，但每次都可能做错
- 一个好的 Skill 可以确保每个新应用从诞生那天起就有正确的基础设施配置

**底层洞察：** Code Scaffolding Skill 比传统脚手架强在**决策能力**。它不只是复制模板，还能根据上下文做出合理的技术决策。这是 Agent 编程相比传统工具的本质优势。

---

### 3.6 类型六：Code Quality & Review（代码质量与审查）

> "Skills that enforce code quality inside of your org and help review code. These can include deterministic scripts or tools for maximum robustness. You may want to run these skills automatically as part of hooks or inside of a GitHub Action."

**定义拆解：**
- **目标**：在组织内部执行代码质量标准、辅助代码审查
- **实现**：可以包含确定性脚本或工具（不完全依赖 LLM 判断）
- **运行方式**：可以作为 Hook 自动运行，或放到 GitHub Action 中

"deterministic scripts or tools for maximum robustness" 这个细节很重要——代码质量检查不能完全靠 LLM 的判断，因为 LLM 的输出是概率性的。好的 Quality Skill 会**混合使用确定性工具**（linter、type checker、custom rules）**和 LLM 分析**（代码意图理解、架构合理性判断）。

**三个示例的详细分析：**

**`adversarial-review`** — "spawns a fresh-eyes subagent to critique, implements fixes, iterates until findings degrade to nitpicks"

这个例子极其精彩，需要充分展开：

1. **"spawns a fresh-eyes subagent"**：启动一个全新的 Claude 实例（sub-agent）来做代码审查。"fresh-eyes"是关键——这个审查者没有参与代码编写，所以不会有"自己写的代码看着都顺眼"的偏见。
2. **"to critique"**：这个 sub-agent 的唯一任务就是找问题。它被指示要严格审查，不要客气。
3. **"implements fixes"**：找到问题后，原来的 Agent（或者第三个 Agent）实施修复。
4. **"iterates"**：修复完再审查，审查完再修复——这是一个多轮对抗循环。
5. **"until findings degrade to nitpicks"**：循环的终止条件是审查发现的问题退化为"吹毛求疵"级别——只剩下风格偏好这种无关紧要的小问题。

这描述的是一个**多 Agent 自我对抗**的工程模式。而且 Anthropic 内部真的在用它。这验证了一个长期以来的假设：Agent 审查 Agent 是可行的，而且能显著提高代码质量。

**`code-style`** — "enforces code style, especially styles that Claude does not do well by default"
- "especially styles that Claude does not do well by default" = 针对 Claude **默认做不好的**风格
- 这是一个务实的切入点——不是重新教 Claude 整个 PEP 8，而是只纠正它特别容易犯的错误
- 比如 Claude 可能默认喜欢超长的函数名、过度使用类型注解、或者在某些场景下不必要地写 try-catch

**`testing-practices`** — "instructions on how to write tests and what to test"
- "how to write tests" = 你的团队偏好什么测试框架、什么断言风格、mock 到什么程度
- "what to test" = 更重要的问题——哪些路径必须测、哪些可以跳过、集成测试的边界在哪里

**底层洞察：** adversarial-review 模式的核心启示是：**Agent 的输出质量不应该依赖单次生成的正确性，而应该依赖一个自我修正的循环。** 这跟人类的 code review 流程是同构的——只是把人换成了 Agent，速度快了 100 倍。

---

### 3.7 类型七：CI/CD & Deployment（持续集成与部署）

> "Skills that help you fetch, push, and deploy code inside of your codebase. These skills may reference other skills to collect data."

**定义拆解：**
- **范围**：获取代码、推送代码、部署代码
- **特点**：可能引用其他 Skill（比如用 Data Fetching Skill 获取部署状态）

**三个示例的详细分析：**

**`babysit-pr`** — "monitors a PR → retries flaky CI → resolves merge conflicts → enables auto-merge"

"babysit"（看孩子）这个名字本身就说明了一切。PR 从创建到合并的过程中有大量"等待+手动干预"的环节：
1. CI 跑了 20 分钟然后某个 flaky test 红了 → 手动重跑
2. 重跑通过了但有合并冲突 → 手动 rebase
3. rebase 后 CI 又要跑一遍 → 又等 20 分钟
4. 终于绿了 → 手动点 merge

这个 Skill 把整个流程自动化了。Claude 会持续监控 PR 状态，遇到 flaky test 自动重跑，遇到冲突自动解决，一切就绪后启用 auto-merge。一个工程师可能同时有 3-5 个 PR 在走流程，babysit-pr 可以同时看管所有 PR。

**`deploy-<service>`** — "build → smoke test → gradual traffic rollout with error-rate comparison → auto-rollback on regression"

这是一个完整的 **canary deployment（金丝雀部署）** 自动化：
1. **build** — 构建新版本
2. **smoke test** — 基本功能冒烟测试
3. **gradual traffic rollout** — 逐步增加新版本的流量（比如 1% → 5% → 25% → 100%）
4. **error-rate comparison** — 实时对比新旧版本的错误率
5. **auto-rollback on regression** — 如果新版本错误率升高，自动回滚

这已经不是"辅助编码"——这是**辅助运维**。Claude 通过这个 Skill 可以独立完成一次生产部署，并在出问题时自动止损。

**`cherry-pick-prod`** — "isolated worktree → cherry-pick → conflict resolution → PR with template"
- 生产环境的紧急修复流程：
  1. 创建隔离的 git worktree（不影响当前工作）
  2. cherry-pick 修复 commit
  3. 解决可能的冲突
  4. 创建带标准模板的 PR
- 紧急修复时人容易慌张出错，自动化这个流程减少了人为失误

**底层洞察：** CI/CD Skill 展示了 Agent 能力的上限不再是"写代码"，而是"管理整个软件交付流程"。从 PR 管理到生产部署到紧急修复，Agent 正在接管 DevOps 的日常操作。

---

### 3.8 类型八：Runbooks（运维手册）

> "Skills that take a symptom (such as a Slack thread, alert, or error signature), walk through a multi-tool investigation, and produce a structured report."

**定义拆解：**
- **输入**：一个症状——可以是 Slack 里的报障消息、监控告警、或一个错误签名
- **过程**：多工具调查——跨多个系统收集信息
- **输出**：结构化报告

Runbook 的本质是把**专家的排查思路**编码化。当一个 P0 告警响起时，资深 SRE 脑子里会自动跑一个决策树："先看这个 dashboard → 如果指标正常就查那个日志 → 如果日志里有这个错误就去看那个配置"。这个决策树以前只存在于人脑中，Runbook Skill 把它变成了可复制、可传承的组织资产。

**三个示例的详细分析：**

**`<service>-debugging`** — "maps symptoms → tools → query patterns for your highest-traffic services"
- 每个高流量服务一个调试 Skill
- "symptoms → tools → query patterns" = 三层映射：
  - 症状（"延迟升高"）→ 该用什么工具查（Grafana / Jaeger / kubectl）
  - 工具 → 具体的查询模式（哪个 dashboard、什么 PromQL 查询、哪个 namespace）
- 针对最高流量服务——因为这些服务出问题影响最大、排查也最复杂

**`oncall-runner`** — "fetches the alert → checks the usual suspects → formats a finding"
- 值班工程师的自动化助手
- "fetches the alert" = 自动拉取告警详情（从 PagerDuty/OpsGenie 等）
- "checks the usual suspects" = 检查常见嫌疑（CPU/内存/磁盘/网络/最近的部署）
- "formats a finding" = 整理成结构化报告
- 如果常见嫌疑能解释问题，值班工程师看报告就够了，不需要亲自排查

**`log-correlator`** — "given a request ID, pulls matching logs from every system that might have touched it"
- 分布式系统中一个请求可能经过 10+ 个服务
- 给一个请求 ID，自动从所有可能经过的系统中拉取相关日志
- 这个操作手工做可能要 30 分钟（登录不同系统、拼查询），Skill 几秒钟完成

**底层洞察：** Runbook Skill 的价值公式是：`(资深工程师的排查时间) × (事故频率) × (团队中没有这个经验的人数)`。对于一个经常出问题的服务，一个好的 Runbook Skill 可能比招一个 SRE 更划算。

---

### 3.9 类型九：Infrastructure Operations（基础设施运维）

> "Skills that perform routine maintenance and operational procedures — some of which involve destructive actions that benefit from guardrails. These make it easier for engineers to follow best practices in critical operations."

**定义拆解：**
- **目标**：日常维护和运维操作
- **特殊之处**：部分操作是**破坏性的**（删除资源、清理数据），需要**护栏（guardrails）**
- **价值**：让工程师更容易遵循关键操作的最佳实践

"destructive actions that benefit from guardrails"——这句话承认了一个现实：有些运维操作本质上是危险的，完全自动化不合适，但完全手动也容易出错。正确的方式是**自动化所有安全的步骤，在危险点设置人工检查点**。

**三个示例的详细分析：**

**`<resource>-orphans`** — "finds orphaned pods/volumes → posts to Slack → soak period → user confirms → cascading cleanup"

这个流程设计值得逐步分析：
1. **finds orphaned pods/volumes** — 自动扫描，找到没有被任何服务引用的 pod 或存储卷
2. **posts to Slack** — 不是直接删除！而是先发通知到 Slack 频道
3. **soak period** — 等一段时间（比如 48 小时），给人时间检查这些资源是否真的不需要
4. **user confirms** — 人类确认"是的，可以删了"
5. **cascading cleanup** — 确认后才执行删除，并处理级联依赖

这是一个教科书式的 **human-in-the-loop（人在环中）** 设计。Agent 做所有枯燥的扫描和准备工作，人类只需要在关键决策点做一次确认。既保证了效率，又保证了安全。

**`dependency-management`** — "your org's dependency approval workflow"
- 依赖升级在大公司里通常需要审批流程
- 这个 Skill 可能包含：自动检测过期依赖 → 评估升级风险 → 生成审批请求 → 跟踪审批状态

**`cost-investigation`** — "why did our storage/egress bill spike" with the specific buckets and query patterns
- 云账单突增是每个团队都会遇到的问题
- "specific buckets and query patterns" = 不是给你一个通用的成本分析教程，而是告诉你：
  - 去哪个 AWS 页面看
  - 查哪个 S3 bucket 的用量
  - 用什么 query 分析 CloudWatch 日志
  - 常见的成本陷阱有哪些（比如 lifecycle rule 没生效、某个 lambda 在疯狂写日志）

**底层洞察：** Infrastructure Skill 是 9 种类型中最需要"护栏设计"的一种。好的 Infra Skill 不是让 Agent 拥有不受限的权限，而是精心设计一个**权限梯度**：安全操作自动执行，危险操作需要人工批准。

---

## 四、Skill 写作最佳实践（逐条深入拆解）

Thariq 在文章的第二大部分提供了 7 条写作建议。他开头说：

> "Once you've decided on the skill to make, how do you write it? These are some of the best practices, tips, and tricks we've found."
> "We also recently released Skill Creator to make it easier to create skills in Claude Code."

[Skill Creator](https://claude.com/blog/improving-skill-creator-test-measure-and-refine-agent-skills) 是 Anthropic 推出的一个帮助创建 Skill 的工具——但工具再好也替代不了设计理念，所以这些最佳实践仍然需要人来理解和应用。

---

### 4.1 Don't State the Obvious（别写 Claude 已经知道的）

> "Claude Code knows a lot about your codebase, and Claude knows a lot about coding, including many default opinions. If you're publishing a skill that is primarily about knowledge, try to focus on information that pushes Claude out of its normal way of thinking."

这句话有两层含义：

1. **Claude Code 了解你的代码库**——通过阅读项目文件、README、代码结构，Claude 已经知道你用什么语言、什么框架、什么目录结构。你不需要在 Skill 里重复这些。

2. **Claude 对编程有默认观点**——它有自己的偏好（命名风格、设计模式、错误处理方式）。如果你的偏好跟 Claude 的默认一致，不需要写进 Skill。只需要写**你跟 Claude 不一样的地方**。

"pushes Claude out of its normal way of thinking"——好的 Skill 应该让 Claude **改变默认行为**，而不是加固它已有的行为。

> "The frontend design skill is a great example — it was built by one of the engineers at Anthropic by iterating with customers on improving Claude's design taste, avoiding classic patterns like the Inter font and purple gradients."

这个例子非常具体。[frontend-design Skill](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md) 的诞生过程：
1. Anthropic 的一位工程师**与客户反复迭代**——不是闭门造车，而是基于真实反馈
2. 核心目标是**改善 Claude 的设计品味**——这是一个抽象的、难以量化的目标
3. 具体手段是**避免经典 AI 生成风格**——Inter 字体 + 紫色渐变是 Claude（和其他 LLM）生成前端代码时的标志性风格，用户一眼就能看出"这是 AI 做的"
4. Skill 的存在让 Claude 跳出了这个默认模式

**实践建议：** 在写 Skill 之前，先让 Claude 不用 Skill 做一遍任务，记录它犯了哪些错误或做了哪些不理想的选择。这些错误和次优选择才是 Skill 应该重点纠正的内容。

---

### 4.2 Build a Gotchas Section（维护一个"陷阱"清单）

> "The highest-signal content in any skill is the Gotchas section. These sections should be built up from common failure points that Claude runs into when using your skill. Ideally, you will update your skill over time to capture these gotchas."

三个关键判断：

1. **"highest-signal content"** = Gotchas 是整个 Skill 中信息密度最高的部分。不是概述，不是步骤说明，而是"坑列表"。

2. **"built up from common failure points"** = Gotchas 不是你预想的，而是从 Claude **实际犯过的错误**中收集的。这意味着 Gotchas 需要在使用中持续积累。

3. **"update your skill over time"** = Skill 是一个**活文档**，不是写完就定稿的。每次 Claude 在使用这个 Skill 时犯了新错误，就应该把那个错误模式加进 Gotchas。

**与我们实践的对照：** 这跟我们在 MEMORY.md 中维护"经验教训"的思路完全一致——从错误中提取教训，写下来防止重犯。区别只是 MEMORY.md 是给整个 Agent 看的通用记忆，而 Gotchas 是 Skill 特有的领域记忆。

**实践建议：** 每个 Skill 的 Gotchas section 应该是一个编号列表，格式统一，方便随时追加。每条 gotcha 应该包含：什么场景下发生、表现是什么、正确做法是什么。

---

### 4.3 Use the File System & Progressive Disclosure（善用文件系统和渐进式披露）

> "Like we said earlier, a skill is a folder, not just a markdown file. You should think of the entire file system as a form of context engineering and progressive disclosure. Tell Claude what files are in your skill, and it will read them at appropriate times."

这可能是全文中对 Skill 设计理念最精辟的一句话：**"你应该把整个文件系统看作一种上下文工程和渐进式披露的形式。"**

**什么是渐进式披露（Progressive Disclosure）？** 这是一个用户界面设计概念——不要一次性把所有信息呈现给用户，而是按需逐步展示。用在 Skill 设计上就是：**不要把所有内容都塞进 SKILL.md，而是分散到多个文件中，让 Claude 按需阅读。**

为什么这很重要？因为 context window 是有限的。如果一个 Skill 把 20 页的 API 文档都写在 SKILL.md 里，每次触发都会占用大量 context。但如果 SKILL.md 只写概述和目录，详细文档放在 references/ 文件夹里，Claude 只在真正需要某个 API 的签名时才去读——context 的利用效率大幅提高。

> "The simplest form of progressive disclosure is to point to other markdown files for Claude to use. For example, you may split detailed function signatures and usage examples into references/api.md."

**最简形式**：在 SKILL.md 中写"详细的函数签名和用法示例请参阅 references/api.md"。Claude 在需要时会自己去读。

> "Another example: if your end output is a markdown file, you might include a template file for it in assets/ to copy and use."

**模板文件**：如果 Skill 的输出是一个 markdown 文件（比如技术方案文档），在 assets/ 里放一个模板。Claude 会复制这个模板然后填充内容——比从头生成更准确、格式更一致。

> "You can have folders of references, scripts, examples, etc., which help Claude work more effectively."

**推荐的文件夹结构：**
- `references/` — 参考文档、API 签名、规范
- `scripts/` — 可执行的脚本（Python/Shell/JS）
- `examples/` — 示例代码、示例输出
- `assets/` — 模板、配置、静态资源

**实践建议：** 在 SKILL.md 的开头写一段"文件目录说明"，列出 Skill 文件夹中有哪些文件/文件夹以及每个的用途。Claude 看到这个目录就知道需要什么信息时去哪里找。

---

### 4.4 Avoid Railroading Claude（避免过度约束 Claude）

> "Claude will generally try to stick to your instructions, and because Skills are so reusable you'll want to be careful of being too specific in your instructions. Give Claude the information it needs, but give it the flexibility to adapt to the situation."

这条建议的核心是一个**设计张力**：

- **太松散**：Skill 没有提供足够的指导，Claude 不知道该怎么做
- **太死板**：Skill 写了过于具体的步骤，Claude 在非典型场景下被迫遵循不合适的步骤

正确的平衡点是：**描述目标和约束，而不是步骤。**

比如一个部署 Skill：
- ❌ "第一步：运行 npm build。第二步：运行 npm test。第三步：运行 deploy.sh。" → 如果项目用的是 yarn 怎么办？如果没有 deploy.sh 怎么办？
- ✅ "确保代码通过所有测试后再部署。使用项目中已有的构建和部署工具。部署前检查是否有未提交的更改。" → Claude 可以自适应不同的项目配置

"because Skills are so reusable" 是原因——同一个 Skill 会在无数不同的上下文中被触发。过于死板的步骤指令在场景 A 完美运行，在场景 B 可能就是灾难。

---

### 4.5 Think through the Setup（想清楚初始化流程）

> "Some skills may need to be set up with context from the user. For example, if you are making a skill that posts your standup to Slack, you may want Claude to ask which Slack channel to post it in."

有些 Skill 需要用户提供配置信息才能工作——Slack channel、API key、目标环境、个人偏好等。

> "A good pattern to do this is to store this setup information in a config.json file in the skill directory like the above example. If the config is not set up, the agent can then ask the user for information."

**推荐模式：**
1. Skill 目录中放一个 `config.json`
2. Skill 被触发时，先检查 config.json 是否存在
3. 如果不存在或缺少必要字段 → 询问用户
4. 用户回答后 → 写入 config.json
5. 下次触发时直接读取，不再询问

这实现了一种**自举（bootstrapping）** 体验——第一次用需要一点配置，之后零摩擦。

> "If you want the agent to present structured, multiple choice questions you can instruct Claude to use the AskUserQuestion tool."

如果需要结构化的多选问题（而不是开放式文本输入），可以用 `AskUserQuestion` 工具。这对于有限选项的配置特别有用——比如"你想发布到哪个环境？production / staging / development"。

---

### 4.6 The Description Field Is For the Model（描述字段是写给模型看的）

> "When Claude Code starts a session, it builds a listing of every available skill with its description. This listing is what Claude scans to decide 'is there a skill for this request?' Which means the description field is not a summary — it's a description of when to trigger this skill."

这段话揭示了一个很多人忽略的机制细节：

**Skill 触发流程：**
1. Claude Code 启动 session 时，读取所有已安装的 Skill
2. 构建一个 listing，其中每个 Skill 只展示**名称 + description**
3. 当用户发出请求时，Claude 扫描这个 listing
4. 基于 description 判断"这个请求是否匹配某个 Skill"
5. 如果匹配，加载那个 Skill 的完整内容

**关键洞察：** description 不是"这个 Skill 做什么"的摘要——它是**"什么情况下应该触发这个 Skill"的触发条件描述**。

这两者的区别：
- 摘要式描述："A skill for deploying services to production."
- 触发条件式描述："Use when deploying, releasing, shipping to prod, doing a rollout, or pushing changes to production. Also covers rollbacks and hotfixes."

后者包含了更多同义词和场景变体，大大增加了被正确触发的概率。

**实践建议：** 把 description 写成一个"什么时候用我"的说明，包含关键动词、场景描述、和常见表述变体。就像 SEO 的元描述一样——你要让搜索引擎（在这里是 Claude）能准确匹配。

---

### 4.7 Memory & Storing Data（记忆与数据存储）

> "Some skills can include a form of memory by storing data within them. You could store data in anything as simple as an append only text log file or JSON files, or as complicated as a SQLite database."

**存储方式的梯度：**
- **最简单**：追加写入的文本日志（如 standup.log）
- **中等**：JSON 文件（结构化但灵活）
- **最复杂**：SQLite 数据库（支持查询、索引、事务）

选择哪种取决于数据量和查询复杂度。大多数场景下 JSON 就够了。

> "For example, a standup-post skill might keep a standups.log with every post it's written, which means the next time you run it, Claude reads its own history and can tell what's changed since yesterday."

这个例子完整地描述了**有状态 Skill 的工作方式**：
1. 第一次运行：生成今天的站会报告，同时写入 standups.log
2. 第二次运行：读取 standups.log，看到上次的报告，对比今天的数据，**只报告增量变化**
3. 第 N 次运行：读取所有历史，可以生成趋势分析（"本周合并了 23 个 PR，比上周多 40%"）

这是一种轻量级的 **Agent 记忆**实现——不需要向量数据库，不需要知识图谱，一个日志文件就能让 Skill 具备跨 session 的连续性。

> "Data stored in the skill directory may be deleted when you upgrade the skill, so you should store this in a stable folder, as of today we provide `${CLAUDE_PLUGIN_DATA}` as a stable folder per plugin to store data in."

**重要警告：** Skill 目录中的数据在**升级 Skill 时可能被删除**（因为升级通常是删除旧版本、安装新版本）。持久化数据应该存在 `${CLAUDE_PLUGIN_DATA}` 这个稳定路径中——每个 plugin 有独立的数据目录，不受升级影响。

---

### 4.8 Store Scripts & Generate Code（存储脚本，让 Claude 组合调用）

> "One of the most powerful tools you can give Claude is code. Giving Claude scripts and libraries lets Claude spend its turns on composition, deciding what to do next rather than reconstructing boilerplate."

这句话描述了一个关键的**效率优化模式**：

**没有脚本时的 Claude：**
1. 理解用户需求
2. 从头写数据连接代码
3. 从头写查询逻辑
4. 从头写结果格式化代码
5. 组合运行

**有脚本时的 Claude：**
1. 理解用户需求
2. 调用现有的 `fetch_events()` 函数
3. 调用现有的 `query_cohort()` 函数
4. 组合结果

步骤从 5 步减少到 4 步看起来变化不大，但每一步的**工作量**差异巨大。从头写代码需要大量 token（思考+生成），调用现有函数只需要几个 token。这意味着 Claude 可以把算力花在**决策和组合**上，而不是**重复劳动**上。

> "For example, in your data science skill you might have a library of functions to fetch data from your event source. In order for Claude to do complex analysis, you could give it a set of helper functions."

Thariq 描述了一个具体场景：数据分析 Skill 中包含一组数据获取的 helper 函数。Claude 不需要知道怎么连接 BigQuery、怎么写 SQL、怎么处理分页——这些都被封装在 helper 里了。它只需要知道"调用 `get_events(start, end, event_type)` 就能拿到数据"。

> "Claude can then generate scripts on the fly to compose this functionality to do more advanced analysis for prompts like 'What happened on Tuesday?'"

Claude 可以**临时生成脚本**来组合这些 helper 函数。对于"周二发生了什么？"这样的开放性问题，Claude 可能会：
1. 调用 `get_events('2026-03-24', '2026-03-25', None)` 获取所有事件
2. 调用 `group_by_type(events)` 按类型分组
3. 生成一个临时脚本做异常检测
4. 输出一份结构化报告

**底层洞察：** 这个模式让 Agent 的工作方式更接近**人类程序员**——人类程序员也不会每次都从头写所有代码，而是组合已有的库和工具。给 Agent 提供"积木"（脚本），让它专注于"搭建"（组合）。

---

### 4.9 On Demand Hooks（按需 Hook）

> "Skills can include hooks that are only activated when the skill is called, and last for the duration of the session. Use this for more opinionated hooks that you don't want to run all the time, but are extremely useful sometimes."

**机制说明：**
- Hook 只在 Skill 被调用时激活（不是全局生效）
- 持续到 session 结束
- 适用于"有时候很有用，但不想一直开着"的场景

> "/careful — blocks rm -rf, DROP TABLE, force-push, kubectl delete via PreToolUse matcher on Bash. You only want this when you know you're touching prod — having it always on would drive you insane."

**`/careful` 详细分析：**
- 通过 PreToolUse Hook 拦截 Bash 工具调用
- 用 matcher 匹配危险命令模式：`rm -rf`、`DROP TABLE`、`force-push`、`kubectl delete`
- 只在操作生产环境时手动启用
- "having it always on would drive you insane" = 日常开发中这些命令是合法的（你当然可以 `rm -rf` 一个临时目录），全程拦截会严重影响效率
- 所以它是**按需启用的安全护栏**：`/careful` 开启后 Claude 无法执行任何危险命令，直到 session 结束

> "/freeze — blocks any Edit/Write that's not in a specific directory. Useful when debugging: 'I want to add logs but I keep accidentally fixing unrelated code'"

**`/freeze` 详细分析：**
- 拦截所有不在指定目录内的 Edit/Write 操作
- 使用场景：**调试时防止 Claude "顺手修"不相关的代码**
- 这是一个极其常见的 Agent 编程痛点——你让 Claude 在 A 文件加调试日志，它看到 B 文件有个小 bug 就顺手改了，结果引入了新问题
- `/freeze` 把可写范围限制在一个目录（比如只允许修改 src/debug/），Claude 看到其他地方的问题只能记录不能修改

**底层洞察：** On Demand Hook 是一种**动态权限管理**机制。不同的任务需要不同的安全等级——日常开发宽松、生产操作严格、调试时限定范围。与其设计一个"一刀切"的权限策略，不如让用户根据当前任务按需启用合适的护栏。

---

## 五、分发策略与市场管理

### 5.1 两种分发方式

> "There are two ways you might share skills with others:
> - check your skills into your repo (under ./.claude/skills)
> - make a plugin and have a Claude Code Plugin marketplace where users can upload and install plugins"

**方式一：代码仓库内（.claude/skills/）**
- 把 Skill 直接提交到项目的 `.claude/skills/` 目录
- 适合**小团队、少量仓库**的场景
- 优点：简单、版本可控、与代码一起 review
- 缺点：每个 Skill 都会增加 context 开销（因为 Claude 启动时要读取所有 Skill 的 description）

> "For smaller teams working across relatively few repos, checking your skills into repos works well. But every skill that is checked in also adds a little bit to the context of the model. As you scale, an internal plugin marketplace allows you to distribute skills and let your team decide which ones to install."

**方式二：Plugin 市场**
- 通过 [Plugin Marketplace](https://code.claude.com/docs/en/plugin-marketplaces) 分发
- 用户自行选择安装哪些 Skill
- 适合**大团队、多仓库**的场景
- 解决了 context 膨胀问题——你不需要所有 Skill，只安装你需要的

### 5.2 市场管理策略

> "How do you decide which skills go in a marketplace? How do people submit them?"

> "We don't have a centralized team that decides; instead we try and find the most useful skills organically."

**Anthropic 的做法：没有中央审批团队，而是让好的 Skill 自然涌现。** 具体流程：

1. **沙盒阶段**：有人做了一个 Skill → 上传到 GitHub 的 sandbox 文件夹 → 在 Slack 或其他论坛中推广
2. **评估阶段**：同事试用、反馈、迭代
3. **准入阶段**：Skill 获得足够 traction 后（由 owner 自行判断），提交 PR 进入正式市场

> "A note of warning, it can be quite easy to create bad or redundant skills, so making sure you have some method of curation before release is important."

**质量控制警告：** Thariq 明确指出"很容易创建糟糕或冗余的 Skill"。他建议在正式发布前**确保有某种策展（curation）机制**。

这可能包括：
- 代码审查（Skill 也应该像代码一样被 review）
- 检查是否与现有 Skill 功能重复
- 验证 Skill 在不同场景下是否正常工作
- 确认 Gotchas section 是否完善

### 5.3 Skill 组合与依赖

> "You may want to have skills that depend on each other. For example, you may have a file upload skill that uploads a file, and a CSV generation skill that makes a CSV and uploads it. This sort of dependency management is not natively built into marketplaces or skills yet, but you can just reference other skills by name, and the model will invoke them if they are installed."

当前的 Skill 系统**没有原生的依赖管理**（不像 npm 的 package.json 可以声明依赖）。但可以通过**按名引用**实现隐式依赖：

- Skill A 的 SKILL.md 里写："如果需要上传文件，使用 file-upload skill"
- Claude 看到这个指示后，如果 file-upload skill 已安装，就会自动调用它
- 如果没安装，Claude 可能会告诉用户"需要先安装 file-upload skill"

这是一个务实但脆弱的方案——如果 Skill 名字改了或者用户忘装，就会出问题。Thariq 的语气（"not natively built yet"）暗示这个功能可能在未来版本中得到原生支持。

### 5.4 度量 Skill 效果

> "To understand how a skill is doing, we use a PreToolUse hook that lets us log skill usage within the company (example code here). This means we can find skills that are popular or are undertriggering compared to our expectations."

Anthropic 使用 PreToolUse Hook 做 **Skill 使用追踪**：
- 每次 Skill 被触发，记录一条日志
- 聚合分析后可以发现：
  - **哪些 Skill 最受欢迎** → 值得继续投入
  - **哪些 Skill 触发率低于预期** → 可能是 description 写得不好（没有被正确匹配），或者这个 Skill 解决的问题不是团队的痛点

[示例代码在这个 Gist 中](https://gist.github.com/ThariqS/24defad423d701746e23dc19aace4de5)。

---

## 六、结语分析

> "Skills are incredibly powerful, flexible tools for agents, but it's still early and we're all figuring out how to use them best."

Thariq 用 "it's still early" 和 "we're all figuring out" 保持了谦逊——即使是 Anthropic 自己，也在探索最佳实践。

> "Think of this more as a grab bag of useful tips that we've seen work than a definitive guide. The best way to understand skills is to get started, experiment, and see what works for you."

**"grab bag" 而非 "definitive guide"**——他自己不希望这篇文章被当作权威标准，而是当作一个实用的经验集合。

> "Most of ours began as a few lines and a single gotcha, and got better because people kept adding to them as Claude hit new edge cases."

这是全文最后一个也许是最重要的实践建议：**从简单开始，持续迭代。** Anthropic 内部大多数 Skill 的起点是"几行文字 + 一个 gotcha"，是在使用过程中 Claude 不断踩到新坑、人们不断添加内容后才变好的。

**不要试图一次性写出完美的 Skill。先写一个最小版本，用起来，然后根据 Claude 的实际表现不断改进。**

---

## 七、与 MiniMax Skills 的交叉分析

我们之前分析过 [MiniMax Skills 项目](/ai-research/agent/engineering/minimax-skills-deep-analysis/)（287 文件，7.5 万行代码），这两篇文章形成了很好的互补：

| 维度 | Anthropic（本文） | MiniMax Skills |
|------|-------------------|---------------|
| **性质** | 方法论 + 经验分享 | 开源实现 + 完整代码 |
| **视角** | 自上而下：为什么做、做什么、怎么想 | 自下而上：具体怎么实现 |
| **分类** | 9 种功能类型 | 11 个具体 Skill + 1 个 Plugin |
| **上下文工程** | 渐进式披露、文件夹结构（理念） | references/、scripts/ 目录（实践） |
| **验证** | 强调 Playwright/tmux 端到端测试 | Office 套件有内置 diff 验证逻辑 |
| **记忆** | `${CLAUDE_PLUGIN_DATA}` + JSON/SQLite | 各 Skill 独立的状态管理 |
| **分发** | repo 内或 Plugin Marketplace | 跨平台：Claude Code/Cursor/Codex/OpenCode |
| **Hook** | On Demand Hook（/careful, /freeze） | 未涉及 Hook 机制 |

**结合来看：** Anthropic 文章给出了"为什么"和"什么"——9 种分类让你知道该做什么 Skill，写作建议让你知道怎么写好。MiniMax 项目给出了"怎么做"——具体的文件组织、脚本实现、跨平台兼容。**读完 Anthropic 的方法论，再看 MiniMax 的实现，才是完整的学习路径。**

---

## 八、核心要点回顾

1. **Skill 是文件夹不是文件** — 包含脚本、资产、数据的微型应用，不是一段 system prompt
2. **9 种分类可以当检查清单** — 对照你的团队现有 Skill，看哪些类别是空白
3. **验证 Skill 是 ROI 最高的投资** — Thariq 唯一说"值得花一整周"的类型
4. **Gotchas 是最高价值内容** — 从 Claude 实际犯的错误中持续积累
5. **文件系统 = 上下文工程** — 用渐进式披露管理信息密度
6. **写触发条件不写功能摘要** — description 是给模型判断"该不该用我"的
7. **从几行开始，持续迭代** — 完美是好的敌人
8. **adversarial-review 是可行的** — 多 Agent 自我对抗已在 Anthropic 内部落地
9. **有状态 Skill 不需要复杂基础设施** — 一个 JSON 文件就能实现跨 session 记忆
10. **On Demand Hook 实现动态安全** — /careful 和 /freeze 是务实的权限管理

---

*本文基于 Thariq (@trq212, Anthropic Claude Code 团队) 2026-03-17 发布的 X 长文原文逐段解读。原文 663 万阅读、43,700 次收藏。*
