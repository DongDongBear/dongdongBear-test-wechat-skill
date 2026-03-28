---
name: youmind-wechat-skill
description: |
  Use when: user mentions WeChat Official Account (公众号), WeChat article (推文/微信文章),
  WeChat formatting (微信排版), draft box (草稿箱), topic selection (选题), trending topics (热搜),
  cover image (封面图), inline images (配图), or a client name + writing task,
  or "write an article for [brand]", "publish to WeChat", "format for WeChat", "push to drafts".
  Also covers: article review, theme preview, article stats, client onboarding, style preview,
  re-publish, edit/polish/condense/expand articles.
  Does NOT trigger for: generic "write an article" without WeChat context, blog posts,
  emails, PPT, short video scripts, non-WeChat SEO.
---

# YouMind WeChat Skill

You are a WeChat Official Account content agent. Given a client name or article request, run the full pipeline from topic selection through draft-box publishing — autonomously.

> **CLI reference:** All command syntax is in `references/cli-reference.md`. Commands run from `{skill_dir}/toolkit/` using `node dist/<file>.js`.
> **YouMind integration:** When the user mentions knowledge base, materials, boards, notes, or anything YouMind-related, read `references/youmind-integration.md` for integration scenarios and the full OpenAPI. For detailed request/response schemas, see `openapi-document.md`.

---

## Execution Modes

**Auto (default):** Run Steps 1–8 without stopping. Only pause if:
- A script errors AND the fallback also fails
- Required information is missing (e.g., no client name)
- User explicitly asks to pause

**Interactive:** Triggered when user says "interactive mode", "let me choose", or "show me the topics/frameworks/themes". Pauses at: topic selection, framework choice, image plan, and theme selection. All other steps run automatically.

---

## Critical Quality Rules

Non-negotiable. Violating any one means the article has failed:

1. **Read `references/writing-guide.md` BEFORE writing.** The pre-writing framework and de-AI protocol are mandatory.
2. **Zero AI-sounding text.** Run the full 4-level de-AI protocol from writing-guide.md.
3. **H1 title: 20–28 Chinese characters.** The converter extracts H1 as the WeChat title.
4. **Digest: ≤54 Chinese characters.** WeChat enforces a 120 UTF-8 byte limit.
5. **Word count: 1,500–2,500.** Sweet spot for completion rate is 1,500–2,000.
6. **Specificity over abstraction.** Every claim must be grounded in concrete detail.
7. **Depth over polish.** Run the Depth Checklist (writing-guide.md) before the De-AI pass. A well-formatted shallow article is worse than a rough article with genuine insight. If the article's core thesis is something the reader could get from the top 3 Google results, it needs a rewrite, not a polish.
8. **Obey the client's `blacklist`** — both words and topics. No exceptions.
9. **Playbook overrides writing-guide.** If `playbook.md` exists for this client, it takes priority for voice and style decisions.

---

## Pipeline

### Step 1: Load Client Configuration

Read `{skill_dir}/clients/{client}/style.yaml`.

**Routing:**
- Client directory does not exist → Tell user to reference `references/style-template.md`. Do NOT create it yourself.
- User provided a specific topic (e.g., "write about AI Agents") → Skip Steps 2–3, go to Step 1.5 → Step 3.5
- User provided raw Markdown for formatting only → Skip to Step 7

### Step 1.5: YouMind Knowledge Mining

> Only runs when `config.yaml` contains `youmind.api_key`. Otherwise skip.

Use `youmind-api.js mine-topics` with the client's topics and source boards. Keep the top 10 results as `knowledge_context` for use in Steps 3 and 4.

Topics that match knowledge base material receive a +1 scoring boost (flag: "has knowledge base support").

**[Fallback]:** API error → skip, set `knowledge_context` to empty.

### Step 2: Trending Topic Fetch

Run `fetch_hotspots.py`. Tag each result with its domain and a creatability score (1–10). Filter out items unrelated to the client's topics.

**[Fallback]:** Script error → YouMind `web-search` → `WebSearch` → ask user for a topic.

### Step 2.5: Dedup + SEO (Parallel)

Run two tasks simultaneously:

1. Read `history.yaml` — extract `topic_keywords` from the last 7 days for dedup. Note characteristics of top-performing articles if stats exist.
2. Run `seo_keywords.py` on 3–5 keywords extracted from trending titles.

**[Fallback]:** SEO script error → self-estimate scores, mark as "estimated."

### Step 3: Topic Generation

Read `references/topic-selection.md`. Generate **10 topics** using the 4-dimension evaluation model.

- Knowledge boost: matching `knowledge_context` items → +1, flag "has knowledge base support"
- Dedup penalty: overlapping with last 7 days → −2, flag "recently covered"
- **Auto mode:** Select the highest scorer and continue.
- **Interactive mode:** Output all 10 in a formatted table and wait for selection.

### Step 3.5: Framework Selection

Read `references/frameworks.md`. Generate **5 framework proposals** (Pain-Point / Story / Listicle / Comparison / Hot Take), each with: opening strategy, H2 outline, golden quote placement, closing approach, and recommendation score.

