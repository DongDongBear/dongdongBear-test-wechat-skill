# Topic Selection & Evaluation

> Topic selection is the single biggest determinant of article performance.
> A great article on a bad topic will underperform a mediocre article on a great topic.
> Spend the thinking here — it pays dividends through every subsequent step.

---

## Evaluation Model: 4 Dimensions

### 1. Heat (权重 25%)

How much attention is this topic getting RIGHT NOW?

| Score | Signal |
|-------|--------|
| 9-10 | National-level trending. Weibo/Douyin top 10. Everyone is talking about it. |
| 7-8 | Cross-platform hot topic. Trending on 2+ platforms. |
| 5-6 | Industry hot topic. Your vertical is buzzing about it. |
| 3-4 | Evergreen topic. Consistent search volume, not time-sensitive. |
| 1-2 | Niche. Only a specific sub-community cares. |

**Timing rule:** A trending topic >24 hours old loses 2 points. >72 hours old, don't write it unless you have an exclusive angle.

### 2. Audience Fit (权重 30%)

How well does this match the client's `topics` and `target_audience`?

| Score | Signal |
|-------|--------|
| 9-10 | Bullseye. Core vertical topic that the target audience actively searches for. |
| 7-8 | Adjacent. Extension of the core vertical that the audience would find relevant. |
| 5-6 | Overlapping. There's a connection, but it requires framing to make it relevant. |
| 3-4 | Stretch. Barely relatable. Would feel off-brand. |
| 1-2 | Irrelevant. No meaningful connection. |

### 3. Angle Value (权重 25%)

Can you say something that hasn't been said 100 times already?

| Score | Signal |
|-------|--------|
| 9-10 | Exclusive angle. Access to unique data, experience, or perspective. Matches `content_style`. |
| 7-8 | Differentiated take. Most articles cover surface; you can go deeper or challenge the mainstream view. |
| 5-6 | Standard take with new information. Not unique, but includes fresh data or examples. |
| 3-4 | Saturated. Dozens of similar articles already published. Hard to stand out. |
| 1-2 | Pure repetition. Nothing new to add. |

### 4. Engagement Potential (权重 20%)

Will this topic drive comments, shares, and 在看?

| Score | Signal |
|-------|--------|
| 9-10 | Polarizing. People have strong, opposing opinions. Natural debate fuel. |
| 7-8 | Relatable. Touches a widely-shared experience or emotion. High share potential. |
| 5-6 | Informative. People will learn something, but may not feel compelled to share. |
| 3-4 | Passive. Read-and-forget content. |
| 1-2 | No emotional hook. Pure information with no personal relevance. |

---

## Scoring Formula

```
Final Score = (Heat × 0.25) + (Audience Fit × 0.30) + (Angle Value × 0.25) + (Engagement × 0.20)
```

**Modifiers:**
- Overlaps with `history.yaml` topic_keywords from last 7 days → **-2 points** + flag "近期已覆盖"
- SEO score from `seo_keywords.py` ≥ 7 → **+0.5 points**
- Matches a high-performing framework from `history.yaml` stats → note in recommendation

---

## Output: 10 Topics

Each topic must include:

| Field | Requirement |
|-------|------------|
| Draft title | 20-28 Chinese characters. Must use a specific title strategy (see seo-rules.md). |
| Final score | 0-10, weighted calculation shown |
| Dimension breakdown | Individual scores for Heat / Fit / Angle / Engagement |
| CTR prediction | High / Medium / Low — based on title strength + topic heat |
| SEO score | From `seo_keywords.py` output. If degraded, mark "estimated." |
| Recommended framework | One of the 5 frameworks + one-line reasoning |
| Dedup flag | Comparison result vs. `history.yaml` last 7 days |
| Key angle | 1 sentence: what's the unique perspective for THIS article? |

---

## Topic Generation Strategy

Don't just pick hot topics. Run through these lenses:

### The Content Gap Lens
"What is everyone talking about that nobody is explaining well?"
> If 20 articles exist on a trending topic but they're all surface-level summaries, there's a gap for a deep-dive or contrarian take.

### The Audience Pain Lens
"What problem is my target audience trying to solve THIS WEEK?"
> Cross-reference trending topics with the client's `target_audience`. A general AI topic becomes a topic selection goldmine when framed as "how [specific audience] should respond."

### The Information Asymmetry Lens
"What do I know (or can I find out) that most readers don't?"
> Industry data, personal experience, expert access, behind-the-scenes knowledge. This is the hardest to find but produces the highest-performing articles.

### The Emotional Resonance Lens
"What topic would make the reader forward this to a friend with the message '这说的不就是你吗'?"
> Topics that touch identity, life stage transitions, career anxiety, relationship dynamics. Evergreen but always fresh when specific.

---

## Sorting Rules

1. Sort by final score, descending
2. If tied: higher SEO score wins
3. If still tied: higher Engagement Potential wins (drives algorithm signals)
4. Topics flagged "近期已覆盖" go to the bottom regardless of score

---

## Gotchas

**"The highest-heat trap":** The hottest topic isn't always the best pick. If it's a national trending topic with 1000 articles already published, your Angle Value is probably 2-3. A 7-heat topic with 9-angle often outperforms.

**"The relevance stretch":** If you need more than one sentence to explain why a topic is relevant to the audience, it's probably not relevant enough. Score it honestly.

**"The evergreen excuse":** "This is an evergreen topic" is not a reason to write it TODAY. What's the trigger? What makes NOW the right time? If there's no trigger, save it for a slow news day.

**"Topic selection by committee":** In auto mode, pick the top scorer and move on. Second-guessing the scoring model wastes time and introduces bias.
