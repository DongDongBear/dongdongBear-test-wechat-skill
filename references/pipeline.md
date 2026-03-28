# Pipeline Execution Detail

> Read this file when running the full writing pipeline (Steps 1–8).
> For CLI command syntax, see `cli-reference.md`.

---

## Step 1: Load Client Configuration

Read `{skill_dir}/clients/{client}/style.yaml`.

**Routing:**
- Client directory does not exist → Tell user to reference `references/style-template.md`. Do NOT create it yourself.
- User provided a specific topic (e.g., "write about AI Agents") → Skip Steps 2–3, go to Step 1.5 → Step 3.5
- User provided raw Markdown for formatting only → Skip to Step 7

## Step 1.5: YouMind Knowledge Mining

> Only runs when `config.yaml` contains `youmind.api_key`. Otherwise skip.

Use `youmind-api.js mine-topics` with the client's topics and source boards. Keep the top 10 results as `knowledge_context` for use in Steps 3 and 4.

Topics that match knowledge base material receive a +1 scoring boost (flag: "has knowledge base support").

**[Fallback]:** API error → skip, set `knowledge_context` to empty.

## Step 2: Trending Topic Fetch

Run `fetch_hotspots.py`. Tag each result with its domain and a creatability score (1–10). Filter out items unrelated to the client's topics.

**[Fallback]:** Script error → YouMind `web-search` → `WebSearch` → ask user for a topic.

## Step 2.5: Dedup + SEO (Parallel)

Run two tasks simultaneously:

1. Read `history.yaml` — extract `topic_keywords` from the last 7 days for dedup. Note characteristics of top-performing articles if stats exist.
2. Run `seo_keywords.py` on 3–5 keywords extracted from trending titles.

**[Fallback]:** SEO script error → self-estimate scores, mark as "estimated."

## Step 3: Topic Generation

Read `references/topic-selection.md`. Generate **10 topics** using the 4-dimension evaluation model.

- Knowledge boost: matching `knowledge_context` items → +1, flag "has knowledge base support"
- Dedup penalty: overlapping with last 7 days → −2, flag "recently covered"
- **Auto mode:** Select the highest scorer and continue.
- **Interactive mode:** Output all 10 in a formatted table and wait for selection.

## Step 3.5: Framework Selection

Read `references/frameworks.md`. Generate **5 framework proposals** (Pain-Point / Story / Listicle / Comparison / Hot Take), each with: opening strategy, H2 outline, golden quote placement, closing approach, and recommendation score.

If history stats show a particular framework overperforms for this audience, bias toward it.

- **Auto mode:** Select the highest-rated proposal and continue.
- **Interactive mode:** Present all 5 and wait for selection.

## Step 4: Article Writing

Read `references/writing-guide.md` and `clients/{client}/playbook.md` (if it exists).

**Before writing, complete the Pre-Writing Thinking Framework** (in `<thinking>` tags — see writing-guide.md for the full process).

**Knowledge integration:** If `knowledge_context` contains relevant items, use `youmind-api.js get-material` / `get-craft` to read the full content. Extract facts, data points, and unique perspectives. Attribute naturally within the article. Do NOT copy-paste.

**Hard rules:** Follow the selected framework structure. Apply writing-guide craft principles throughout. H1 title 20–28 characters. Word count 1,500–2,500. No banned words from writing-guide or client blacklist. Place golden quotes at framework-specified positions. Match client voice and tone. Do NOT insert image placeholders (Step 6 handles images).

**Self-check (two passes, in this order):**
1. **Depth Checklist** (writing-guide.md "Depth Architecture" section): Does the article contain at least one genuinely surprising insight? Does it pass the "So What?" ladder to Level 3? Would it still be worth reading if you stripped all the formatting? If not — rewrite the weak sections before polishing.
2. **Voice Verification** (writing-guide.md Level 4): De-AI check, rhythm, specificity, structural variation.

Save to: `{skill_dir}/output/{client}/{YYYY-MM-DD}-{slug}.md`

## Step 5: SEO Optimization + De-AI Pass

Read `references/seo-rules.md`. Execute ALL 6 optimizations:

1. **Title optimization:** Generate 3 alternatives using different strategies. Select the best.
2. **Keyword density:** Core keyword in the first 200 characters, 3–5 natural occurrences total.
3. **De-AI deep pass:** Full 4-level protocol. Scan every paragraph. Replace every banned word, break every parallel structure, inject cognitive imperfection.
4. **Digest:** ≤54 characters with core keyword + curiosity hook. Must NOT repeat the title.
5. **Tags:** 5 tags (2 industry + 2 trending + 1 long-tail). Specific beats broad.
6. **Completion rate check:** Verify paragraph lengths, hook intervals, and rhythm variation. Fix flat sections.

Overwrite the file with the optimized version.

## Step 6: Visual AI

Read `references/visual-prompts.md`.

### 6a. Ask user about image needs

After writing, ask the user whether they want: cover + inline images (recommended for full visual experience), cover only (quick publish), inline only (already have a cover), or no images (text-only publish). Also ask about style preferences if they have any.

### 6b. Design prompts

**Cover:** Design 3 creative directions (per visual-prompts.md Creative A/B/C). Each includes a concept description, a full English prompt (must include `no text, no letters, no words`), and a matching color scheme.

**Inline images:** Analyze the article paragraph-by-paragraph. Image-worthy paragraphs: data/evidence, scene/narrative, turning points. Skip: pure opinion, opening hooks, CTA/closing. Maintain ≥300 characters spacing between images, 3–6 images total.

**Prompt source priority:** User-specified style > Nano Banana Pro library (via `nano-banana-pro-prompts-recommend-skill` if available) > visual-prompts.md patterns > self-designed.

- **Interactive mode:** Show all plans and wait for selection.
- **Auto mode:** Select Creative A and generate all images.

### 6c. Generate images

Use `image-gen.js` for cover and inline images.

**Three-level fallback:** API generation succeeds → match predefined covers from `cover/` directory by color → output full prompts for manual generation and continue pipeline in text-only mode.

Insert generated image paths into the Markdown file.

## Step 7: Format + Publish

**Always publish directly to WeChat drafts. Do NOT ask the user whether to publish — this step is mandatory and automatic.**

Use `cli.js publish` with theme and color from style.yaml (or user override). For custom themes, use `--custom-theme`. Include `--cover` only if a cover image exists.

**[Fallback]:** Publish fails → generate a local HTML preview with `cli.js preview` and tell user the file path.

## Step 7.5: History + Archive

**History:** Append to `clients/{client}/history.yaml` with: date, title, topic_source, keywords, knowledge_refs, framework, word_count, media_id, theme, stats: null.

**YouMind Archive:** If `youmind.save_board` is configured, use `youmind-api.js save-article` to save the article back to the knowledge base.

**[Fallback]:** Either operation fails → warn the user, do not block the pipeline.

## Step 8: Final Output

Report the results: title (with 2 alternatives and their strategies), digest, tags, theme + color, media_id, and remind the user to check the draft box to publish. On partial success, list each step's status and explain what needs manual completion.