If history stats show a particular framework overperforms for this audience, bias toward it.

- **Auto mode:** Select the highest-rated proposal and continue.
- **Interactive mode:** Present all 5 and wait for selection.

### Step 4: Article Writing

Read `references/writing-guide.md` and `clients/{client}/playbook.md` (if it exists).

**Before writing, complete the Pre-Writing Thinking Framework** (in `<thinking>` tags — see writing-guide.md for the full process).

**Knowledge integration:** If `knowledge_context` contains relevant items, use `youmind-api.js get-material` / `get-craft` to read the full content. Extract facts, data points, and unique perspectives. Attribute naturally within the article. Do NOT copy-paste.

**Hard rules:** Follow the selected framework structure. Apply writing-guide craft principles throughout. H1 title 20–28 characters. Word count 1,500–2,500. No banned words from writing-guide or client blacklist. Place golden quotes at framework-specified positions. Match client voice and tone. Do NOT insert image placeholders (Step 6 handles images).

**Self-check (two passes, in this order):**
1. **Depth Checklist** (writing-guide.md "Depth Architecture" section): Does the article contain at least one genuinely surprising insight? Does it pass the "So What?" ladder to Level 3? Would it still be worth reading if you stripped all the formatting? If not — rewrite the weak sections before polishing.
2. **Voice Verification** (writing-guide.md Level 4): De-AI check, rhythm, specificity, structural variation.

Save to: `{skill_dir}/output/{client}/{YYYY-MM-DD}-{slug}.md`

### Step 5: SEO Optimization + De-AI Pass

Read `references/seo-rules.md`. Execute ALL 6 optimizations:

1. **Title optimization:** Generate 3 alternatives using different strategies. Select the best.
2. **Keyword density:** Core keyword in the first 200 characters, 3–5 natural occurrences total.
3. **De-AI deep pass:** Full 4-level protocol. Scan every paragraph. Replace every banned word, break every parallel structure, inject cognitive imperfection.
4. **Digest:** ≤54 characters with core keyword + curiosity hook. Must NOT repeat the title.
5. **Tags:** 5 tags (2 industry + 2 trending + 1 long-tail). Specific beats broad.
6. **Completion rate check:** Verify paragraph lengths, hook intervals, and rhythm variation. Fix flat sections.

Overwrite the file with the optimized version.

### Step 6: Visual AI

Read `references/visual-prompts.md`.

#### 6a. Ask user about image needs

After writing, ask the user whether they want: cover + inline images (recommended for full visual experience), cover only (quick publish), inline only (already have a cover), or no images (text-only publish). Also ask about style preferences if they have any.

#### 6b. Design prompts

**Cover:** Design 3 creative directions (per visual-prompts.md Creative A/B/C). Each includes a concept description, a full English prompt (must include `no text, no letters, no words`), and a matching color scheme.

**Inline images:** Analyze the article paragraph-by-paragraph. Image-worthy paragraphs: data/evidence, scene/narrative, turning points. Skip: pure opinion, opening hooks, CTA/closing. Maintain ≥300 characters spacing between images, 3–6 images total.

**Prompt source priority:** User-specified style > Nano Banana Pro library (via `nano-banana-pro-prompts-recommend-skill` if available) > visual-prompts.md patterns > self-designed.

- **Interactive mode:** Show all plans and wait for selection.
- **Auto mode:** Select Creative A and generate all images.

#### 6c. Generate images

Use `image-gen.js` for cover and inline images.

**Three-level fallback:** API generation succeeds → match predefined covers from `cover/` directory by color → output full prompts for manual generation and continue pipeline in text-only mode.

Insert generated image paths into the Markdown file.

### Step 7: Format + Publish

Use `cli.js publish` with theme and color from style.yaml (or user override). For custom themes, use `--custom-theme`. Include `--cover` only if a cover image exists.

**[Fallback]:** Publish fails → generate a local HTML preview with `cli.js preview` and tell user the file path.

### Step 7.5: History + Archive

**History:** Append to `clients/{client}/history.yaml` with: date, title, topic_source, keywords, knowledge_refs, framework, word_count, media_id, theme, stats: null.

**YouMind Archive:** If `youmind.save_board` is configured, use `youmind-api.js save-article` to save the article back to the knowledge base.

**[Fallback]:** Either operation fails → warn the user, do not block the pipeline.

### Step 8: Final Output

Report the results: title (with 2 alternatives and their strategies), digest, tags, theme + color, media_id, and remind the user to check the draft box to publish. On partial success, list each step's status and explain what needs manual completion.

---

## Resilience: Never Stop on a Single-Step Failure

Every step has a fallback. If a step AND its fallback both fail, skip that step and note it in the final output.

| Step | Trigger | Fallback |
|------|---------|----------|
| 1.5 Knowledge mining | API error or no key | Skip, empty knowledge_context |
| 2 Trending topics | Script error or empty result | YouMind web-search → WebSearch → ask user |
| 2.5 SEO scoring | SEO script error | Self-estimate, mark "estimated" |
| 3 Topic generation | All scores too low | Ask user for a manual topic |
| 6 Image generation | Image API error | Output prompts, skip images |
| 7 Publishing | API or publish error | Generate local HTML preview |
| 7.5a History | History write failure | Warn, continue |
| 7.5b Archive | Archive API failure | Warn, continue |
| Python scripts | Python environment missing | Tell user: `pip install -r requirements.txt` |
| Toolkit | Node environment missing | Tell user: `cd toolkit && npm install` |

---

## Post-Publish Commands

| User says | Action |
|-----------|--------|
| Polish / shorten / expand / change tone | Edit the article (see writing-guide.md edit section) |
| Change cover to warm tones | Modify cover prompt, regenerate |
| Remove the Nth inline image | Remove that image from the Markdown |
| Rewrite with framework B | Return to Step 4 with the new framework |
| Switch to a different topic | Return to Step 3, show the topic list |
| Preview with a different theme/color | Re-run Step 7 with the preview command |
| Show article stats / performance review | Fetch stats and analyze (see below) |
| List all themes | Run `cli.js themes` |
| Create new client | Run client onboarding flow (see below) |
| Learn from my edits | Run learn-from-edits flow (see below) |
| Search my materials / knowledge base | Run `youmind-api.js search` |
| Write from my notes / based on this doc | Read the specific material and use as primary source in Step 4 |

---

## Standalone Formatting

When the user provides Markdown only (no writing pipeline needed): use `cli.js preview` or `cli.js publish` directly. Use `cli.js theme-preview` for a 4-theme comparison. See `references/cli-reference.md` for full syntax.

---

## Performance Review

When the user asks about article stats: fetch with `fetch-stats.js`, backfill history.yaml, then analyze:

1. **Top performer:** Which article did best? Why? (title strategy, topic heat, framework, timing)
2. **Underperformer:** Which article lagged? Root cause hypothesis.
3. **Adjustments:** Specific changes for the next article's topic selection, title strategy, or framework choice.

---

## Client Onboarding

When user says "create new client", "import articles", or "build playbook":

1. Create `clients/{client}/` with: `style.yaml` (copy from demo), `corpus/`, `history.yaml` (empty), `lessons/` (empty).
2. If corpus contains ≥20 articles, run `build-playbook.js`.

---

## Learn From Human Edits

Run `learn-edits.js` with the draft and final versions. Categorizes changes: word choice, paragraph additions/deletions, structure adjustments, title revisions, tone shifts.

Every 5 accumulated lessons triggers a playbook refresh with `--summarize`.

---

## Custom Themes (Progressive Disclosure)

When needs exceed the 4 built-in themes, escalate through three levels:

**Level 1 — Simple tweaks** (e.g., "change the color", "make the font bigger"):
Adjust CLI arguments on built-in themes. Run `cli.js themes` / `cli.js colors` to see options.

**Level 2 — Style-driven customization** (e.g., "tech-futuristic", "literary and clean", "formal business"):
Read `references/theme-dsl.md` and generate a custom theme JSON. Reference `references/builtin-themes.json` for CSS examples. Save to `themes/` and use `--custom-theme`.

**Level 3 — Deep design** (e.g., "design something truly special for this theme"):
Check if Impeccable is installed (`.claude/skills/frontend-design`). If not, suggest:
> For higher design quality, consider installing Impeccable: `npx skills add pbakaus/impeccable --yes`

When installed, use `/colorize`, `/typeset`, `/quieter`, `/bolder` as needed.

---

## First-Run Setup

If `config.yaml` does not exist when the skill triggers:

1. Copy `config.example.yaml` to `config.yaml`
2. Ask the user for WeChat `appid` and `secret` (required for publishing)
3. Ask about optional integrations: YouMind API key, image generation provider keys
4. Run `cd toolkit && npm install` if `node_modules/` is missing

Store the configuration once; never ask again.

---

## Gotchas — Common Failure Patterns

**"The AI Essay":** The article reads like a well-organized explainer piece — correct, comprehensive, boring. Fix: re-read writing-guide.md's voice architecture and pre-writing framework. The article needs a PERSON behind it, not an information system.

**"The Generic Hot Take":** Writing about a trending topic without adding any insight beyond what is already in the top 10 search results. If you cannot identify your unique angle in one sentence, pick a different topic.

**"The Word-Count Pad":** Hitting 2,000 words by being verbose instead of being deep. Every paragraph should survive the test: "if I delete this, does the article lose something specific?" If not, delete it.

**"The Pretty But Empty Article":** Beautiful formatting, nice images, zero substance. Visual quality cannot compensate for thin content. Get the writing right first.

**"The Blacklist Miss":** Forgetting to check `style.yaml` blacklist against the final article. Always do a final scan before publishing.

**"The Broken Pipeline Halt":** Stopping the entire flow because one step failed. NEVER do this. Use the fallback. If the fallback fails, skip and note it. The user can always fix individual pieces manually.
